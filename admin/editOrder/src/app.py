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

    params = json.loads(event['body'])

    try:
        tracking_id = params['tracking_id']
        status = params['status']
        # user_id = params['user_id']
        order_id = params['order_id']
    except Exception as e:
        print(e)
        return(400,e)

    if role != 0 :
        print("Admin-only")
        return message(403,"Admin only.")
    
    query = f"UPDATE tbl_orders SET `status` = '{status}', `tracking_id` = '{tracking_id}' WHERE `order_id` = '{order_id}'"
    print(query)

    conn = connectProductDb()
    cur = conn.cursor()
    try:
        cur.execute(query)
        conn.commit()
        # conn.close()
    except Exception as e :
        print(e)
        conn.close()
        return message(400, e)

    query2 = f"UPDATE tbl_all_order SET `status` = '{status}', `tracking_id` = '{tracking_id}' WHERE `order_id` = '{order_id}'"
    print(query)

    try:
        cur.execute(query2)
        conn.commit()
        conn.close()
    except Exception as e :
        print(e)
        conn.close()
        return message(400, e)

    return {
        "statusCode": 200,
        "body": "Successfully updated"
    }