# Define DBClient's callback functions
# DBClient는 DB 동기화 관련 Client 입니다

import time, os, json
from mqttClient import watchdogClient, DBClient, ivuname, ivpw
import Mqtthub_object
from seceretism import unsecretism


############### read json file ###############
dirPath = os.path.dirname(os.path.realpath(__file__))

# files.json stores files' name
with open(dirPath+'/'+'data/file.json', 'r') as json_fileInfo:
    fileInfo = json.load(json_fileInfo)

# topic stores topic strings
with open(dirPath+'/'+fileInfo['topic'], 'r') as json_topic:
    topic = json.load(json_topic)


############### define callback function ###############
def on_connect(client, userdata, flags, rc):
    print('DBClient')
    if rc == 0:
        print("connected OK")
    else:
        print("Bad connection Returned code=", rc)

def on_disconnect(client, userdata, flags, rc=0):
    print(str(rc))

def on_subscribe(client, userdata, mid, granted_qos):
    print("subscribed: " + str(mid) + " " + str(granted_qos))

# subscriber callback
def on_message(client, userdata, message):
    print('subClient subscribes...')
    print('received time: ', time.strftime('%Y-%m-%d %H:%M:%S'))
    msg = str(message.payload.decode("utf-8"))
    print("message received=", msg)
    print("message topic=", message.topic)
    print("message qos=", message.qos)
    print("message retain flag=", message.retain)
    print()

    if(msg.split('/')[0] == topic['dbDel']):
        id = msg.split('/')[1]
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
    

# def on_publish(client, userdata, mid):
#     print("In on_pub callback mid= ", mid)
