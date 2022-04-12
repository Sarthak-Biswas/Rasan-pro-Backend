import json
import datetime
from unicodedata import name
from db import connectUserDb,connectProductDb
from utility import validateEmail,validatePhone,message,USERID,USERTYPE,validateToken,valid_uuid

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
    
    if not valid_uuid(authToken):
        return message(403,"Invalid Token")
    
    print("start")
    info = validateToken(authToken)
    role = info[USERTYPE]
    id = info[USERID]

    if role != 0 :
        print("Admin-only")
        return message(403,"Admin only.")

    params = json.loads(event['body'])
    print(params)

    try:
        id = params["id"]
    except Exception as e:
        print(e)
        return message(400,"Invalid input")
    
    res = None
    query = f"UPDATE tbl_user SET is_locked = 1, is_active = 0 WHERE id = '{id}'"

    conn = connectUserDb()
    cur = conn.cursor()
    try:
        cur.execute(query)
        conn.commit()
        print(res)
        # conn.close()
    except Exception as e :
        print(e)
        conn.close()
        return message(400, e)

    conn.close()

    print(res)
    return {
        "statusCode": 200,
        "body": "User Locked"
    }