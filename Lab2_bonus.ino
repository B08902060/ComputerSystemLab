#define button 7
#define volume A4

bool prev_b = 0;
int prev_v = 0;
bool play = 0;
int brightness = 0;
void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(button, INPUT);
  pinMode(volume, INPUT);
  // 13 LED binary
  // pinMode(13, OUTPUT);
  // 11 LED linear birghtness
  pinMode(11, OUTPUT);

}

void loop() {
  // put your main code here, to run repeatedly:
  bool b = digitalRead(button);
  int v = analogRead(volume);
  
  if(prev_b != b && b){
    Serial.print("b\n");
    play = !play;   
  }
  // 音樂播放時LED，反之暗 bonus:1
  /* 
  if (play) digitalWrite(13, HIGH);
  else digitalWrite(13, LOW);
  */
  prev_b = b;
  
  if(abs(prev_v - v) > 20){
    Serial.print("v\n");
    Serial.println(v);
    prev_v = v;
  }
  // 旋轉調整音樂播放開關(超過600:開\低於450:關) bonus:2
  if( v > 600 && !play ){
    Serial.print("b\n");
    play = !play;
  }
  if( v < 450 && play ){
    Serial.print("b\n");
    play = !play; 
  }
  // 亮度隨音量改變 (bonus3)
  // noramlize to brightness 0~250
  birghtness = (v)/1024*250
  analogWrite(11,brightness);


  delay(10);
}
