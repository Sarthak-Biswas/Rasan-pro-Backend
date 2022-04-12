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

    params = json.loads(event['body'])

    try:
        name = params['name']
        email = params['email']
        phone = params['phone']
        address = params['address']
    except Exception as e:
        print(e)
        return message(400,e)

    # picture = params['picture']
    if len(name) == 0 or len(address) == 0:
        return message(400, "Invalid input")

    if role == -1 :
        print("Invalid Token")
        return message(403,"Invalid Token")

    if not validatePhone(phone):
        return message(400, "Invalid phone number")

    if not validateEmail(email):
        return message(400, "Invalid email")

    Q = f"UPDATE tbl_user SET name = '{name}', email = '{email}', phone = '{phone}', address = '{address}' WHERE id = '{id}'"

    conn = connectUserDb()
    cur = conn.cursor()
    try:
        cur.execute(Q)
        conn.commit()
    except Exception as e:
        print(e)
        conn.close()
        return message(400,e)
    
    conn.close()

    return message(200, "Profile updated")