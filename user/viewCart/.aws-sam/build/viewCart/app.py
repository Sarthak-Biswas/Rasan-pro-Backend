import json
from urllib import response
from db import connectUserDb,connectProductDb
from utility import validateToken,USERID,USERTYPE,message, valid_uuid



def lambda_handler(event,context):
    print(event)
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

    info = validateToken(authToken)
    role = info[USERTYPE]
    id = info[USERID]

    if role != 2 :
        print("Invalid Token-> role 1")
        return message(403,"Access Declined")

    Q = f"SELECT * FROM tbl_cart where `user_id` = {id}"
    conn = connectProductDb()
    cur = conn.cursor()

    try:
        cur.execute(Q)
        res = cur.fetchall()
    except Exception as e:
        conn.close()
        return message(401,e)



    Q2 = f"SELECT id,name,description,price,stock,primary_image,category,likes FROM tbl_pdt where "

    for i in res:
        k = f"id = {i['pdt_id']} or " 
        Q2 = Q2 + k
    Q2 = Q2[:-3]

    print(Q2)

    try:
        cur.execute(Q2)
        res2 = cur.fetchall()
    except Exception as e:
        conn.close()
        return message(401,e)

    for i in res:
        s = i['pdt_id']
        for j in res2:
            if j['id'] == s:
                    i['name'] = j['name']
                    i['category'] = j['category']
                    i['primary_image'] =  j['primary_image']
                    i['likes'] = j['likes']
                    i['price'] = j['price']
                    i['stock'] = j['stock']
                    break
            else:
                    pass

    return{
            "statusCode": 200,
            "body": json.dumps(res)
        }
