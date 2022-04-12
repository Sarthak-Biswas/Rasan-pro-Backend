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


    searchQ = f"SELECT * FROM tbl_wishlist WHERE user_id = '{id}'"

    conn = connectProductDb()
    cur = conn.cursor()
    try:
        cur.execute(searchQ)
        res = cur.fetchall()
    except Exception as e:
        print(e)
        conn.close()
        return message(400,e)
    
    print(res)
    # print(res2)

    q = "SELECT * FROM tbl_pdt"
    try:
        cur.execute(q)
        res2 = cur.fetchall()
    except Exception as e:
        print(e)
        conn.close()
        return message(400,e)

    conn.close()

    out = []
    count = 0

    for val in res:
        for val2 in res2:
            if val['pdt_id'] == val2['id']:
                out.insert(count, val2)

    print(out)

    return {
        "statusCode": 200,
        "body":json.dumps(out)
    }