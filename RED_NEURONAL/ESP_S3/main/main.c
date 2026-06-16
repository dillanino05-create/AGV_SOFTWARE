/*
 * Firmware del carro (ESP32-S3).
 *
 * Que hace:
 *   1) Conecta la ESP32 a una red WiFi (modo estacion / STA).
 *   2) Una vez conectada, levanta un servidor HTTP que permite controlar
 *      por red dos motores (izquierdo y derecho) a traves de un driver
 *      tipo puente H (TB6612) y una "plataforma" (un actuador extra).
 *
 * Como se controla:
 *   Desde un navegador o cualquier cliente HTTP, en la misma red WiFi:
 *     GET /            -> pagina con botones (Adelante/Atras/Izq/Der/Stop/Plataforma)
 *     GET /move?l=N&r=M -> fija velocidad del motor izquierdo (l) y derecho (r)
 *                          N y M van de -255 (reversa maxima) a 255 (adelante maximo)
 *     GET /stop        -> detiene ambos motores
 *     GET /platform?on=1|0 -> activa/desactiva la plataforma
 */

#include <string.h>
#include <stdlib.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "driver/gpio.h"
#include "driver/ledc.h"
#include "esp_http_server.h"

/* Credenciales de la red WiFi a la que se conecta la ESP32 (hotspot del celular). */
#define WIFI_SSID  "OPPOA805G"
#define WIFI_PASS  "12345678"

/* Pines GPIO usados, segun el esquematico del driver de motores (tipo TB6612).
 * Cada motor usa 2 pines de direccion (IN1/IN2) + 1 pin de PWM para la velocidad.
 * STANDBY debe estar en alto para que el driver este habilitado (si esta en bajo,
 * el chip entra en modo de bajo consumo y no mueve nada). */
#define PIN_IN1_PLATAFORMA  GPIO_NUM_3    /* Activa/desactiva el actuador de la plataforma */
#define PIN_STANDBY         GPIO_NUM_46   /* Habilita el driver de motores (1 = activo) */
#define PIN_PWM_IZQ         GPIO_NUM_9    /* PWM (velocidad) del motor izquierdo */
#define PIN_IN2_IZQ         GPIO_NUM_10   /* Direccion del motor izquierdo (IN2) */
#define PIN_IN1_IZQ         GPIO_NUM_11   /* Direccion del motor izquierdo (IN1) */
#define PIN_PWM_DER         GPIO_NUM_12   /* PWM (velocidad) del motor derecho */
#define PIN_IN2_DER         GPIO_NUM_13   /* Direccion del motor derecho (IN2) */
#define PIN_IN1_DER         GPIO_NUM_14   /* Direccion del motor derecho (IN1) */

/* Canales del periferico LEDC (PWM por hardware) usados para la velocidad de cada motor. */
#define LEDC_CH_IZQ  LEDC_CHANNEL_0
#define LEDC_CH_DER  LEDC_CHANNEL_1

static const char *TAG = "car";

/* Grupo de eventos usado para avisar, desde los callbacks de WiFi, si la
 * conexion tuvo exito (CONNECTED) o se agotaron los reintentos (FAILED). */
static EventGroupHandle_t wifi_events;
#define CONNECTED BIT0
#define FAILED    BIT1
static int retries = 0;  /* cuenta los intentos de reconexion fallidos */

/* ============================================================
 *  MOTORES
 *  Logica de control del puente H: para cada lado (izquierdo/derecho)
 *  hay 2 pines de direccion + 1 canal PWM de velocidad.
 *    IN1=1, IN2=0  -> gira hacia adelante
 *    IN1=0, IN2=1  -> gira en reversa
 *    IN1=0, IN2=0  -> rueda libre / freno (sin PWM)
 * ============================================================ */

/* Configura todos los pines GPIO de motores/plataforma como salida,
 * configura el periferico PWM (LEDC) y deja el driver listo para usarse. */
