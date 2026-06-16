#include <WiFi.h>

const char* ssid = "OPPOA805G";
const char* password = "12345678";

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println();
  Serial.print("Conectando a la red: ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  int intentos = 0;
  while (WiFi.status() != WL_CONNECTED && intentos < 20) {
    delay(500);
    Serial.print(".");
    intentos++;
  }

  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("¡Conectado a WiFi!");
    Serial.print("Dirección IP: ");
    Serial.println(WiFi.localIP());
    Serial.print("Intensidad de señal (RSSI): ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
  } else {
    Serial.println("No se pudo conectar. Revisa el nombre de la red y la contraseña.");
  }
}

void loop() {
  // Verifica el estado de la conexión cada 5 segundos
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("Estado: Conectado");
  } else {
    Serial.println("Estado: Desconectado");
  }
  delay(5000);
}