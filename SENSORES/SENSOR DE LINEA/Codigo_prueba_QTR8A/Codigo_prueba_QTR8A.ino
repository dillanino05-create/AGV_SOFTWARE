const int sensores[8] = {36, 39, 34, 35, 32, 33, 25, 26};

void setup() {
  Serial.begin(115200);

  // Resolución ADC del ESP32
  analogReadResolution(12); // 0 - 4095

  Serial.println("Prueba QTR-8A con ESP32");
}

void loop() {

  for (int i = 0; i < 8; i++) {

    int lectura = analogRead(sensores[i]);

    Serial.print(lectura);
    Serial.print("\t");
  }

  Serial.println();

  delay(100);
}