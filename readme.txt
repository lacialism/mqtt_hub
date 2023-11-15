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
# - 메인 파일(이 파일)에서는 subClient의 loopforever()를 실행하고, watchdog/DB Client의 loopforever()는 쓰레드로 실행함
# - MQTT 브로커 인증기능 추가
# 0.0.5 #
# - subProcess 도 쓰레드로 돌아감
# - 대신에 프로그램 돌아가면서 관리자로부터 입력 받을 수 있도록 무한 루프문으로 돌림
#   - restart: 재시작
#   - change [ip/port] ['ip주소'/'Port번호']
# - MQTT 브로커 인증기능 추가
# - 키 생성 및 브로커 접속 위해서 username 과 password 필요 - 특정 브로커에 대한 단일 계정을 상정함
# - 프로그램 실행시 로그인 하거나 새로 등록 - username, password 혹은 브로커 ip, port번호 혹은 common topic 변경시 새로 등록해야함
# - 파일 암호화 기능 추가
# 0.0.6 #
# - 신규 등록 메시지에 타입 (control/sensor)가 추가됨
#   - 이에 따라 메시지 받는 절차가 변경됨
# - 사물 삭제 기능 추가
# - DB Request 기능 구현 (삭제 요청 처리)


main file -> mqtt_hub.py
    username & pw -> your mosquitto(mqtt broker)'s username & pw (mosquitto 설정으로 추가해야함)
    broker ip/port -> 127.0.0.1/1887(or which you set) if you run it where mosquitto was installed |OR| your broker IP/port if you run it somewhere else than where the program was installed
    common topic -> Any word you want

other config
mqttClient.py
    ivuname, ivpw -> These values will be used as elements of Initial Vector for security. Change these to enhance the security level of your system
