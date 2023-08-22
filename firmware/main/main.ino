#include <LiquidCrystal.h>
LiquidCrystal lcd(8, 9, 4, 5, 6, 7);
char LCD_Row_1[17];
char LCD_Row_2[17];

#include <FastGPIO.h>
#define DREAD(x) FastGPIO::Pin<x>::isInputHigh()
#define DHIGH(x) FastGPIO::Pin<x>::setOutputHigh()
#define DLOW(x) FastGPIO::Pin<x>::setOutputLow()

#define ENC_A 3 // D3
#define ENC_B 2 // D2
volatile long spindlePos = 0; // Spindle position
long last_spindlePos = 0;
int delta_mot = 0;
int steep_by_click = 16;

#define DIR 11
#define STEP 12
#define ENA 13

enum Pressed_Key
{
  Key_None,
  Key_Right,
  Key_Up,
  Key_Down,
  Key_Left,
  Key_Select
};
byte Pressed_Key=Key_None;
boolean key_flag=false;

void setup() {
  Serial.begin(9600);
  // put your setup code here, to run once:
  lcd.begin(16, 2);
  snprintf(LCD_Row_1, 17," Hello world");
  Print();

  pinMode(ENC_A, INPUT_PULLUP);
  pinMode(ENC_B, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(ENC_A), spinEnc, FALLING);

  pinMode(DIR, OUTPUT);
  digitalWrite(DIR, LOW);
  pinMode(ENA,OUTPUT);
  digitalWrite(ENA, LOW);
  pinMode(STEP, OUTPUT);
  digitalWrite(STEP, HIGH);
  Serial.println("Start ...");
  new_divider();
}


void loop() 
{
  // put your main code here, to run repeatedly:
 
  menu();
  if (spindlePos != last_spindlePos) {
    snprintf(LCD_Row_2, 17, "Enc: %3ld ", spindlePos); 
    Print();
    delta_mot = spindlePos - last_spindlePos;
    last_spindlePos = spindlePos;
    if (delta_mot != 0) {

      if (delta_mot > 0) { 
        DHIGH(DIR);
      } else {
        DLOW(DIR);
        }  
      delayMicroseconds(100);
      for (int i=0; i < (abs(delta_mot) * steep_by_click) ; i++ )   {
        DLOW(STEP);
        delayMicroseconds(50);
        DHIGH(STEP);
        delayMicroseconds(100);
        }
      } 
      Serial.println(spindlePos);    
    }
  }

void menu()
{
  int ADC_value = analogRead(A0);
  if (ADC_value < 50) Pressed_Key=Key_Right;
  else if (ADC_value < 180) Pressed_Key=Key_Up;
  else if (ADC_value < 330) Pressed_Key=Key_Down;
  else if (ADC_value < 520) Pressed_Key=Key_Left;
  else if (ADC_value < 830) Pressed_Key=Key_Select;
  else Pressed_Key = Key_None;

  if (!key_flag)
  {
      switch (Pressed_Key)
      {
        case Key_Left:
          MenuKeyLeftPressed();
          break;
        case Key_Right:
          MenuKeyRightPressed();
          break;
        case Key_Up:
          MenuKeyUpPressed();
          break;
        case Key_Down:
          MenuKeyDownPressed();
          break;
        case Key_Select:
          MenuKeySelectPressed();
          break;
      }
  }
  if (Pressed_Key == Key_None) key_flag = false;
}
void new_divider()
{
  key_flag= true;
  memset (LCD_Row_1, ' ' ,17);
  snprintf(LCD_Row_1, 17,"Steep/Click: %3hd", steep_by_click);
  Print();

}
void MenuKeySelectPressed()
{
  }
void MenuKeyRightPressed()
{
  spindlePos = 0;
  last_spindlePos = 0;
  snprintf(LCD_Row_2, 17, "Enc: %3ld ", spindlePos); 
  Print();
  }
void MenuKeyLeftPressed()
{
  }
void MenuKeyUpPressed()
{
  if (steep_by_click < 20) {
    steep_by_click++;
    new_divider();
    }
  }

void MenuKeyDownPressed()
{
  if (steep_by_click > 1) {
    steep_by_click--;
    new_divider();
    }
  }

void Print()
{
lcd.clear();
lcd.setCursor(0, 0);
lcd.print(LCD_Row_1);

lcd.setCursor(0, 1);
lcd.print(LCD_Row_2);
}

// Called on a FALLING interrupt for the rotary encoder pin.
// Keeps track of the position.
void spinEnc()
{
 int delta;
 delta = DREAD(ENC_B) ? -1 : 1;
 spindlePos += delta;
  }
