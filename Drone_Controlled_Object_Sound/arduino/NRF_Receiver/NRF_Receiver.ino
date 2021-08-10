
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

RF24 radio(8, 7); // CE, CSN
const byte address[6] = "00001";

struct Received_data {
  byte ch1;
  byte ch2;
};

Received_data received_data;

int ch1_value = 0;
int ch2_value = 0;

void setup() {

  received_data.ch1 = 130;
  received_data.ch2 = 130;
  
  Serial.begin(9600);
  radio.begin();
  radio.setAutoAck(false);
  radio.setPALevel(RF24_PA_MIN);
  radio.setDataRate(RF24_250KBPS);
  radio.openReadingPipe(0,address);
  radio.startListening();

}

unsigned long last_Time =0;

void receive_the_data()
{
  if(radio.available()> 0)
  {
    radio.read(&received_data, sizeof(Received_data));
    last_Time = millis();
  }
}

void loop() {
  receive_the_data();
  ch1_value = received_data.ch1;
  ch2_value = received_data.ch2;
  String sp1 = " : ";
  Serial.println(ch1_value + sp1 + ch2_value);

 }
