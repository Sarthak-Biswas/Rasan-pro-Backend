import json
import datetime
from re import search
from unicodedata import name
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
    print(params)
    try:
        category = params['category']
        sort = params['sort']
    except Exception as e:
        print(e)
        return message(400,"Invalid input")
    name = params['name']

    searchQ = f"SELECT * FROM tbl_pdt"

    if not name == "":
        searchQ = searchQ + f" WHERE name == '{name}'"
        text = "AND"
    else:
        text = "WHERE"


    if not category == 0:
        searchQ = searchQ + f" {text} category = '{category}'"

    if sort == 1:
        searchQ = searchQ + f" ORDER BY price ASC"
    if sort == 2:
        searchQ = searchQ + f" ORDER BY price DESC"
    if sort == 3:
        searchQ = searchQ + f" ORDER BY date_added ASC"
    if sort == 4:
        searchQ = searchQ + f" ORDER BY date_added DESC"
    if sort == 5:
        searchQ = searchQ + f" ORDER BY name ASC"
    if sort == 6:
        searchQ = searchQ + f" ORDER BY likes DESC"

    print(searchQ)

    conn = connectProductDb()
    cur = conn.cursor()
    try:
        cur.execute(searchQ)
        res = cur.fetchall()
    except Exception as e:
        print(e)
        conn.close()
        return message(400,e)
    
    conn.close()

    return {
        "statusCode": 200,
        "body":json.dumps(res, indent=4, sort_keys=True, default=str)
    }