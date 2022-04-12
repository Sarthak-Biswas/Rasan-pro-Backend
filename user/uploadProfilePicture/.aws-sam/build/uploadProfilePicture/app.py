import json
import base64
import boto3
import botocore
import datetime
import uuid
from db import connectUserDb,connectProductDb
from utility import validateEmail,validatePhone,message,USERID,USERTYPE,validateToken,valid_uuid

def lambda_handler(event,context):
    try:
        authToken = event['headers']['authToken']
        # directory = event['headers']['directory']
        # type = event['headers']['type']
        # contenttype = event['headers']['Content']
        # print(authToken + " "+type+" "+contenttype)
    except:
        try:
            authToken = event['headers']['authtoken']
            # directory = event['headers']['directory']
            # type = event['headers']['type']
            # contenttype = event['headers']['Content']
            # print(authToken + " "+type+" "+contenttype)
        except:
            print("token not found")
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Token Not Found"}),
            }
    
    if not valid_uuid(authToken):
        return message(403,"Invalid Token")
    print(authToken)

    info = validateToken(authToken)
    role = info[USERTYPE]
    id = info[USERID]


    if role == -1 :
        print("Invalid User.")
        return message(403,"Invalid User.")

    s3 = boto3.client('s3')
    params = json.loads(event['body'])

    type = params['type']
    contenttype = params['Content']

    file = bytes(base64.b64decode(params['img']))
    now = datetime.datetime.now()

    conn = connectUserDb()
    cur = conn.cursor()

    directory = str(id)

    file_name = "user" + "/" + directory + "/" + now.strftime("%m.%d.%Y, %H:%M:%S") + "." + type
    print(file_name)

    bucket = 'ration-pro-files'
    key = file_name
    body = file

    upload = s3.put_object(Bucket=bucket, ACL = 'public-read', Key=key, Body=body, ContentType = contenttype)
    

    print(upload)

    url = "https://ration-pro-files.s3.ap-south-1.amazonaws.com/" + key

    
    query = f"UPDATE `tbl_user` SET picture = '{url}' WHERE id = '{id}'"

    
    try:
        cur.execute(query)
        conn.commit()
    except Exception as e:
        conn.close()
        return message(400,e)
    conn.close()

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'File uploaded',
            'url': url,
        })
    }






    




