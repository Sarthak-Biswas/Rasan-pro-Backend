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
    try:
        pdt_id = params['id']
    except Exception as e:
        print(e)
        return message(400,e)
    
    Q = f"INSERT INTO tbl_wishlist (`pdt_id`,`user_id`) VALUES ('{pdt_id}','{id}')"

    conn = connectProductDb()
    cur = conn.cursor()
    try:
        cur.execute(Q)
        conn.commit()
    except Exception as e:
        print(e)
        conn.close()
        return message(400,e)
    
    # print(res)
    # print(res2)

    # q = "SELECT * FROM tbl_pdt"
    # try:
    #     cur.execute(q)
    #     res2 = cur.fetchall()
    # except Exception as e:
    #     print(e)
    #     conn.close()
    #     return message(400,e)

    conn.close()

    # out = []
    # count = 0

    # for val in res:
    #     for val2 in res2:
    #         if val['pdt_id'] == val2['id']:
    #             out.insert(count, val2)

    out = {"message": "Product added to wishlist"}

    print(out)

    return {
        "statusCode": 200,
        "body":json.dumps(out)
    }