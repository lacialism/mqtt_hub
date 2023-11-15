import os, json

dirPath = os.path.dirname(os.path.realpath(__file__))

with open(dirPath+'/data/file.json', 'r') as json_fileInfo:
    fileInfo = json.load(json_fileInfo)

with open(dirPath+'/'+fileInfo['object_data_format'], 'r') as json_object_data_format:
    valid_format = json.load(json_object_data_format)

class Mqtthub_object:

    # constructor
    def __init__(self, data=None):   # String data = 'name/func1/func2...
        # instance member variable
        self.__id = ''
        self.__name = ''
        self.__type = ''
        self.__func = []
        
        if(data == None):
            return

        print()
        print('############### object constructor ###############')

        # construct object with data    data format: [device name]/[device func1]/.../[device func2]
        if(self.__set_data(data) == -1):
            print('construction failed')
            return -1
        
        print('############### object creation success ###############')

        self.show_obj_info()
    
    # member functions
    # to set data
    def __set_data(self, data): # String data = 'tempID/type/name/func1/func2.../funcN
        print()
        print('############### set data ###############')
        if(self.check_data(data) == -1):
            print('cant regist')
            return -1
        self.__name = data.split('/')[0]
        self.__type = data.split('/')[1]
        for i in data.split('/')[2:]:
            self.__func.append(i)
        
        # get new ID
        self.__id = self.__set_ID()

        # if there is no object_list.json file, generate the json file
        if(self.__id == valid_format['id_init']):
            with open(dirPath+'/'+fileInfo['object_list'], 'w') as json_objlist:
                print('initialize object_list.json')
                json.dump({}, json_objlist, indent=4)

        # read object file to add data of new object
        with open(dirPath+'/'+fileInfo['object_list'], 'r') as objlistfile:
            objlist = json.load(objlistfile)
            
        #============================================= Done 23-08-13 #
        # append the id in the idList, which is one of the keys in the dictionary
        try:
            objlist['idList'].append(self.__id)
        # when the key idList does not exist in the dictionary
        except KeyError as noKeyList:
            print('idList does not exist')
            print('Make new list')
            objlist['idList']=[self.__id]
        
        # add new object data ~ {key-ID : value-data}
        objlist[self.__id] = data
        

        # update the object_list.json
        with open(dirPath+'/'+fileInfo['object_list'], 'w') as objlistfile:
            json.dump(objlist, objlistfile, indent=4)
        
        print('############### set data ###############')

        return 0
    
    # to check the data is valid
    @staticmethod
    def check_data(data):
        print()
        print('############### check data ###############')
        
        # check the data format -> name/type/func1/.../funcN
        if(len(data.split('/')) < 3):   # name, type, and a function are mandatory
            print(data)
            print(len(data.split('/')))
        
            print('data format invalid')
            return -1
        
        print('data format is valid')
        print('############### check data ###############')

        return 0
    
    def show_obj_info(self):
        print()
        print('############### object infomation ###############')
        print('name:',self.__name)
        print('id:', self.__id)
        print('type:', self.__type)
        print('func num:', len(self.__func))
        print('func:', self.__func)
        print('############### object infomation ###############')
    
    def get_obj_ID(self):
        return self.__id
    
    # 수정후 #
    # 마지막 ID 번호 +1 부터 순서대로 중복 검사를 함
    # ID에 알파벳이 들어가는 경우는 가정하지 않았음
    # ID가 스킵된 경우는 고려하지 않고 IDList의 마지막 원소를 기준으로 잡음
    def __set_ID(self):
        # read object file and calculate next ID
        try:
            with open(dirPath+'/'+fileInfo['object_list'], 'r') as json_objlist:
                objlist = json.load(json_objlist)
        # 파일을 열어봤는데 파일이 없거나, 안에 내용이 없으면 id_init으로 지정된 값을 반환함
        except FileNotFoundError as e:              # no file exception
            return valid_format['id_init']
        except json.decoder.JSONDecodeError as e1:  # no content in file exception
            return valid_format['id_init']
        # idList는 있는데 등록된 사물이 없을 경우
        if(len(objlist['idList']) == 0):
            return valid_format['id_init']
        
        # 마지막 ID 번호 +1 부터 순서대로 중복검사 후 적절한 값을 반환
        newID=str( int(objlist['idList'][-1]) + 1 )
        while(newID in objlist['idList']):
            newID=str( int(newID)+1 )
        
        if(len(valid_format['id_format']) - len(newID) > 0):
            for i in range(len(valid_format['id_format']) - len(newID)):
                newID = '0' + newID

        
        return newID
        
        
    
    def __set_obj(self, id, name, func):
        self.__id = id
        self.__name = name
        self.__func = func.copy()

    
    def get_object_by_ID(self, id):
        try:
            with open(dirPath+'/'+fileInfo['object_list'], 'r') as objlistfile:
                objlist = json.load(objlistfile)
        except FileNotFoundError as e:              # no file exception
            print('There is no object_list.json file')
            print('Register object first, plz')
            return -1
        except json.decoder.JSONDecodeError as e1:  # no content in file exception
            print('There is object_list.json file but it has no content')
            print('Register object first, plz')
            return -1
        if id in objlist:
            print('I found valid id')
            print('Taking device info...')

            self.__id = id
            self.__name = objlist[id].split('/')[0]
            self.__type = objlist[id].split('/')[1]
            self.__func.clear()
            for i in range(2, len(objlist[id].split('/'))):
                self.__func.append(objlist[id].split('/')[i])
            print('Success!')
            return 0
        else:
            print('There is no valid id')
            return -1
            

    def __check_id(self, id):
        if not (len(valid_format['id_format']) == len(id)):
            print('id size incorrect')
            return -1
        for i in range(len(valid_format['id_format'])):
            if(valid_format['id_format'][i] == '0'):    # check number
                if not (int(id[i]) <= 9 and int(id[i]) >= 0):
                    print('id[', i, '] is not number')
                    return -1
            elif(valid_format['id_format'][i] == 'A'):  # check character
                if not (ord(id[i]) >= ord('A') and ord(id[i]) <= ord('z')):
                    print('id[', i, '] is not charcter')
                    return -1
        return 0
    
    def del_object(self, topic):
        with open(dirPath+'/'+fileInfo['object_list'], 'r') as objlistfile:
            objlist = json.load(objlistfile)
        objlist['idList'].remove(self.__id)
        del objlist[self.__id]

        # update the object_list.json
        with open(dirPath+'/'+fileInfo['object_list'], 'w') as objlistfile:
            json.dump(objlist, objlistfile, indent=4)