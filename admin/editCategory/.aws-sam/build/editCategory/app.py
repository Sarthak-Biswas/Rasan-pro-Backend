from email.mime import image
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

    params = json.loads(event['body'])
    print(params)
    try:
        id = params['id']
        active = params["active"]
        name = params['name']
        img = params['url']
        # img = params['img']
    except Exception as e:
        print(e)
        return message(400,"Invalid input")
    
    insertQ = f"SELECT active FROM tbl_category WHERE id = '{id}'"
    print(insertQ)

    conn = connectProductDb()
    cur = conn.cursor()
    try:
        cur.execute(insertQ)
        res = cur.fetchone()
    except Exception as e :
        print(e)
        conn.close()
        return message(400, e)


    q = f"UPDATE tbl_category SET active = '{active}', category_name = '{name}', img = '{img}' WHERE id = '{id}'"
    print(q)

    try:
        cur.execute(q)
        conn.commit()
    except Exception as e :
        print(e)
        conn.close()
        return message(400, e)

    conn.close()

    print("product added")
    return {
        "statusCode": 200,
        "body":json.dumps("category edited.")
    }