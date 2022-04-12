import json
import datetime
import uuid
from db import connectUserDb
from random import randint
from utility import validatePhone,message
import boto3

# sns = boto3.client('sns')

# def send_otp(otp,phone):
#     res = sns.publish(PhoneNumber = '+91'+phone, Message=f"Your OTP for Ration Pro account : {otp}\n 'Never share your otp'")
#     print(res)

def lambda_handler(event,context):
    print(event)
    params = json.loads(event['body'])
    
    
    try:
        phoneno = params['phoneno']
        
    except:
        return message(400,"Missing inputs")

    search_query = None
    
    if validatePhone(phoneno):
        search_query = "SELECT otp from tbl_user WHERE phone= '%s'" % phoneno
    else:
        return message(400,f"Invalid Input {phoneno}")

    conn = connectUserDb()
    cur = conn.cursor()
    id = None
    try:
        cur.execute(search_query)
        res = cur.fetchone()
    except :
        pass

    return{
            "statusCode": 200,
            "body": json.dumps(res),
        }
