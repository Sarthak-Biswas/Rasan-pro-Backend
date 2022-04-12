import json
import requests
import datetime
import razorpay
import urllib.request
import urllib.parse
from db import connectUserDb,connectProductDb
from utility import validateEmail,validatePhone,message,USERID,USERTYPE,validateToken,valid_uuid
from secret import key_id, key_secret

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

    if role != 2 :
        print("Invalid user")
        return message(403,"Invalid user")

    params = json.loads(event['body'])

    conn = connectProductDb()
    cur = conn.cursor()
    q = f"UPDATE tbl_orders SET payment_id = '{params['razorpay_payment_id']}' WHERE order_id = '{params['razorpay_order_id']}'"
    q2 = f"UPDATE tbl_all_order SET payment_id = '{params['razorpay_payment_id']}', signature = '{params['razorpay_signature']}' WHERE order_id = '{params['razorpay_order_id']}'"

    try:
        cur.execute(q)
        conn.commit()
    except Exception as e:
        print(e)
        conn.close()
        return message(400,e)

    try:
        cur.execute(q2)
        conn.commit()
    except Exception as e:
        print(e)
        conn.close()
        return message(400,e)

    client = razorpay.Client(auth=(key_id, key_secret))

    k = client.utility.verify_payment_signature(params)
    print(k)

    if k == None:
        q3 = f"UPDATE tbl_orders SET status = 'Packing' WHERE order_id = '{params['razorpay_order_id']}'"
        q4 = f"UPDATE tbl_all_order SET status = 'Packing' WHERE order_id = '{params['razorpay_order_id']}'"
        q5 = f"UPDATE user_notification SET notification = 'Order Placed' WHERE order_id = '{params['razorpay_order_id']}'"
        q6 = f"DELETE FROM tbl_cart WHERE user_id = '{id}'"

        try:
            cur.execute(q3)
            conn.commit()
        except Exception as e:
            print(e)
            conn.close()
            return message(400,e)

        try:
            cur.execute(q4)
            conn.commit()
        except Exception as e:
            print(e)
            conn.close()
            return message(400,e)

        try:
            cur.execute(q5)
            conn.commit()
        except Exception as e:
            print(e)
            conn.close()
            return message(400,e)

        try:
            cur.execute(q6)
            conn.commit()
        except Exception as e:
            print(e)
            conn.close()
            return message(400,e)

        conn.close()

        return message(200, "Payment verified and order placed")

    else :
        return message(400,"Payment verification failed")



    




    


