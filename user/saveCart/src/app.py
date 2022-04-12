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
        return{
            "statusCode": 403,
            "body": json.dumps({
                    "message": "Invalid Token"
                }),
        }
        

    info = validateToken(authToken)
    role = info[USERTYPE]
    # id = info[USERID]

    if role != 2 :
        print("Invalid Token-> role 1")
        return message(403,"Access Declined")
  
    
    params = json.loads(event['body'])
    print(params)

    q = f"UPDATE tbl_cart SET quantity = CASE id "
    for p in params:
        id = int(p['id'])
        quantity = int(p['quantity'])
        q = q + f"WHEN '{id}' THEN {quantity} "
    
    q = q + "ELSE 1 END WHERE id IN ("
    for p in params:
        id = int(p['id'])
        q = q + f"'{id}',"
    q = q[:-1] + f")"
    print(q)


    conn = connectProductDb()
    cur = conn.cursor()

    try:
        cur.execute(q)
        conn.commit()
    except Exception as e:
        conn.close()
        return message(401,e)
    conn.close()
    return message(200,"saved to cart")