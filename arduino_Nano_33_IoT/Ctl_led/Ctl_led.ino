// Led Device
#include <WiFi.h>
#include <WiFiClient.h>
#include <WiFiServer.h>
#include <PubSubClient.h>

// net info
// wifi
#define WFSSID      ""
#define PASSWORD    ""
// broker info
#define MQTT_IP    ""
#define MQTT_PORT   1883 // default 1883
#define USERNAME    ""
#define PW          ""

// topic info
const char* mqtt_common_topic = "";
const char* mqtt_regist_topic = "/dev/new";
const char* mqtt_regist_ack_topic = "/dev/new/ack/";
const char* mqtt_control_topic = "/dev/control/";
const char* mqtt_report_topic = "/dev/report/";

// device info
char temporaryID[20] = "";  // Empty means it will generate randomly
const char* dev_name = "nanoIoT_led";
const char* dev_type = "control";

char deviceID[20];
char mqtt_topic[50];
char mqtt_message[50];

// device setting
#define LED 8

// device function
#define FUNCN 2
#define CTL_MAX 20  // Control String's max size
char func[FUNCN][CTL_MAX] = {"on", "off"};  // 수신받는 명령어

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
  Serial.println(WiFi.localIP()); // <- return the IP Add of itself

  // MQTT client setting
  client.setServer(MQTT_IP, MQTT_PORT); // set broker
  
  client.setCallback(regist_callback);

  // Device setting
  pinMode(LED, OUTPUT);
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

  // subscribe control topic  ->  [common]/dev/control/[dev ID]
  strcpy(mqtt_topic, mqtt_common_topic);
  strcat(mqtt_topic, mqtt_control_topic);
  strcat(mqtt_topic, deviceID);
  
  Serial.print("subscribtion\ntopic: ");  // debug
  strprint(mqtt_topic);
  Serial.println();

  client.subscribe(mqtt_topic);

  // callback 함수 재설정
  client.setCallback(control_callback);

}

void control_callback(char* topic, byte* payload, unsigned int length){ // 메세지 받은 후 명령어 추출, 동작, 결과 보고 토픽 발행
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");

  // extract control command
  char ctl[CTL_MAX] = "";
  
  for (int i = 0; i < length; i++) { ctl[i] = (char)payload[i]; }
  Serial.print("message: ");
  strprint(ctl);
  Serial.println();

  // if kill signal -> terminate the program
  if(!strcmp(ctl, "kill")){
    digitalWrite(LED, LOW);
    exit(0);
  }
  // compare cmd and cmd list in the code above
  int funci;
  bool exist=false;
  for(funci=0; funci<FUNCN; funci++){
    if(!strcmp(ctl, func[funci])){
      exist=true;
      break;
    }
  }

  // =========================== //
  // define your custom function //
  // ===== Code this block ===== //
  if(exist){
    if(funci == 0){ // Default: on
      digitalWrite(LED, HIGH);
    }
    else if(funci == 1){  // Default: off
      digitalWrite(LED, LOW);
    }
    else{ // something went wrong
      Serial.println("error");
    }
  }
  else{ // wrong syntax on cmd
    Serial.println("Function match fail");
    return; // no report
  }


  strcpy(mqtt_topic, mqtt_common_topic);
  strcat(mqtt_topic, mqtt_report_topic);
  strcat(mqtt_topic, deviceID);

  // message: a function in the function list
  strcpy(mqtt_message, func[funci]);

  // debug
  Serial.print("report message publishing...\ntopic: ");
  strprint(mqtt_topic);
  Serial.print("\tmessage: ");
  strprint(mqtt_message);
  Serial.println();

  // report topic publish
  client.publish(mqtt_topic, mqtt_message);
  Serial.println("published");

  return;

}

void reconnect() {
  while(!client.connected()) {
    Serial.println("Attempting MQTT connection...");
    if(client.connect(dev_name, USERNAME, PW)) {
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
      for(int i=0; i<FUNCN; i++){
        strcat(mqtt_message, "/");
        strcat(mqtt_message, func[i]);
      }

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