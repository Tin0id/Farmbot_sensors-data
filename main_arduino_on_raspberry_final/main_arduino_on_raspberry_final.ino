
#include <Wire.h>
#include <SPI.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include "Si115X.h"
#include "SCD30.h"
#include <SoftwareSerial.h>

#define RX1 0
#define TX1 17

SoftwareSerial Uart1(RX1, TX1);

Si115X si1151;

#define BME_SCK 13
#define BME_MISO 12
#define BME_MOSI 11
#define BME_CS 10
#define WATER_SENSOR 2

#define SEALEVELPRESSURE_HPA (1013.25)

Adafruit_BME280 bme; // I2C
//Adafruit_BME280 bme(BME_CS); // hardware SPI
//Adafruit_BME280 bme(BME_CS, BME_MOSI, BME_MISO, BME_SCK); // software SPI

unsigned long delayTime;

void setup() {
  //--- O2
  Uart1.begin(9600);
  delay(10);
  Serial.begin(9600);
  while(!Serial);    // time to get serial running
  //--- Co2
  scd30.initialize();
  //--- Water
  pinMode(WATER_SENSOR, INPUT);
  //--- sun
  uint8_t conf[4];
  Wire.begin();
  while (!si1151.Begin()){
    
  }
  //--- BME
  unsigned status;  
  status = bme.begin();  
}


void loop() { 
  while(!Serial.available()){

  }
  Serial.print("Start ");
  Serial.println("Start");

  print_bme();
  delay(100);
  print_sun();
  delay(100);
  print_water();
  delay(100);
  print_co2();
  delay(100);
  print_O2();
  delay(100);

}
void print_water(){
  Serial.print("Water ");
  
  Serial.println(digitalRead(WATER_SENSOR));
  delay(100);
  
}
void print_co2(){
  float result[3] = {0};
  
  if(scd30.isAvailable()){
    scd30.getCarbonDioxideConcentration(result);
    Serial.print("CO2 ");
    Serial.println(result[0]);
     
    Serial.print("Temp_co2 ");
    Serial.println(result[1]);
        
    Serial.print("Humidity_co2 ");
    Serial.println(result[2]);
        
  }

}
void print_sun(){
    Serial.print("IR ");
    while(!si1151.ReadHalfWord()){

    }
    Serial.println(si1151.ReadHalfWord());
    Serial.print("VISIBLE ");
    while(!si1151.ReadHalfWord()){
      
    }
    
    Serial.println(si1151.ReadHalfWord_VISIBLE());
    Serial.print("UV ");
    while(!si1151.ReadHalfWord()){
      
    }
    Serial.println(si1151.ReadHalfWord_UV());
    
}
void print_bme() {
    Serial.print("Temp_bme ");
    
    Serial.println(bme.readTemperature());

    Serial.print("Pressure_bme ");
    
    Serial.println(bme.readPressure() / 100.0F);

    Serial.print("Altitude_bme ");
    
    Serial.println(bme.readAltitude(SEALEVELPRESSURE_HPA));

    Serial.print("Humidity ");
    
    Serial.println(bme.readHumidity());
}

void print_O2(){
  if (Uart1.available()) {
    uint8_t begin_code = Uart1.read();
    delay(10);
    uint8_t state_code = Uart1.read();
    delay(10);
    uint8_t high_code = Uart1.read();
    delay(10);
    uint8_t low_code = Uart1.read();
    delay(10);
    uint8_t check_code = Uart1.read();
    delay(10);
    uint8_t checkk_code = Uart1.read();
    delay(10);
    uint8_t checkkk_code = Uart1.read();
    delay(10);
    uint8_t checkkkk_code = Uart1.read();
    delay(10);
    uint8_t checkkkkk_code = Uart1.read();
    delay(10);

    if (begin_code == 255 && state_code == 134) {
      float O2_val = ((high_code * 256) + low_code) * 0.1;
      Serial.print("O2 ");
      Serial.println(O2_val);
      
    }
  }

  while (Uart1.read() >= 0);  // clear buffer
  
}