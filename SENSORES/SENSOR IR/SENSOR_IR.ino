#define IR 8

void setup() {
  pinMode(IR, INPUT);
  Serial.begin(115200);
}

void loop() {
  int estado = digitalRead(IR);

  if (estado == LOW) {
    Serial.println("Objeto detectado");
  } else {
    Serial.println("Sin objeto");
  }

  delay(300);
}