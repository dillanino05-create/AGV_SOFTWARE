const int sensores[8] = {36, 39, 34, 35, 32, 33, 25, 26};

int umbral = 2000;

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);
}

void loop() {

  for (int i = 0; i < 8; i++) {

    int lectura = analogRead(sensores[i]);

    if (lectura > umbral)
      Serial.print("1 ");
    else
      Serial.print("0 ");
  }

  Serial.println();
  delay(100);
}