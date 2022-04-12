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

    if role == -1 :
        print("Invalid User")
        return message(403,"Invalid User.")

    params = json.loads(event['body'])
    print(params)

    try:
        order_id = params["id"]
    except Exception as e:
        print(e)
        return message(400,"Invalid input")
    
    res = None
    query = f"SELECT * FROM tbl_orders WHERE id = '{order_id}'"

    conn = connectProductDb()
    cur = conn.cursor()
    try:
        cur.execute(query)
        res = cur.fetchone()
        print(res)
        # conn.close()
    except Exception as e :
        print(e)
        conn.close()
        return message(400, e)

    q = f"SELECT id,primary_image,name FROM tbl_pdt WHERE id = '{res['pdt_id']}'"
    
    try:
        cur.execute(q)
        res3 = cur.fetchone()
        print(res3)
        # conn.close()
    except Exception as e :
        print(e)
        conn.close()
        return message(400, e)

    res['product_image'] = res3['primary_image']
    res['name'] = res3['name']
        

    # res2 = None  
    # Q = "SELECT name, picture FROM tbl_user WHERE id = " + f"{id}"
    # print(Q)

    # conn2 = connectUserDb()
    # cur = conn2.cursor()
    # try:
    #     cur.execute(Q)
    #     res2 = cur.fetchall()
    #     print(res2)
    #     conn2.close()
    # except Exception as e :
    #     print(e)
    #     conn2.close()
    #     return message(400, e)

    # # res[len(res)]['user_name'] = res2[0]['name']
    # # res[len(res)]['user_picture'] = res2[0]['picture']

    # a = {"user_name": res2[0]['name'], "user_picture": res2[0]['picture']} 
    
    # res.insert(len(res),a)

    print(res)
    return {
        "statusCode": 200,
        "body":json.dumps(res, indent=4, sort_keys=True, default=str)
    }