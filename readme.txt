# @Aurthor KMS
# @Since 2023-10-01
# @Version 0.0.6
# @Changes
# 0.0.3 #
# - 기기의 기능을 명령어 키워드 단위로 다루기 위한 전반적인 코드 수정
# - 파일 정리 및 축소
#   + 여러 파일에 흩어져 저장된 규약된 토픽을 topic.json 에 모두 모아 저장
# 0.0.4 #
# - 파일/폴더이름 변경 newDeviceCatcher -> mqtt_hub
# - json 파일은 하위 경로의 data 폴더 안에 저장
# - mqtt Client를 3개로 분할
#     1) subClient : 신규기기 등록
#     2) watchdogClient : 모든 사물 구독
#     3) DBClient : DB 서버와 통신
#     - 각 Client 는 서로를 각자의 call-back 함수에서 호출하여 작동하므로 모든 Client를 mqttClient.py 에서 선언함
# - Client 별 call-back 함수들을 각 파일에서 정의
# - Capstone_object 클래스의 __check_data() 메소드를 static 메소드 check_data()로 변경
# - Capstone_object 클래스에서 딕셔너리 키 개수만 고려하여 작동한 id 할당방식에서 마지막 id를 기준으로 중복검사를 통한 할당으로 변경
# - 메인 파일(mqtt_hub.py)에서는 subClient의 loopforever()를 실행하고, watchdog/DB Client의 loopforever()는 쓰레드로 실행함
# - MQTT 브로커 인증기능 추가
# 0.0.5 #
# - subProcess 도 쓰레드로 돌아감
# - 대신에 프로그램 돌아가면서 관리자로부터 입력 받을 수 있도록 무한 루프문으로 돌림
#   - restart: 재시작
#   - change [ip/port] ['ip주소'/'Port번호']
#   - 등을 구현하려 했지만 아직 미구현...
# - MQTT 브로커 인증기능 추가
# - 키 생성 및 브로커 접속 위해서 username 과 password 필요 - 특정 브로커에 대한 단일 계정을 상정함
# - 프로그램 실행시 로그인 하거나 새로 등록 - username, password 혹은 브로커 ip, port번호 혹은 common topic 변경시 새로 등록해야함
# - 암호화 기능 추가
#   - data/broker_info.json 에 저장되는 ip/port 정보 및 data/topic.json 에 저장되는 common 토픽 정보는 딕셔너리에 암호화 되어 헥사로 저장됨
# 0.0.6 #
# - 신규 등록 메시지에 타입 (control/sensor)가 추가됨
#   - 이에 따라 메시지 받는 절차가 변경됨
# - 삭제 기능
#   - 관리자가 사물을 삭제할 수 있는 기능 추가 : 메인으로 돌아가는 무한 루프문 안에서 동작
#   - 또한, MQTT hub 관리자가 사물을 삭제할 경우 DB에 kill 메시지 전송
#   - DB 로부터 kill 메시지를 보내 삭제를 수행할 수도 있음
#
#   - MQTT hub 에서 동작하는 삭제는 watchdogClient의 감시 토픽 구독을 취소함
#   - MQTT hub 에서 동작하는 삭제는 제어 사물에게 kill 메시지를 전달할 수 있음
#       - 센서의 경우에는 기존에 control 토픽을 구독하지 않지만 kill 메시지 전달을 위해 사용되어질 수도 있음; 현재는 kill 메시지를 못 받음
# - Mqtthub_object 클래스 del_object() 메서드 추가 (object_list.json 에서 사물 정보 제거)


[Configuration]
- before running
mqttClient.py
    ivuname, ivpw -> These values will be used as elements of Initial Vector for security. Change these to enhance the security level of your system

- run time
mqtt_hub.py
    username & pw -> your mosquitto(mqtt broker)'s username & pw (mosquitto 설정으로 추가해야함)
    broker ip/port -> 127.0.0.1/1887(or another Port Number configured) if running it where mosquitto was installed
                    |OR| your broker IP/port if running it on another station
    common topic -> Any word you want


[File Commnets]
{Main File} = mqtt_hub.py
    has three sub Threads for each client
    - subProcess -> subClient : 사물 등록 담당
    - DBProcess -> DBClient : DB 통신 담당
    - watchdogProcess -> watchdogClient : 사물 감시 담당

    메인 스레드는 시작시, 필요한 정보를 입력받고
    세 클라이언트의 브로커 연결/콜백함수설정/스레드할당 의 작업을 수행
    무한 루프문 안에서 Mqtt Hub 관리자의 명령을 입력받고 수행함


{Client File}
    - Client Declare File = mqttClient.py;
    - Client Callback Func Files = subClientd.py, DBClientd.py, watchdogClientd.py

    mqttClient.py
        ├─ subClientd.py
        ├─ DBClientd.py
        └─ watchdogClientd.py


{Mqtthub_object}
    사물 클래스
    추후 수정


{security File} = secretism.py
    암호화에 관한 파일

    정의된 함수
    - generate_key(username, pw)
        username / pw 를 해싱하여 키로 사용 -> 생성된 키는 seceretism.bin 바이너리 파일에 저장
            param : 유저 로그인 정보
            return : 키 스트링 값
    - read_key()
        키를 읽어오는 함수; seceretism.bin 참조 -> generate_key() 선행 필요
            return : 키 스트링 값
    - check_key(username, pw)
        저장된 키 값과 비교하여 로그인 정보가 맞는지 확인
            param : 유저 로그인 정보
            return : Match = 0; Unmatch = 1; FileException = -1
    - secertism(data, username, pw)
        data 를 암호화함; username/pw 는 iv 벡터 요소로써 필요
            param : 문자열, 유저 로그인 정보
            return : 16진수 암호문
    - unsecretism(cipher_text, username, pw)
        cipher_text 를 복호화함; username/pw 는 iv 벡터 요소로써 필요
            param : 16진수 암호문
            return : 복호된 문자열


{data}
    ├─ broker_info.json
    │   : 브로커 정보
    ├─ file.json
    │   : 파일 경로/이름 정보
    ├─ object_data_format.json
    │   : 사물 ID 포맷 정보
    ├─ object_list.json
    │   : 등록된 사물 및 사물ID리스트 저장
    └─ topic.json
        : 시스템에서 사용하는 MQTT 토픽 문자열 저장
