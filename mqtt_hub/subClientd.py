# Define subClient's callback functions
# subClient는 신규기기 등록 요청을 받는 Client 입니다

import time, os, json
from Mqtthub_object import *
from mqttClient import watchdogClient, DBClient, ivuname, ivpw
from seceretism import unsecretism


############### read json file ###############
dirPath = os.path.dirname(os.path.realpath(__file__))

# files.json stores files' name
with open(dirPath+'/'+'data/file.json', 'r') as json_fileInfo:
    fileInfo = json.load(json_fileInfo)


############### define callback function ###############
def on_connect(client, userdata, flags, rc):
    print('subClient')
    if rc == 0:
        print("connected OK")
    else:
        print("Bad connection Returned code=", rc)

def on_disconnect(client, userdata, flags, rc=0):
    print(str(rc))

def on_subscribe(client, userdata, mid, granted_qos):
    print("subscribed: " + str(mid) + " " + str(granted_qos))

def on_message(client, userdata, message):
    print('message arrived...')
    print('received time: ', time.strftime('%Y-%m-%d %H:%M:%S'))
    msg = str(message.payload.decode("utf-8"))
    print("message received=", msg)
    print("message topic=", message.topic)
    print("message qos=", message.qos)
    print("message retain flag=", message.retain)
    print()

    print('registering new device...')
    obj_id = register_object(client, msg)
    if(obj_id == -1):
        return

    # watchdogClient subscribes new device
    # extract topic string
    with open(dirPath+'/'+fileInfo['topic'], 'r') as json_topic:
        topic = json.load(json_topic)
    com = unsecretism(topic['common'], ivuname, ivpw)
    topicStr = com + topic['report'] + '/' + obj_id
    print('Subscribe topic:' + topicStr)
    
    # subscribe
    watchdogClient.subscribe(topicStr, 1)

    # DBClient publish new device
    # extract topic string
    topicStr = com + topic['dbQuery']
    print('Publishing topic:' + topicStr)
    
    # make message
    tempID = msg.split('/')[0]
    syncMsg = topic['dbAdd'] + '/' + obj_id + '/' + msg[len(tempID) +1:]    # ../id/type/func1/func2/...funcN
    print('sync msg: '+syncMsg)
    
    # publishing
    DBClient.publish(topicStr, syncMsg, 1)
    

def on_publish(client, userdata, mid):
    print("In on_pub callback mid= ", mid)



############### define functions ###############
# return String id
def register_object(client, data):
    print('starting object register')
    tempID = data.split('/')[0]

    data = data[len(tempID) +1:]

    if(  Mqtthub_object.check_data(data) == -1  ):
        print('data invalid')
        return -1

    newObj = Mqtthub_object(data)

    # allocate ID
    id = newObj.get_obj_ID()
    print('new Device ID:', id)

    # generate ack message
    ack_msg = id
    print('ack:',ack_msg)
    
    # extract topics
    with open(dirPath+'/'+fileInfo['topic'], 'r') as json_topic:
        topic = json.load(json_topic)
    com = unsecretism(topic['common'], ivuname, ivpw)

    # publisihing
    print('publishing...')
    print('topic: ', com + topic['publish'] + '/' + tempID, ack_msg)
    client.publish(com + topic['publish'] + '/' + tempID, ack_msg, 1)

    return id