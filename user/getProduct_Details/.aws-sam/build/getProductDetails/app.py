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

    params = json.loads(event['body'])
    print(params)
    try:
        id = int(params["id"])
    except Exception as e:
        print(e)
        return message(400,"Invalid input")
    



    searchQ = f"SELECT * FROM tbl_pdt WHERE id = '{id}'"
    search2 = f"SELECT * FROM pdt_image WHERE pdt_id = '{id}'"

    conn = connectProductDb()
    cur = conn.cursor()
    try:
        cur.execute(searchQ)
        res = cur.fetchone()
        cur.execute(search2)
        res2 = cur.fetchall()
    except Exception as e:
        print(e)
        conn.close()
        return message(400,e)
    
    conn.close()
    images = []

    for item in res2:
        images.append(item['url'])

    res["images"]=images
    print(res)
    # print(res2)

    return {
        "statusCode": 200,
        "body":json.dumps(res)
    }