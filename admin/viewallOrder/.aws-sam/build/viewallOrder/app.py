import json
import datetime
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
    
    res = None
    query = "SELECT * FROM tbl_all_order"

    conn = connectProductDb()
    cur = conn.cursor()
    try:
        cur.execute(query)
        res = cur.fetchall()
        print(res)
        conn.close()
    except Exception as e :
        print(e)
        conn.close()
        return message(400, e)

    res2 = None
    Q = "SELECT id, name, picture FROM tbl_user WHERE "
    print(Q)

    for order in res:
        Q = Q + f"id = {order['user_id']} OR "

    conn2 = connectUserDb()
    cur = conn2.cursor()
    try:
        cur.execute(Q[:-4])
        res2 = cur.fetchall()
        print(res2)
        conn2.close()
    except Exception as e :
        print(e)
        conn2.close()
        return message(400, e)

    count = 0
    n = len(res2)

    for values in res:
        for data in res2:
            if values['user_id'] == data['id']:
                values['name'] = data['name']
                values['picture'] = data['picture']

    print(res)
    return {
        "statusCode": 200,
        "body":json.dumps(res, indent=4, sort_keys=True, default=str)
    }