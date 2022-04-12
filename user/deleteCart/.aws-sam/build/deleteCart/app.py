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
    id = info[USERID]

    if role != 2 :
        print("Invalid Token-> role 1")
        return message(403,"Access Declined")
  
    
    # params = json.loads(event['body'])
    # try:
    #     cart_id = params['id']
    # except Exception as e:
    #     print(e)
    #     return message(400,e)

    Q = f"DELETE FROM tbl_cart WHERE user_id = '{id}'"
    conn = connectProductDb()
    cur = conn.cursor()

    try:
        cur.execute(Q)
        conn.commit()
    except Exception as e:
        conn.close()
        return message(401,e)
    conn.close()
    return message(200,"Deleted cart")