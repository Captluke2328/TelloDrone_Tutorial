#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

//Define joystick pins (Analog)

//Using Arduino
#define joyX = A0;
#define joyY = A1;
int sw = 2;

//Using RPI Pico
//#define joyX = 27;
//#define joyY = 26;
//int sw = 22;

//Declare pin state
String valx, valy;
char xyData[32] = "";
int sw_state = 0;

RF24 radio(8, 7); // CE, CSN
const byte address[6] = "00001";

//Create a struct that do not exceed 32 bytes
struct Data_to_be_sent {
  byte ch1;
  byte ch2;
};

Data_to_be_sent sent_data;

void setup() {
  Serial.begin(9600);
  radio.begin();
  radio.setAutoAck(false);
  radio.setPALevel(RF24_PA_MIN);
  radio.setDataRate(RF24_250KBPS);
  radio.openWritingPipe(address);
  radio.stopListening();  

//Reset each channel value
  sent_data.ch1 = 130;
  sent_data.ch2 = 130;
}

void loop() {

sent_data.ch1 = map(analogRead(A0), 0, 1024, 0, 255);
sent_data.ch2 = map(analogRead(A1), 0, 1024, 0, 255);

radio.write(&sent_data, sizeof(Data_to_be_sent));
Serial.println(sent_data.ch1);
}
