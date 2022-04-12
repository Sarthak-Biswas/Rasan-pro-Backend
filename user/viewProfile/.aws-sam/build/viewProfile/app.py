import json
import datetime
from re import search
from db import connectUserDb,connectProductDb
from utility import validateEmail,validatePhone,message,USERID,USERTYPE,validateToken

def lambda_handler(event,context):
    try:
        authToken = event['headers']['authToken']
    except:
        try:
            authToken = event['headers']['authtoken']
        except:
            print("token not found")
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Token Not Found"}),
            }
    
    print("start")
    info = validateToken(authToken)
    role = info[USERTYPE]
    id = info[USERID]

    if role == -1 :
        print("Invalid Token")
        return message(403,"Invalid Token")


    searchQ = f"SELECT id,name,phone,email,address,picture FROM tbl_user WHERE id = '{id}'"

    conn = connectUserDb()
    cur = conn.cursor()
    try:
        cur.execute(searchQ)
        res = cur.fetchone()
    except Exception as e:
        print(e)
        conn.close()
        return message(400,e)
    
    print(res)

    return {
        "statusCode": 200,
        "body":json.dumps(res)
    }