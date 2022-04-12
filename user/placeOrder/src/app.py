import json
import requests
import datetime
import razorpay
import uuid
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

    try :
        coupon = params['coupon']
        mode = params['mode']
    except Exception as e:
        print(e)
        return message(400,e)

    if mode == 'cod':
        payment_mode = "Cash on Delivery"
    else :
        payment_mode = "Online"

    conn1 = connectUserDb()
    cur1 = conn1.cursor()
    q = f"SELECT address from tbl_user WHERE id = '{id}'"
    try:
        cur1.execute(q)
        usr = cur1.fetchone()
        conn1.close()
        print(usr)
    except Exception as e:
        print(e)
        conn1.close()
        return message(400,e)


    details = None
    conn = connectProductDb()
    cur = conn.cursor()
    if len(coupon) > 0:
        query = f"SELECT * from tbl_coupon WHERE coupon = '{coupon}'"

        try:
            cur.execute(query)
            details = cur.fetchone()
            print(details)
        except Exception as e:
            print(e)
            conn.close()
            return message(400,e)

    url = "https://aetivopun1.execute-api.ap-south-1.amazonaws.com/Prod/user/viewCart"
    payload={}
    headers = {
    'authtoken': authToken
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    res = json.loads(response.text)
    print(res)

    totalcost = 0
    d1 = []
    d2 = []
    d3 = []
    discount = 0
    dis = 0

    now = datetime.datetime.now()

    for product in res:
        a = int(product['price'])
        b = int(product['quantity'])

        if len(coupon) > 0:
            if details['is_active'] == '1' and now <= details['valid_till'] and details['quantity']>0 :
                dis = int(max(details['pricelimit'],a*b)) * (int(details['discount']) / 100)
                discount = discount + dis
            else:
                msg = "Coupon invalid or expired"
                return message(400,msg)

        totalcost = (totalcost + a*b)
        d1.append(str(product['pdt_id']))
        d2.append(str(a*b - dis))
        d3.append(str(b))

    totalcost = totalcost - discount
    totalcost = totalcost * 100
    print("total cost =" + str(totalcost))

    if mode == 'Online':
        client = razorpay.Client(auth=(key_id, key_secret))
        DATA = {
                "amount": totalcost,
                "currency": "INR",
                "receipt": f"{id}",
                "notes": {}
            }
        print(DATA)  
        k = client.order.create(data=DATA)
        print(k)

        time_now = datetime.datetime.now()
        Q = f"INSERT INTO `tbl_all_order` (`user_id`, `total`, `order_id`, `create_date`, `status`) VALUES ('{id}', '{totalcost/100}', '{k['id']}', '{time_now}', 'Pending')"

        try:
            cur.execute(Q)
            conn.commit()
            print("done")
        except:
            conn.close()
            print("Error: unable to fetch data")
            return message(400,"Error: unable to fetch data")

        query2 = f"INSERT INTO tbl_orders (`user_id`,`order_id`,`status`,`pdt_id`,`quantity`,`payment_mode`,`address`,`create_date`, `total`) VALUES "
        
        count = 0
        for values in d1:
            query2 = query2 + f"('{id}', '{k['id']}', 'Pending','{d1[count]}','{d3[count]}','{payment_mode}','{usr['address']}','{time_now}', '{d2[count]}'), " 
            count = count + 1

        try:
            cur.execute(query2[:-2])
            conn.commit()
            print("done")
        except:
            conn.close()
            print("Error: unable to fetch data")
            return message(400,"Error: unable to fetch data")

        k['offer_id'] = str(k['offer_id'])
        conn.close()

        url2 = "https://c3wwmgv6y6.execute-api.ap-south-1.amazonaws.com/Prod/user/deleteCart"
        payload={}
        headers = {
        'authtoken': authToken
        }
        response = requests.request("POST", url2, headers=headers, data=payload)

        return {
            "statusCode": 200,
            "body":json.dumps(k)
        }
    else:

        order_id = str(uuid.uuid4())
        order_id = "order_" + order_id
        time_now = datetime.datetime.now()
        Q = f"INSERT INTO `tbl_all_order` (`user_id`, `total`, `order_id`, `create_date`, `status`) VALUES ('{id}', '{totalcost/100}', '{order_id}', '{time_now}', 'Packing')"

        try:
            cur.execute(Q)
            conn.commit()
            print("done")
        except:
            conn.close()
            print("Error: unable to fetch data")
            return message(400,"Error: unable to fetch data")

        query2 = f"INSERT INTO tbl_orders (`user_id`,`order_id`,`status`,`pdt_id`,`quantity`,`payment_mode`,`address`,`create_date`, `total`) VALUES "
        
        count = 0
        for values in d1:
            query2 = query2 + f"('{id}', '{order_id}', 'Packing','{d1[count]}','{d3[count]}','{payment_mode}','{usr['address']}','{time_now}', '{d2[count]}'), " 
            count = count + 1

        try:
            cur.execute(query2[:-2])
            conn.commit()
            print("done")
        except:
            conn.close()
            print("Error: unable to fetch data")
            return message(400,"Error: unable to fetch data")

        # k['offer_id'] = str(k['offer_id'])
        conn.close()

        r = {
            "id": f"'{order_id}'",
            "entity": "order",
            "amount": f"'{totalcost/100}'",
            "amount_paid": 0,
            "amount_due": f"'{totalcost/100}'",
            "currency": "INR",
            "receipt": f"{id}",
            "offer_id": "None",
            "status": "created",
            "attempts": 0,
            "notes": [],
            "created_at": 1647487349
        }

        url2 = "https://c3wwmgv6y6.execute-api.ap-south-1.amazonaws.com/Prod/user/deleteCart"
        payload={}
        headers = {
        'authtoken': authToken
        }
        response = requests.request("POST", url2, headers=headers, data=payload)

        return {
            "statusCode": 200,
            "body":json.dumps(r)
        }





    


