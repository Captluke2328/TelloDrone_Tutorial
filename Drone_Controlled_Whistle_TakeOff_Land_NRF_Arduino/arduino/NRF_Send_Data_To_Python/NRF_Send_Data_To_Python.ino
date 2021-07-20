
#define numofvaluereceive 2
#define digitpervaluereceive 3
#define numofvaluesend 2

#define joyX = A0;
#define joyY = A1;
int sw = 2;

int valreceive[numofvaluereceive];
int stringlength = numofvaluereceive * digitpervaluereceive + 1;
int valssend[numofvaluesend] = {0, 0};

int counter = 0;
bool counterstart = false;
String receivestring;

int valx, valy;
char xyData[32] = "";
int sw_state = 0;

void setup() {
  Serial.begin(9600);
}

void senddata(int myvals[numofvaluesend]){
  String mystring;
  for (int i=0; i<numofvaluesend; i++){
    mystring +=String(myvals[i]) + '#';
  }
  Serial.println(mystring);
}

void loop() {
  valy = map(analogRead(A0), 0, 1024, 0, 255);
  valx = map(analogRead(A1), 0, 1024, 0, 255);

  valssend[0] = valy;
  valssend[1] = valx;
  senddata(valssend);
  //delay(100);

}
