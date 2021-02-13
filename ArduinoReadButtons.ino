/*
  DigitalReadSerial

  Reads a digital input on pin 2, prints the result to the Serial Monitor

  This example code is in the public domain.

  http://www.arduino.cc/en/Tutorial/DigitalReadSerial
*/

// digital pin 2 has a pushbutton attached to it. Give it a name:
int pushButton2 = 2;
int pushButton3 = 3;
int pushButton4 = 4;
int pushButton5 = 5;
int pushButton6 = 6;
int pushButton7 = 7;
int pushButton8 = 8;
int pushButton9 = 9;

// the setup routine runs once when you press reset:
void setup() {
  // initialize serial communication at 9600 bits per second:
  Serial.begin(9600);
  // make the pushbutton's pin an input:
  pinMode(pushButton2, INPUT);
  pinMode(pushButton3, INPUT);
  pinMode(pushButton4, INPUT);
  pinMode(pushButton5, INPUT);
  pinMode(pushButton6, INPUT);
  pinMode(pushButton7, INPUT);
  pinMode(pushButton8, INPUT);
  pinMode(pushButton9, INPUT);
}

// the loop routine runs over and over again forever:
void loop() {
  // read the input pin:
  int buttonState2 = digitalRead(pushButton2);
  int buttonState3 = digitalRead(pushButton3);
  int buttonState4 = digitalRead(pushButton4);
  int buttonState5 = digitalRead(pushButton5);
  int buttonState6 = digitalRead(pushButton10);
  int buttonState7 = digitalRead(pushButton7);
  int buttonState8 = digitalRead(pushButton8);
  int buttonState9 = digitalRead(pushButton9);

  pinMode(LED_BUILTIN, OUTPUT);
  // print out the state of the button:
  Serial.println(buttonState2);
  Serial.println(buttonState3);
  Serial.println(buttonState4);
  Serial.println(buttonState5);
  Serial.println(buttonState6);
  Serial.println(buttonState7);
  Serial.println(buttonState8);
  Serial.println(buttonState9);
  Serial.println("\n");
  delay(100);        // delay in between reads for stability
}
