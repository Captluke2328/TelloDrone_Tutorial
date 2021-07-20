//Using Arduino
#define joyX = A0;
#define joyY = A1;
int sw = 2;

//Using RPI Pico
//#define joyX = 27;
//#define joyY = 26;
//int sw = 22

int valx, valy;
char xyData[32] = "";
int sw_state = 0;

void setup() {
  Serial.begin(9600);
}
 
void loop() {
  // put your main code here, to run repeatedly:
  valx = map(analogRead(A0), 0, 1024, 0, 255);
  valy = map(analogRead(A1), 0, 1024, 0, 255);
  
  //print the values with to plot or view
  Serial.print(valx);
  Serial.print("\t");
  Serial.println(valy);
  
}
