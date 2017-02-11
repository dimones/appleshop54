import json,threading,requests,uuid,pymysql,sys,datetime


def get_mysql_connection() -> pymysql.cursors.DictCursor:
    return pymysql.connect(host='217.71.129.181',
                           user='root',
                           password='jmXQF97JqkeNxV5B%',
                           db='appleshop54',
                           charset='utf8')


def get_mysql_connection_1() -> pymysql.cursors.DictCursor:
    return pymysql.connect(host='217.71.129.181',
                           user='root',
                           password='jmXQF97JqkeNxV5B%',
                           db='appleshop54',
                           charset='utf8',
                           cursorclass=pymysql.cursors.DictCursor)

class AuthHelper:
    device_token = None
    device_id = None
    try:
        connection = get_mysql_connection()
    except:
        pass
    def __init__(self,device_token,device_id):
        self.device_id = device_id
        self.device_token = device_token

    def __del__(self):
        try:
            self.connection.close()
        except Exception as e:
            print(str(e), file=sys.stderr)
    def buildSQLgetUserID(self):
        return "(SELECT DISTINCT(user_id) FROM MYNSTU_TOKENS WHERE device_id='%s' AND device_token='%s')" % \
               (self.device_id,self.device_token)

    def tokenExist(self, device_token):
        try:
            if self.connection.open != True:
                self.connection = get_mysql_connection()
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT * FROM MYNSTU_TOKENS WHERE device_token = '%s'" % device_token)
                if cursor.rowcount > 0:
                    return True
                else:
                    return False
        except Exception as e:
            print(str(e),file=sys.stderr)
        # finally:
        #     connection.close()
    def getNewToken(self):
        temp = uuid.uuid4().hex
        while self.tokenExist(temp):
            temp = uuid.uuid4().hex
        return temp

class Auther:
    username = None
    password = None
    device_id = None
    a_helper = None
    connection = get_mysql_connection()
    def __init__(self, username, password, device_id):
        self.username = username
        self.password = password
        self.device_id = device_id
        self.a_helper = AuthHelper(None,device_id)

    def __del__(self):
        self.a_helper = None
        try:
            self.connection.close()
        except Exception as e:
            print(str(e), file=sys.stderr)
    def auth_user(self):
        pass

class AdminHelper(AuthHelper):
    def isValid(self):
        try:
            if self.connection.open != True:
                self.connection = get_mysql_connection()
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT id FROM MYNSTU_ADMIN_TOKENS tok WHERE tok.device_id = '%s' "
                               "AND tok.device_token = '%s'" % (self.device_id, self.device_token))
                if cursor.rowcount > 0:
                    return True
                else:
                    return False
        except Exception as e:
            print(str(e))
            return 'error happened'
    def getRole(self):
        try:
            if self.connection.open != True:
                self.connection = get_mysql_connection()
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT role FROM MYNSTU_ADMIN_USERS WHERE id = (SELECT user_id FROM MYNSTU_ADMIN_TOKENS tok WHERE tok.device_id = '%s' "
                               "AND tok.device_token = '%s' LIMIT 0,1)" % (self.device_id, self.device_token))
                if cursor.rowcount > 0:
                    return cursor.fetchone()[0]
                else:
                    return -1
        except Exception as e:
            print(str(e))
            return 'error happened'
    def getUserName(self):
        try:
            if self.connection.open != True:
                self.connection = get_mysql_connection()
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT username FROM MYNSTU_ADMIN_USERS WHERE id = (SELECT user_id FROM MYNSTU_ADMIN_TOKENS tok WHERE tok.device_id = '%s' "
                               "AND tok.device_token = '%s' LIMIT 0,1)" % (self.device_id, self.device_token))
                if cursor.rowcount > 0:
                    return cursor.fetchone()[0]
                else:
                    return -1
        except Exception as e:
            print(str(e))
            return 'error happened'
class AdminAuther(Auther):
    def tokenExist(self, device_token):
        try:
            if self.connection.open != True:
                self.connection = get_mysql_connection()
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT id FROM MYNSTU_ADMIN_TOKENS WHERE device_token = '%s'" % device_token)
                if cursor.rowcount > 0:
                    return True
                else:
                    return False
        except Exception as e:
            print(str(e), file=sys.stderr)
            # finally:
            #     connection.close()

    def getNewToken(self):
        temp = uuid.uuid4().hex
        while self.tokenExist(temp):
            temp = uuid.uuid4().hex
        return temp
    def auth_user(self):
        begin = datetime.datetime.now()
        try:
            if self.connection.open != True:
                self.connection = get_mysql_connection()
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT id FROM MYNSTU_ADMIN_USERS au WHERE au.username = '%s' and au.password='%s'"
                               %(self.username, self.password))
                user_id = -1
                if cursor.rowcount > 0:
                    user_id = cursor.fetchone()[0]
                else:
                    return json.dumps({"succeed": False})

                cursor.execute("SELECT id FROM MYNSTU_ADMIN_TOKENS WHERE device_id='%s'" % (self.device_id))
                ids = [element for tupl in cursor.fetchall() for element in tupl]
                if len(ids) > 0:
                    cursor.execute("DELETE FROM MYNSTU_ADMIN_TOKENS WHERE id IN %s" % (
                        str(ids).replace('[', '(').replace(']', ')')))
                device_token = self.getNewToken()
                cursor.execute(
                    "INSERT INTO MYNSTU_ADMIN_TOKENS(device_id,device_token,user_id) VALUES('%s','%s', %s)" % (
                    self.device_id, device_token, user_id))
                self.connection.commit()
                return json.dumps({"succeed": True, 'device_token': device_token})
        except Exception as e:
            print('AdminAuther auth: %s' % str(e))


if __name__ == '__main__':
    # a = AuthHelper('fd8f7307c56e46e0ba4925d05f474794', '33ec7015-e736-687d-a1d3-d4c81061ed2e')
    # print(a.getUserInfo())
    # aa = Auther('info_audit','642imb','test')
    # print(aa.auth_user())
    # headers = {'Content-Type': 'application/json',
    #            'X-OpenAM-Username': 'avgustan.2016@stud.nstu.ru',
    #            'X-OpenAM-Password': '37469361LIoNNS'}
    # headers = {'Content-Type': 'application/json',
    #            'X-OpenAM-Username': 'avt310_bogomolov',
    #            'X-OpenAM-Password': '396sgx'}
    #
    # r = requests.post('https://login.nstu.ru/ssoservice/json/authenticate', headers=headers)
    # resp = r.json()
    # print(resp)
    # sr_r = requests.get('https://api.ciu.nstu.ru/v1.0/data/simple/staff_inf',
    #                     cookies={'NstuSsoToken': resp['tokenId']})
    # sr_r_json = sr_r.json()
    # print(sr_r_json)
    a = AdminAuther('dimones','123qwe','test')
    # print(a.auth_user())
    # pass
    # a = Auther('avt310_bogomolov','396sgx','test-device-id')
    #
    a_h = AdminHelper('e20d0e93430642d5843c022bb559ee73','test')
    print(a_h.getUserName())
    # print(a.auth_user())