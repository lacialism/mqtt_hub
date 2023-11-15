// Ultra Sonic Sensor for MQTT_hub
#include <WiFi.h>
#include <WiFiClient.h>
#include <WiFiServer.h>
#include <PubSubClient.h>

// net info
// wifi
#define WFSSID      ""
#define PASSWORD    ""
// broker info
#define MQTT_IP     ""
#define MQTT_PORT   51213 // default 1883
#define USERNAME    ""
#define PW          ""

// topic info
const char* mqtt_common_topic = "";
const char* mqtt_regist_topic = "/dev/new";
const char* mqtt_regist_ack_topic = "/dev/new/ack/";
const char* mqtt_report_topic = "/dev/report/";

// device info
char temporaryID[20] = "";  // Empty means it will generate randomly
const char* dev_name = "nanoIoT_ultrasonic";
const char* dev_type = "sensor";

char deviceID[20];
char mqtt_topic[50];
char mqtt_message[50];

// device setting
#define FUNCN 2
#define CTL_MAX 20  // Control String's max size
#define TRIGPIN 6
#define ECHOPIN 7
const char* minVal = "20";    // mm
const char* maxVal = "5000";  // mm
// level 0: 0~99(mm) / 1: 100~199 / 2: 200~299 ...
int clevel, level;
char report_topic[50];  // 수시로 발행 하므로 매번 만드는게 비효율적
#define TRIAL 2         // 초음파 신호 측정 횟수


void strcat(char* str1, char* str2){
  int i, j;
  for(i=0; str1[i]; i++);
  for(j=0; str2[j]; i++, j++){
    str1[i]=str2[j];
  } str1[i]='\0';
}

char* strcpy(char *dest, const char *src)
{
  for (; *dest = *src; dest++, src++); //복사한 문자가 참이면 반복
  return dest;
}

void strprint(char* str){
  for(int i=0; str[i]; i++){
    Serial.print(str[i]);
  }
}

void genTempID(){
  for(int i=0; i<8; i++){
    temporaryID[i] = (char)random('0', '9');
  }
}



WiFiClient espClient;
PubSubClient client(espClient);
long lastMsg = 0;
char msg[50];
int val = 0;

void setup() {
  // 디버그용 시리얼 통신
  Serial.begin(115200);
  //Serial.setDebugOutput(true);
  Serial.println();

  for(uint8_t t = 3; t > 0; t--) {
    Serial.print("[SETUP] BOOT WAIT");
    Serial.print(t);
    Serial.println("...");
    Serial.flush();
    delay(1000);
  }
  // WiFi setting
  WiFi.begin(WFSSID, PASSWORD);
  Serial.print("Connecting to WiFi");
  while(WiFi.status() != WL_CONNECTED) {
    delay(300);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
  
  // MQTT client setting
  client.setServer(MQTT_IP, MQTT_PORT);
  
  client.setCallback(regist_callback);

  // Device setting
  pinMode(ECHOPIN, INPUT);   // echoPin 입력    
  pinMode(TRIGPIN, OUTPUT);  // trigPin 출력

  level = -1;
}

void loop() {
  client.loop();
  
  if(!client.connected()) {
    reconnect();
  }
  if(WiFi.status() != WL_CONNECTED) {
    WiFi.begin(WFSSID, PASSWORD);
    Serial.print("Reconnecting WiFi");
    while(WiFi.status() != WL_CONNECTED) {
      Serial.print(".");
    }
    Serial.println();
    Serial.println("WiFi Reconnected");
  }
}

void regist_callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");


  Serial.print("=> ");
  for (int i = 0; i < length; i++) { Serial.print((char)payload[i]); } Serial.println();

  // Extract device ID
  for(int i=0; i<length; i++){ deviceID[i]=(char)payload[i]; }
  Serial.print("Device ID: ");
  strprint(deviceID);
  Serial.println();
  
  // 토픽 정리
  // unsubscribe ack topic
  strcpy(mqtt_topic, mqtt_common_topic);
  strcat(mqtt_topic, mqtt_regist_ack_topic);
  strcat(mqtt_topic, deviceID);
  client.unsubscribe(mqtt_topic);
  
  // Make sensor report topic
  strcpy(report_topic, mqtt_common_topic);
  strcat(report_topic, mqtt_report_topic);
  strcat(report_topic, deviceID);


  int distance, davg, sum;
  while(1){
    // 측정 시작
    sum=0;
    for(int count=0; count < TRIAL; count++){
      digitalWrite(TRIGPIN, HIGH);          // trigPin: 초음파 발생(echoPin -> HIGH)
      delayMicroseconds(100);
      digitalWrite(TRIGPIN, LOW);           // trigPin: 초음파 끄기(echoPin -> Low)
      distance = ((float)(340 * pulseIn(ECHOPIN, HIGH)) / 1000) / 2;
      if(distance == 0){
        count--;
        continue;
      }
      sum += distance;
      delay(100);
    } // 측정 끝
    
    // 보정값 계산
    davg = sum / TRIAL;
    clevel = davg/100;
    Serial.print("AVG distance: "); Serial.print(davg); Serial.print("mm\tlevel=");  Serial.println(clevel);

    // 변화 수준 비교
    if(level != clevel){
      // Report Message publish    
      char cstr[16];
      itoa(davg, cstr, 10);

      strcpy(mqtt_message, cstr);

      Serial.print("publishing\ntopic: ");  // debug
      strprint(report_topic);
      Serial.print("\tmessage: ");
      strprint(mqtt_message);
      Serial.println();

      client.publish(report_topic, mqtt_message);
      level=clevel;
    }
  }
}

void reconnect() {
  while(!client.connected()) {
    Serial.println("Attempting MQTT connection...");
    if(client.connect("untraSonic_sensor", USERNAME, PW)) {
      Serial.println("connected");

      // if temporaryID is null -> generate Temp ID 
      if(!strcmp(temporaryID, "")){genTempID();}  // strcmp( true->0 false->-1/1 )
      Serial.print("your temporary ID: ");
      strprint(temporaryID);
      Serial.println();

      // subscribe ack topic
      strcpy(mqtt_topic, mqtt_common_topic);
      strcat(mqtt_topic, mqtt_regist_ack_topic);
      strcat(mqtt_topic, temporaryID);
      
      Serial.print("subscribtion\ntopic: ");  // debug
      strprint(mqtt_topic);
      Serial.println();

      client.subscribe(mqtt_topic);
      
      // Regist Message publish
      strcpy(mqtt_topic, mqtt_common_topic);
      strcat(mqtt_topic, mqtt_regist_topic);

      strcpy(mqtt_message, temporaryID);
      strcat(mqtt_message, "/");
      strcat(mqtt_message, dev_type);
      strcat(mqtt_message, "/");
      strcat(mqtt_message, dev_name);
      strcat(mqtt_message, "/");
      strcat(mqtt_message, minVal);
      strcat(mqtt_message, "/");
      strcat(mqtt_message, maxVal);

      Serial.print("publishing\ntopic: ");  // debug
      strprint(mqtt_topic);
      Serial.print("\tmessage: ");
      strprint(mqtt_message);
      Serial.println();

      client.publish(mqtt_topic, mqtt_message);
      
      Serial.println("Publishing DONE");
    } else {
      Serial.print("failed, rc = ");
      Serial.print(client.state());
      Serial.println(" automatically trying again in 1 second");
      delay(1000);
    }
  }
}