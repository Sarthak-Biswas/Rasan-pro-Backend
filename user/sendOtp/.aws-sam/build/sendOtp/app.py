import json
import datetime
import uuid
from db import connectUserDb
from random import randint
from utility import validatePhone,message
import boto3
import urllib.request
import urllib.parse
from secret import apikey, sender

# sns = boto3.client('sns')

def send_otp(message,phone):
    data =  urllib.parse.urlencode({'apikey': apikey, 'numbers': phone,
        'message' : message, 'sender': sender})
    data = data.encode('utf-8')
    request = urllib.request.Request("https://api.textlocal.in/send/?")
    f = urllib.request.urlopen(request, data)
    fr = f.read()
    print(fr)
    return(fr)

def lambda_handler(event,context):
    print(event)
    params = json.loads(event['body'])
    
    
    try:
        phoneno = params['phoneno']
        
    except:
        return message(400,"Missing inputs")

    search_query = None
    
    if validatePhone(phoneno):
        search_query = "SELECT id from tbl_user WHERE phone= '%s'" % phoneno
    else:
        return message(400,f"Invalid Input {phoneno}")

    conn = connectUserDb()
    cur = conn.cursor()
    id = None
    try:
        cur.execute(search_query)
        res = cur.fetchone()
        id = res["id"]
    except :
        pass
    
    otp =randint(100000,999999)
    hash_id = str(uuid.uuid4())
    expiry = datetime.datetime.now() + datetime.timedelta(minutes = 2)
    now = datetime.datetime.now()
    update_Q = f"UPDATE `tbl_user` SET `otp` = '{otp}', `token` = '{hash_id}', `validity`='{expiry}' WHERE (`id` = '{id}')"
    insert_Q = f"INSERT INTO `tbl_user` (`phone`, `otp`, `validity`, `role`, `token`,`created_on`) VALUES ('{phoneno}', '{otp}',  '{expiry}', '2', '{hash_id}','{now}')"
    msg = f"Your Login OTP for Rasan Pro is {otp}. Please do not share this with anyone."
    if (id != None):
        try:
            send_otp(msg,str(phoneno))
            cur.execute(update_Q)
            conn.commit()
        except Exception as e:
            conn.close()
            return message(400,e)
    else:
        try:
            send_otp(msg,str(phoneno))
            cur.execute(insert_Q)
            conn.commit()
        except Exception as e :
            conn.close()
            return message(400,e)
    conn.close()


    return{
            "statusCode": 200,
            "body": json.dumps({
                    "success": True,
                    "authtoken": hash_id,
                }),
        }
