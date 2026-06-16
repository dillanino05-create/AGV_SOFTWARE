# Registra este componente "main" ante ESP-IDF.
# REQUIRES declara las dependencias que usa main.c:
#   esp_wifi/esp_event/esp_netif/nvs_flash -> conexion WiFi
#   esp_http_server                        -> servidor HTTP de control del carro
#   driver                                 -> GPIO (direccion de motores) y LEDC (PWM)
idf_component_register(
    SRCS "main.c"
    INCLUDE_DIRS "."
    REQUIRES esp_wifi esp_event esp_netif nvs_flash esp_http_server driver
)
