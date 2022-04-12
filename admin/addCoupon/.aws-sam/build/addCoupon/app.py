import json
import datetime
from logging.config import dictConfig
from time import strftime
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
        coupon = params["coupon"]
        valid_till = params["valid_till"]
        discount = int(params["discount"])
        categories = params["category_name"]
        description = params["description"]
        pricelimit = int(params["pricelimit"])
        quantity = int(params["quantity"])
    except Exception as e:
        print(e)
        return message(400,"Invalid input")

    print(valid_till)
    d1 = valid_till
    d2 = valid_till
    d3 = valid_till
    a = d1[8:10] +"/"+ d2[3:5] +"/"+ d3[0:2] + " " + "23:59:59"
    date_time_obj = datetime.datetime.strptime(a, '%y/%m/%d %H:%M:%S')
    now = datetime.datetime.now()
    created_by = id
    insertQ = f"INSERT INTO tbl_coupon (coupon,valid_till,discount,categories,description,pricelimit,created_by,quantity,create_date, is_active) VALUES ('{coupon}','{date_time_obj}','{discount}','{categories}', '{description}', '{pricelimit}','{created_by}','{quantity}','{now}', '1');"
    print(insertQ)

    conn = connectProductDb()
    cur = conn.cursor()
    try:
        cur.execute(insertQ)
        conn.commit()
        print("query executed")
    except Exception as e :
        print(e)
        conn.close()
        return message(400, e)
 
    print("coupon added")
    return {
        "statusCode": 200,
        "body":json.dumps("coupon added.")
    }