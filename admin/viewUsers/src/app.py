import json
import datetime
from logging.config import dictConfig
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

    viewQ = "SELECT id,name,address,email,phone,created_on,role,is_active,is_locked,total_transaction,validity,picture FROM tbl_user WHERE role = 1 OR role =2;"
    print(viewQ)

    conn = connectUserDb()
    cur = conn.cursor()
    try:
        cur.execute(viewQ)
        res=cur.fetchall()
        print(res)
    except Exception as e :
        print(e)
        conn.close()
        return message(400, e)

    conn.close()

    return {
        "statusCode": 200,
        "body":json.dumps(res,indent=4,sort_keys=True,default=str)
    }