import json
import datetime
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

    if role != 0 :
        print("Admin-only")
        return message(403,"Admin only.")

    params = json.loads(event['body'])
    print(params)
    try:
        name = params["name"]
        price = int(params["price"])
        mrp = int(params["MRP"])
        # images = params["images"]
        description = params["description"]
        stock = int(params["stock"])
        primary_image = params["primary_image"] 
        category_name = params["category_name"]
    except Exception as e:
        print(e)
        return message(400,"Invalid input")

    res = None
    conn = connectProductDb()
    cur = conn.cursor()
    now = datetime.datetime.now()

    if category_name == "None":
        insertQ = f"INSERT INTO `tbl_pdt` (`name`, `price`, `description`, `stock`,`primary_image`, `category_name`, `category`, `likes`, `MRP`) VALUES ('{name}', '{price}', '{description}', '{stock}','{primary_image}', '{category_name}', '0', '0', '{mrp}');"  
    else:
        Q = f"SELECT id from tbl_category WHERE category_name = '{category_name}'"

        try:
            cur.execute(Q)
            res = cur.fetchone()
            # conn.close()
        except Exception as e:
            print(e)
            return message(400,e)
        insertQ = f"INSERT INTO `tbl_pdt` (`name`, `price`, `description`, `stock`,`primary_image`, `category_name`, `category`, `likes`, `MRP`) VALUES ('{name}', '{price}', '{description}', '{stock}','{primary_image}', '{category_name}', '{res['id']}', '0', '{mrp}');"


    print(insertQ)

    # images and videos are list of urls each element would be stored in individual rows.
    selectQ = "SELECT id FROM tbl_pdt ORDER BY id DESC LIMIT 1;"

    # conn = connectProductDb()
    # cur = conn.cursor()
    try:
        cur.execute(insertQ)
        conn.commit()
        print("25%")
        cur.execute(selectQ)
        res2 = cur.fetchone()
        pdt_id = res2["id"]
        print("50%")
    except Exception as e :
        print(e)
        # conn.close()
        return message(400, e)
    
    # if( len(images)) > 0: 

    #     insertQ2 = "INSERT INTO pdt_image (`pdt_id`,`url`) VALUES "
    #     for image in images:
    #         insertQ2 = insertQ2 + f"('{pdt_id}','{image}'),"

    #     insertQ2 = insertQ2[:-1]
    #     print(insertQ2)


    #     try:
    #         cur.execute(insertQ2)
    #         conn.commit()
    #     except Exception as e: 
    #         print(e)
    #         conn.close()
    #         return message(400,e)

    conn.close()

    print("product added")
    return {
        "statusCode": 200,
        "body":json.dumps("product added.")
    }