# Function that validates the authtoken and returns roles
# Return values: meanig
# -1 : Invalid Token
# 0 :  admin
# 1 :  
# 2 :  user

from pymysql import connect
from db import connectUserDb
import json
import re

USERTYPE = "role"
USERID = "userId"


def validateEmail(email):
    regex_email = "^[\\w!#$%&'*+/=?`{|}~^-]+(?:\\.[\\w!#$%&'*+/=?`{|}~^-]+)*@(?:[a-zA-Z0-9-]+\\.)+[a-zA-Z]{2,6}$"
    return re.fullmatch(regex_email, email)


def validatePhone(phone):
    regex_phone = "(0|91)?[6-9][0-9]{9}"
    return re.fullmatch(regex_phone, phone)


def valid_uuid(uuid):
    regex = re.compile('^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z', re.I)
    match = regex.match(uuid)
    return bool(match)

def validateToken(authToken):
    flag = 1
    response = {USERTYPE: -1, USERID: None}
    if not valid_uuid(authToken) :
        flag = 0
        print("Not authtoken")
        return response

    conn = connectUserDb()
    cur = conn.cursor()

    query = "SELECT user_id, role FROM tbl_session WHERE token ='%s'" % authToken
    cur.execute(query)
    res = cur.fetchone()

    if not res:
        response[USERTYPE] = -1
        response[USERID] = None
    elif res["role"] == '0':
        response[USERTYPE] = 0
        response[USERID] = res['user_id']
    elif res["role"] == '1':
        response[USERTYPE] = 1
        response[USERID] = res['user_id']
    elif res["role"] == '2':
        response[USERTYPE] = 2
        response[USERID] = res['user_id']
    else:
        flag = 0

    if flag:
        cur.close()
        conn.close()
        return response

def message(N, msg):
    return {
        "statusCode": N,
        "body": json.dumps({"message": f"{msg}"}),
    }