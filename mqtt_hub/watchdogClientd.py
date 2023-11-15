# Define watchdogClient's callback functions
# WatchdogClient는 등록된 기기의 report 토픽을 구독하는 Client 입니다

import time, os, json
from mqttClient import watchdogClient, DBClient, ivuname, ivpw
from seceretism import unsecretism

############### read json file ###############
dirPath = os.path.dirname(os.path.realpath(__file__))

# files.json stores files' name
with open(dirPath+'/'+'data/file.json', 'r') as json_fileInfo:
    fileInfo = json.load(json_fileInfo)


############### define callback function ###############
def on_connect(client, userdata, flags, rc):
    print('wtchdogClient')
    if rc == 0:
        print("connected OK")
    else:
        print("Bad connection Returned code=", rc)

    # Read topic
    with open(dirPath+'/'+fileInfo['topic'], 'r') as json_topic:
        topic = json.load(json_topic)
    
    # object_list.json 을 참고하여 기존에 등록된 기기들을 Subscribe
    try:
        with open(dirPath+'/'+fileInfo['object_list'], 'r') as json_objlist:
            objList = json.load(json_objlist)
        com = unsecretism(topic['common'], ivuname, ivpw)
        for objID in objList['idList']:
            # extract topic string
            topicStr = com + topic['report'] + '/' + objID
            print('Subscribe topic:' + topicStr)
            
            # watchdogClient subscribe topic
            watchdogClient.subscribe(topicStr, 1)
            
    # 파일을 열어봤는데 파일이 없거나, 안에 내용이 없으면 id_init으로 지정된 값을 반환함
    except FileNotFoundError as e:              # no file exception
        print('no file')
    except json.decoder.JSONDecodeError as e1:  # no content in file exception
        print('no content')
    

def on_disconnect(client, userdata, flags, rc=0):
    print(str(rc))

def on_subscribe(client, userdata, mid, granted_qos):
    print('watchdogClient subscribes...')
    print("subscribed: " + str(mid) + " " + str(granted_qos))

# subscriber callback
def on_message(client, userdata, message):

    # object_list.json 을 참고하여 기존에 등록된 기기들을 Subscribe
    try:
        with open(dirPath+'/'+fileInfo['object_list'], 'r') as json_objlist:
            objList = json.load(json_objlist)
    # 파일을 열어봤는데 파일이 없거나, 안에 내용이 없으면 id_init으로 지정된 값을 반환함
    except FileNotFoundError as e:              # no file exception
        print('no file')
        return
    except json.decoder.JSONDecodeError as e1:  # no content in file exception
        print('no content')
        return
    
    msg = str(message.payload.decode("utf-8"))

    # DBClient publish sync message
    # extract topic string
    with open(dirPath+'/'+fileInfo['topic'], 'r') as json_topic:
        topic = json.load(json_topic)
    topicStr = unsecretism(topic['common'], ivuname, ivpw) + topic['dbQuery']
    
    # make message
    devID = message.topic.split('/')[-1]
    syncMsg = topic['dbSyn'] + '/' + devID + '/' + msg

    if(objList[message.topic.split('/')[-1]].split('/')[0] != 'sensor'):    # 제어 사물들은 관리자가 볼 수 있게 화면에 출력
        print('received time: ', time.strftime('%Y-%m-%d %H:%M:%S'))        # 발행 정보
        print("message received=", msg)
        print("message topic=", message.topic)
        print("message qos=", message.qos)
        print("message retain flag=", message.retain)
        print()
        print('Publishing topic:' + topicStr)
        print('sync msg: '+syncMsg)
    
    # publishing
    DBClient.publish(topicStr, syncMsg, 1)

def on_publish(client, userdata, mid):
    print("In on_pub callback mid= ", mid)