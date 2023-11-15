import json, os, threading, sys
import paho.mqtt.client as mqtt
from time import sleep
from mqttClient import *
from seceretism import *
from Mqtthub_object import *
import subClientd, watchdogClientd, DBClientd

# @Description
# Mqtt hub 로 동작하기 위한 프로그램의 메인 파일로 동작합니다.
# broker 정보는 broker_info.json 파일로부터 받아옵니다.

############### get json ###############
dirPath = os.path.dirname(os.path.realpath(__file__))
print('File path: ' + dirPath)

# files.json stores files' name
with open(dirPath+'/'+'data/file.json', 'r') as json_fileInfo:
    fileInfo = json.load(json_fileInfo)

# broker_info stores broker network info
with open(dirPath+'/'+fileInfo['broker_info'], 'r') as json_broker_info:
    broker_info = json.load(json_broker_info)

# topic stores topic strings
with open(dirPath+'/'+fileInfo['topic'], 'r') as json_topic:
    topic = json.load(json_topic)


############### Init Sequence ###############
# 유저 이름 + 비밀번호로 키 생성
def setIP(ip, username, pw):
    broker_info['brokerIP'] = seceretism(ip, username, pw)
    with open(dirPath+'/'+fileInfo['broker_info'], 'w') as json_broker_info:
        json.dump(broker_info, json_broker_info, indent=4)

def setPort(port, username, pw):
    broker_info['port'] = seceretism(port, username, pw)
    with open(dirPath+'/'+fileInfo['broker_info'], 'w') as json_broker_info:
        json.dump(broker_info, json_broker_info, indent=4)

def setCom(com, username, pw):
    topic['common'] = seceretism(com, ivuname, ivpw)
    with open(dirPath+'/'+fileInfo['topic'], 'w') as json_topic:
        json.dump(topic, json_topic, indent=4)

def login(username):
    for i in range(6):
        if(i==5):
            print('Login Fail')
            sys.exit()
            
        pw = input('password:')
        
        ckey = check_key(username, pw)
        if(ckey == 0):
            print('success')
            return pw
        elif(ckey == -1):
            print('There is no login file')
            sys.exit()
        elif(ckey == 1):
            print('Incorrect')

        print('attempt '+str(i+1)+' failed')

def register_broker():
    print('register your mqtt username and password')
    username = input('username:')
    pw = input('password:')

    generate_key(username, pw)
    while(True):
        print('enter broker\'s network info (it wont check your entering so be careful)')
        ip = input('Broker IP:')
        port = input('Port Number:')
        print('Enter your common topic')
        com = input('Common Topic:')
        print()
        m = input('ip='+ip+'\nport='+port+'\ncommon topic='+com+'\nAre you sure? (Y/N)')
        print()
        if(m == 'Y' or m == 'y'):
            break

    setIP(ip, username, pw)
    setPort(port, username, pw)
    setCom(com, ivuname, ivpw)

    return username, pw

def delObject(id):
    target = Mqtthub_object()
    fail = target.get_object_by_ID(id)
    if(fail == -1):
        print('object match fail')
        return
    
    com = unsecretism(topic['common'], ivuname, ivpw)
    
    # send kill msg
    targetTopic = com + topic['control'] + '/' + id
    watchdogClient.publish(targetTopic, 'kill')
    dbTopic = com + topic['dbQuery']
    dbMsg = topic['dbSyn'] + '/' + id + '/kill'
    DBClient.publish(dbTopic, dbMsg)
    
    # unsubscribe
    targetTopic = com + topic['report'] + '/' + id
    print('unsubscribe='+targetTopic)
    watchdogClient.unsubscribe(targetTopic)
    target.del_object(targetTopic)
    

############### Login & Generate Key ###############
username = ''
pw = ''
if(len(sys.argv) == 2): # When the program starts with username argument
    username = sys.argv[1]
    pw = login(username)

elif(len(sys.argv) == 1):   # When the program starts without an argument
    m = input('Login? (Y/N)')
    if(m == 'Y' or m == 'y'):
        username = input('username:')
        pw = login(username)

    else:
        username, pw = register_broker()


