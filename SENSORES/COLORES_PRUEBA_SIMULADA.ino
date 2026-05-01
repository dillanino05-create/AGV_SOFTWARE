#include <Wire.h>
#include "Adafruit_TCS34725.h"

// -------- PINES MOTORES --------
#define IN1 4
#define IN2 5
#define IN3 6
#define IN4 7

// Crear objeto del sensor
Adafruit_TCS34725 tcs = Adafruit_TCS34725(
  TCS34725_INTEGRATIONTIME_50MS,
  TCS34725_GAIN_4X
);

// -------- SETUP --------
void setup() {
  Serial.begin(115200);

  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  if (!tcs.begin()) {
    Serial.println("No se detecta el TCS34725");
    while (1);
  }

  Serial.println("Sensor de color listo");
}

// -------- LOOP --------
void loop() {
  String color = detectarColor();

  Serial.print("Color detectado: ");
  Serial.println(color);

  // ACCIONES DEL AGV
  if (color == "VERDE") {
    girarIzquierda();
  }
  else if (color == "ROJO") {
    retroceder();
  }
  else if (color == "AZUL") {
    girarIzquierda();
  }
  else {
    detener();
  }

  delay(300);
}

// -------- FUNCION DETECTAR COLOR --------
String detectarColor() {
  uint16_t r, g, b, c;
  tcs.getRawData(&r, &g, &b, &c);

  // Evitar errores por baja luz
  if (c < 50) return "NINGUNO";

  // Normalización con canal clear
  float rf = (float)r / c;
  float gf = (float)g / c;
  float bf = (float)b / c;

  // DEBUG para calibrar
  Serial.print("R: "); Serial.print(rf, 3);
  Serial.print(" G: "); Serial.print(gf, 3);
  Serial.print(" B: "); Serial.println(bf, 3);

  if (rf > 0.45 && gf < 0.30 && bf < 0.25) return "ROJO";

  if (rf > 0.38 && gf > 0.32 && bf < 0.20) return "AMARILLO";

  if (gf > 0.40 && rf < 0.30 && bf < 0.25) return "VERDE";

  if (bf > 0.40 && rf < 0.30 && gf < 0.35) return "AZUL";

  return "NINGUNO";
}

// -------- FUNCIONES DE MOVIMIENTO --------
void avanzar() {
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}

void retroceder() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
}

void girarIzquierda() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}

void detener() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
}