static void motores_init(void)
{
    gpio_config_t io = {
        .pin_bit_mask = (1ULL << PIN_IN1_PLATAFORMA) | (1ULL << PIN_STANDBY) |
                        (1ULL << PIN_IN1_IZQ) | (1ULL << PIN_IN2_IZQ) |
                        (1ULL << PIN_IN1_DER) | (1ULL << PIN_IN2_DER),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    gpio_config(&io);

    /* Un solo timer LEDC (5kHz, resolucion de 8 bits = duty 0-255) compartido
     * por los dos canales de PWM (izquierdo y derecho). */
    ledc_timer_config_t timer = {
        .speed_mode      = LEDC_LOW_SPEED_MODE,
        .duty_resolution = LEDC_TIMER_8_BIT,
        .timer_num       = LEDC_TIMER_0,
        .freq_hz         = 5000,
        .clk_cfg         = LEDC_AUTO_CLK,
    };
    ledc_timer_config(&timer);

    /* Canal PWM del motor izquierdo, arranca en duty=0 (detenido). */
    ledc_channel_config_t ch_izq = {
        .gpio_num   = PIN_PWM_IZQ,
        .speed_mode = LEDC_LOW_SPEED_MODE,
        .channel    = LEDC_CH_IZQ,
        .timer_sel  = LEDC_TIMER_0,
        .duty       = 0,
        .hpoint     = 0,
    };
    ledc_channel_config(&ch_izq);

    /* Canal PWM del motor derecho, arranca en duty=0 (detenido). */
    ledc_channel_config_t ch_der = {
        .gpio_num   = PIN_PWM_DER,
        .speed_mode = LEDC_LOW_SPEED_MODE,
        .channel    = LEDC_CH_DER,
        .timer_sel  = LEDC_TIMER_0,
        .duty       = 0,
        .hpoint     = 0,
    };
    ledc_channel_config(&ch_der);

    gpio_set_level(PIN_STANDBY, 1);          /* Sacar el driver de standby */
    gpio_set_level(PIN_IN1_PLATAFORMA, 0);   /* Plataforma apagada al iniciar */
}

/* Limita un valor de velocidad al rango valido [-255, 255]. */
static int clamp255(int v)
{
    if (v > 255) return 255;
    if (v < -255) return -255;
    return v;
}

/* Mueve un solo lado (izquierdo o derecho) a la velocidad indicada.
 * velocidad > 0 -> adelante, < 0 -> reversa, 0 -> detenido.
 * in1_pin/in2_pin son los pines de direccion de ESE lado, y "canal" es
 * el canal LEDC que controla su PWM. */
static void set_lado(int in1_pin, int in2_pin, ledc_channel_t canal, int velocidad)
{
    velocidad = clamp255(velocidad);
    if (velocidad > 0) {
        gpio_set_level(in1_pin, 1);
        gpio_set_level(in2_pin, 0);
    } else if (velocidad < 0) {
        gpio_set_level(in1_pin, 0);
        gpio_set_level(in2_pin, 1);
    } else {
        gpio_set_level(in1_pin, 0);
        gpio_set_level(in2_pin, 0);
    }
    /* El PWM siempre usa la magnitud (valor absoluto); el signo ya se
     * tradujo arriba en la combinacion de IN1/IN2. */
    ledc_set_duty(LEDC_LOW_SPEED_MODE, canal, abs(velocidad));
    ledc_update_duty(LEDC_LOW_SPEED_MODE, canal);
}

/* Punto de entrada unico para mover el carro: fija la velocidad de
 * ambos motores en la misma llamada. */
static void set_motores(int izquierdo, int derecho)
{
    set_lado(PIN_IN1_IZQ, PIN_IN2_IZQ, LEDC_CH_IZQ, izquierdo);
    set_lado(PIN_IN1_DER, PIN_IN2_DER, LEDC_CH_DER, derecho);
    ESP_LOGI(TAG, "Motores -> izquierdo=%d derecho=%d", izquierdo, derecho);
}

/* ============================================================
 *  SERVIDOR HTTP
 *  Expone los endpoints que permiten controlar el carro desde
 *  cualquier dispositivo conectado a la misma red WiFi.
 * ============================================================ */

/* Helper: lee un parametro entero de la query string de la URL
 * (ej. "?l=200&r=-100" -> query_int(req,"l",0) devuelve 200).
 * Si el parametro no existe, devuelve valor_defecto. */
static int query_int(httpd_req_t *req, const char *clave, int valor_defecto)
{
    char buf[128];
    char val[16];
    if (httpd_req_get_url_query_str(req, buf, sizeof(buf)) != ESP_OK) {
        return valor_defecto;
    }
    if (httpd_query_key_value(buf, clave, val, sizeof(val)) != ESP_OK) {
        return valor_defecto;
    }
    return atoi(val);
}

/* GET /move?l=<velocidad_izq>&r=<velocidad_der> */
static esp_err_t move_handler(httpd_req_t *req)
{
    int izq = query_int(req, "l", 0);
    int der = query_int(req, "r", 0);
    set_motores(izq, der);
    httpd_resp_set_type(req, "text/plain");
    httpd_resp_sendstr(req, "OK");
    return ESP_OK;
}

/* GET /stop -> detiene ambos motores */
static esp_err_t stop_handler(httpd_req_t *req)
{
    set_motores(0, 0);
    httpd_resp_set_type(req, "text/plain");
    httpd_resp_sendstr(req, "OK");
    return ESP_OK;
}

/* GET /platform?on=1|0 -> activa/desactiva el actuador de la plataforma */
static esp_err_t platform_handler(httpd_req_t *req)
{
    int on = query_int(req, "on", 0);
    gpio_set_level(PIN_IN1_PLATAFORMA, on ? 1 : 0);
    httpd_resp_set_type(req, "text/plain");
    httpd_resp_sendstr(req, "OK");
    return ESP_OK;
}

/* GET / -> pagina HTML simple con botones que llaman a los endpoints
 * anteriores via fetch() desde el navegador. */
static esp_err_t root_handler(httpd_req_t *req)
{
    static const char *html =
        "<html><body style='font-family:sans-serif;text-align:center'>"
        "<h2>Control del carro</h2>"
        "<p>"
        "<button onclick=\"fetch('/move?l=200&r=200')\">Adelante</button> "
        "<button onclick=\"fetch('/move?l=-200&r=-200')\">Atras</button>"
        "</p><p>"
        "<button onclick=\"fetch('/move?l=-150&r=150')\">Izquierda</button> "
        "<button onclick=\"fetch('/move?l=150&r=-150')\">Derecha</button>"
        "</p><p>"
        "<button onclick=\"fetch('/stop')\">Stop</button>"
        "</p><p>"
        "<button onclick=\"fetch('/platform?on=1')\">Plataforma ON</button> "
        "<button onclick=\"fetch('/platform?on=0')\">Plataforma OFF</button>"
        "</p></body></html>";
    httpd_resp_set_type(req, "text/html");
    httpd_resp_sendstr(req, html);
    return ESP_OK;
}

/* Arranca el servidor HTTP y registra las 4 rutas anteriores. Se llama
 * una sola vez, despues de que el WiFi ya esta conectado. */
static void servidor_iniciar(void)
{
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    httpd_handle_t server = NULL;
    if (httpd_start(&server, &config) != ESP_OK) {
        ESP_LOGE(TAG, "No se pudo iniciar el servidor HTTP");
        return;
    }

    httpd_uri_t root_uri     = { .uri = "/",         .method = HTTP_GET, .handler = root_handler };
    httpd_uri_t move_uri     = { .uri = "/move",     .method = HTTP_GET, .handler = move_handler };
    httpd_uri_t stop_uri     = { .uri = "/stop",     .method = HTTP_GET, .handler = stop_handler };
    httpd_uri_t platform_uri = { .uri = "/platform", .method = HTTP_GET, .handler = platform_handler };

    httpd_register_uri_handler(server, &root_uri);
    httpd_register_uri_handler(server, &move_uri);
    httpd_register_uri_handler(server, &stop_uri);
    httpd_register_uri_handler(server, &platform_uri);

    ESP_LOGI(TAG, "Servidor HTTP listo");
}

/* ============================================================
 *  WIFI
 *  Maneja los eventos del stack WiFi: inicia la conexion, reintenta
 *  si se cae, y avisa (via wifi_events) cuando ya hay IP asignada
 *  o cuando se agotaron los intentos.
 * ============================================================ */

static void handler(void *arg, esp_event_base_t base, int32_t id, void *data)
{
    if (base == WIFI_EVENT && id == WIFI_EVENT_STA_START) {
        /* El driver WiFi ya arranco: intentar conectar por primera vez. */
        esp_wifi_connect();

    } else if (base == WIFI_EVENT && id == WIFI_EVENT_STA_DISCONNECTED) {
        /* Se perdio la conexion (o nunca se logro). "reason" indica el motivo
         * segun los codigos de la norma 802.11 (ej. 201=AP no encontrado,
         * 2=AUTH_EXPIRE, 204=timeout del handshake WPA2, etc). Reintenta
         * hasta 5 veces antes de darse por vencido. */
        wifi_event_sta_disconnected_t *e = data;
        ESP_LOGW(TAG, "Desconectado, reason=%d", e->reason);
        if (retries++ < 5) {
            esp_wifi_connect();
        } else {
            xEventGroupSetBits(wifi_events, FAILED);
        }

    } else if (base == IP_EVENT && id == IP_EVENT_STA_GOT_IP) {
        /* Conexion exitosa: el router/hotspot ya nos asigno una IP. */
        ip_event_got_ip_t *e = data;
        ESP_LOGI(TAG, "============================================");
        ESP_LOGI(TAG, "  CONECTADO a: %s", WIFI_SSID);
        ESP_LOGI(TAG, "  IP: " IPSTR, IP2STR(&e->ip_info.ip));
        ESP_LOGI(TAG, "============================================");
        xEventGroupSetBits(wifi_events, CONNECTED);
    }
}

/* ============================================================
 *  PUNTO DE ENTRADA
 * ============================================================ */
void app_main(void)
{
    /* Inicializa el almacenamiento no volatil (NVS), donde el stack WiFi
     * guarda datos de calibracion de radio. Si esta corrupto u obsoleto,
     * se borra y se reintenta una vez. */
    esp_err_t r = nvs_flash_init();
    if (r == ESP_ERR_NVS_NO_FREE_PAGES || r == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        nvs_flash_erase();
        nvs_flash_init();
    }

    motores_init();

    /* Stack de red (lwIP) y loop de eventos por donde llegan los
     * eventos de WiFi/IP que maneja la funcion handler(). */
    esp_netif_init();
    esp_event_loop_create_default();
    esp_netif_create_default_wifi_sta();

    /* Inicializa el driver WiFi con la configuracion por defecto. */
    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    esp_wifi_init(&cfg);

    /* Crea el grupo de eventos propio y registra el handler para
     * todos los eventos de WIFI_EVENT y para "ya tengo IP" de IP_EVENT. */
    wifi_events = xEventGroupCreate();
    esp_event_handler_register(WIFI_EVENT, ESP_EVENT_ANY_ID, handler, NULL);
    esp_event_handler_register(IP_EVENT,   IP_EVENT_STA_GOT_IP, handler, NULL);

    /* Configura el SSID/password y fuerza WPA2 (threshold.authmode), con
     * PMF opcional (capable=true pero no obligatorio: required=false)
     * para ser compatible con hotspots de celular que no lo exigen. */
    wifi_config_t wc = {
        .sta = {
            .ssid     = WIFI_SSID,
            .password = WIFI_PASS,
            .threshold.authmode = WIFI_AUTH_WPA2_PSK,
            .pmf_cfg  = { .capable = true, .required = false },
        },
    };
    esp_wifi_set_mode(WIFI_MODE_STA);
    esp_wifi_set_config(WIFI_IF_STA, &wc);
    esp_wifi_start();
    esp_wifi_set_max_tx_power(84);   /* Maxima potencia de transmision permitida */
    esp_wifi_set_ps(WIFI_PS_NONE);   /* Desactiva el ahorro de energia (mejora estabilidad) */

    /* Escaneo de diagnostico: lista las redes que la ESP32 detecta antes de
     * intentar conectarse. Util para confirmar que el SSID configurado esta
     * realmente visible (senal, banda 2.4GHz, etc) cuando hay problemas de
     * conexion. No es necesario para el funcionamiento normal. */
    ESP_LOGI(TAG, "Escaneando redes cercanas...");
    uint16_t num_aps = 20;
    static wifi_ap_record_t aps[20];  /* static: evita usar 20 registros en el stack */
    esp_wifi_scan_start(NULL, true);
    esp_wifi_scan_get_ap_records(&num_aps, aps);
    ESP_LOGI(TAG, "Redes encontradas: %d", num_aps);
    for (int i = 0; i < num_aps; i++) {
        ESP_LOGI(TAG, "  SSID='%s' RSSI=%d canal=%d auth=%d",
                 (char *)aps[i].ssid, aps[i].rssi, aps[i].primary, aps[i].authmode);
    }

    ESP_LOGI(TAG, "Conectando a '%s'...", WIFI_SSID);

    /* Bloquea aqui hasta que el handler() avise CONNECTED o FAILED. */
    EventBits_t bits = xEventGroupWaitBits(wifi_events,
                                           CONNECTED | FAILED,
                                           pdFALSE, pdFALSE,
                                           portMAX_DELAY);
    if (bits & CONNECTED) {
        ESP_LOGI(TAG, "WiFi OK. Iniciando servidor de control...");
        servidor_iniciar();
        /* Bucle principal: solo reporta la calidad de señal (RSSI) cada
         * 5s. El control real del carro ocurre en los handlers HTTP,
         * que corren en la tarea propia del servidor httpd. */
        while (1) {
            int rssi = 0;
            esp_wifi_sta_get_rssi(&rssi);
            ESP_LOGI(TAG, "Activo | RSSI: %d dBm", rssi);
            vTaskDelay(pdMS_TO_TICKS(5000));
        }
    } else {
        ESP_LOGE(TAG, "No se pudo conectar a '%s'", WIFI_SSID);
    }
}
