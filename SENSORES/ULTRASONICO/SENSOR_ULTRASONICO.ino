#include <Arduino.h>

#define TRIG 9
#define ECHO 10

long duracion;
float distancia;

void setup() {
  Serial.begin(115200);
  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);
}

void loop() {
  distancia = medirDistancia();

  Serial.print("Distancia: ");
  Serial.print(distancia);
  Serial.println(" cm");

  delay(300);
}

float medirDistancia() {
  digitalWrite(TRIG, LOW);
  delayMicroseconds(2);

  digitalWrite(TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG, LOW);

  duracion = pulseIn(ECHO, HIGH);

  float distancia = duracion * 0.034 / 2;

  return distancia;
}