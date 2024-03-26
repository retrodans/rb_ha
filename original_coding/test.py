import requests
import hashlib
import json

apiUrl = 'https://v24.fenixgroup.eu/api/v0.1/human'

class fenixV24:

    def runner(self):
        self.getConfig()
        self.token()
        self.read()

    def getConfig(self):
        with open('../config.json') as fp:
            self.config = json.load(fp)

    def token(self):
        url = apiUrl + '/user/auth/'
        passwordHash = hashlib.md5(bytes(self.config['password'], encoding='utf-8')).hexdigest(),
        data = {
            'email': self.config['email'],
            'password': passwordHash,
            'remember_me': 'true',
            'lang': 'en_GB',
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        response = requests.post(url, data=data, headers=headers)
        json_object_auth = json.loads(response.content)
        self.token = json_object_auth['data']['user_infos']['token']

    # This is working, but pointless without authentication (copying tokens from browsers is not ideal).
    def read(self):
        url = apiUrl + '/smarthome/read/'
        data = {
            'token': self.token,
            'smarthome_id': self.config['smarthome_id'],
            'lang': 'en_GB',
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        response = requests.post(url, data=data, headers=headers)
        json_object = json.loads(response.content)
        for zoneId in json_object['data']['zones']:
            zone = json_object['data']['zones'][zoneId]
            primaryDevice = zone['devices']['0']
            print("* It is currently " + primaryDevice['temperature_air'] + " degress Fahrenheit in " + zone['zone_label'] + '. [heating_up:' + primaryDevice['heating_up'] + ']')

fenixv24 = fenixV24()
fenixv24.runner()
