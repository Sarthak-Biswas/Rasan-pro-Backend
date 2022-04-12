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
    print(params)
    try:
        pdt_id = params['product_id']
        name = params["name"]
        price = int(params["price"])
        mrp = int(params["MRP"])
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

    

    if category_name == "None":
        updateQ = f"UPDATE tbl_pdt SET name = '{name}', price = '{price}', description = '{description}', stock = '{stock}', primary_image = '{primary_image}', category_name ='{category_name}', category = 0, MRP = '{mrp}' WHERE id = '{pdt_id}'"  
    else:
        Q = f"SELECT id from tbl_category WHERE category_name = '{category_name}'"

        try:
            cur.execute(Q)
            res = cur.fetchone()
            # conn.close()
        except Exception as e:
            print(e)
            return message(400,e)
        updateQ = f"UPDATE tbl_pdt SET name = '{name}', price = '{price}', description = '{description}', stock = '{stock}', primary_image = '{primary_image}', category_name ='{category_name}', category = '{res['id']}', MRP = '{mrp}' WHERE id = '{pdt_id}'"


    print(updateQ)

    # images and videos are list of urls each element would be stored in individual rows.
    selectQ = "SELECT id FROM tbl_pdt ORDER BY id DESC LIMIT 1;"

    # conn = connectProductDb()
    # cur = conn.cursor()
    try:
        cur.execute(updateQ)
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
        "body":json.dumps("product edited.")
    }