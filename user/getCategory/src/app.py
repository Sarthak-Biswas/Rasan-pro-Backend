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

    if role == 0:
        searchQ = f"SELECT id,category_name,active,img FROM tbl_category"
    else:
        searchQ = f"SELECT id,category_name,img FROM tbl_category WHERE active = 1"

    conn = connectProductDb()
    cur = conn.cursor()
    try:
        cur.execute(searchQ)
        res = cur.fetchall()
    except Exception as e:
        print(e)
        conn.close()
        return message(400,e)
    
    conn.close()
    print(res)
    # print(res2)

    return {
        "statusCode": 200,
        "body":json.dumps(res)
    }