############### call-back function 설정 ###############
# print('############### call-back function 설정 ###############')

# 콜백 함수 설정 on_connect(브로커에 접속), on_disconnect(브로커에 접속중료), on_subscribe(topic 구독),
# on_message(발행된 메세지가 들어왔을 때)
subClient.on_connect = subClientd.on_connect
subClient.on_disconnect = subClientd.on_disconnect
subClient.on_subscribe = subClientd.on_subscribe
subClient.on_message = subClientd.on_message
subClient.on_publish = subClientd.on_publish
subClient.username_pw_set(username, pw)

watchdogClient.on_disconnect = watchdogClientd.on_disconnect
watchdogClient.on_connect = watchdogClientd.on_connect
watchdogClient.on_subscribe = watchdogClientd.on_subscribe
watchdogClient.on_message = watchdogClientd.on_message
watchdogClient.on_publish = watchdogClientd.on_publish
watchdogClient.username_pw_set(username, pw)

DBClient.on_disconnect = DBClientd.on_disconnect
DBClient.on_connect = DBClientd.on_connect
DBClient.on_subscribe = DBClientd.on_subscribe
DBClient.on_message = DBClientd.on_message
# DBClient.on_publish = DBClientd.on_publish
DBClient.username_pw_set(username, pw)


############### extract infomations from json ###############
# print('############### extract infomations from json ###############')

# extract broker info
brokerIP = unsecretism(broker_info['brokerIP'], username, pw)
port = int(unsecretism(broker_info['port'], username, pw))
print('Broker Address:'+brokerIP+':', port)

# extract common topic string
com = unsecretism(topic['common'], ivuname, ivpw)

############### connect to broker & run ###############
# print('############### connect to broker & run ###############')

# 각 Client broker 연결
subClient.connect(brokerIP, port)
watchdogClient.connect(brokerIP, port)
DBClient.connect(brokerIP, port)

# subClient subscribes 'Subscribe Topic'
topicStr = com + topic['subscribe']
print('subClient subscribes \'Subscribe Topic\':'+ topicStr)
subClient.subscribe(topicStr, 1)

# DBClient subscribe 'DBRequest Topic'
topicStr = com + topic['dbRequest']
print('DBClient subscribe \'DBRequest Topic\':'+ topicStr)
DBClient.subscribe(topicStr, 1)

# Declare Thread Function
def sub_loop():
    subClient.loop_forever()
def watchdog_loop():
    watchdogClient.loop_forever()
def DB_loop():
    DBClient.loop_forever()


# Loop Thread Allocate and Run
subProcess = threading.Thread(target=sub_loop)
watchhdogProcess = threading.Thread(target=watchdog_loop)
DBProcess = threading.Thread(target=DB_loop)
subProcess.daemon = True
watchhdogProcess.daemon = True
DBProcess.daemon = True
subProcess.start()
watchhdogProcess.start()
DBProcess.start()

sleep(1)

while(True):
    cmd = input('>>>')
    
    if(cmd == 'exit'):
        exit

    elif(cmd == 'restart'):
        print('not start again')
        os.execl(sys.executable, sys.executable, *sys.argv)
    
    elif(cmd == 'list'):
        print('list')
    
    elif(cmd.split(' ')[0] == 'del'):
        print('del object in idlist and objlist')
        s=cmd.split(' ')
        try:
            if(s[1] == '*'):
                with open(dirPath+'/'+fileInfo['object_list'], 'r') as objlistfile:
                    objlist = json.load(objlistfile)
                for targetID in objlist['idList']:
                    delObject(targetID)
            else:
                targetID = s[1]
                delObject(targetID)
        except(IndexError):
            print('invalid input')
            continue

    elif(cmd.split(' ')[0] == 'change'):
        s=cmd.split(' ')
        try:
            if(s[1] == 'ip'):
                ip = s[2]
                setIP(ip)

            elif(s[1] == 'port'):
                port = s[2]
                setPort(port)

        except(IndexError):
            print('invalid input')
            continue

print('program unexpectedly dead')

