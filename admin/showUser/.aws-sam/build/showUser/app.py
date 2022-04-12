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
    query = f"SELECT id,phone,email,name,total_transaction,picture,address FROM tbl_user WHERE id = '{id}'"

    conn = connectUserDb()
    cur = conn.cursor()
    try:
        cur.execute(query)
        res = cur.fetchall()
        print(res)
        # conn.close()
    except Exception as e :
        print(e)
        conn.close()
        return message(400, e)
    conn.close()

    q = f"SELECT order_id, create_date FROM tbl_all_order WHERE user_id = '{res[0]['id']}'"

    conn = connectProductDb()
    cur = conn.cursor()

    try:
        cur.execute(q)
        res2 = cur.fetchall()
        print(res2)
        # conn.close()
    except Exception as e :
        print(e)
        conn.close()
        return message(400, e)

    if res2:
        res = res + res2

    print(res)
    return {
        "statusCode": 200,
        "body": json.dumps(res, indent=4, sort_keys=True, default=str)
    }