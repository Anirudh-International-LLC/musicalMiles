from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
from urllib.parse import urlencode
import mysql.connector

def connectSQL():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root1234",
        database="musicalMiles"
    )


app = Flask(__name__)
CORS(app)

@app.route("/api/token", methods=['POST'])
def token():
    data = request.get_json()
    a, u, ids = get_access(data)
    if a:
        return jsonify({"status" : "success", "user" : u, "id" : ids}), 200
    else:
        return jsonify({"status" : "failure"}), 400


def get_access(data):
    mydb = connectSQL()
    cursor = mydb.cursor()
    try:
        authorization_code = data.get('grant_type')
        code = data.get('code')
        redirect_uri = data.get('redirect_uri')
        client_id = "18cd51e587a34060b5bfa3a32363441f"
        code_verifier = data.get('code_verifier')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        print(latitude)
        print(longitude)
        response = requests.post("https://accounts.spotify.com/api/token", data = {
    'grant_type': authorization_code,
    'code': code,
    'redirect_uri': redirect_uri,
    'client_id': client_id,
    'code_verifier': code_verifier
}

                                                                         , headers = {'Content-Type' : "application/x-www-form-urlencoded"})
        json = response.json()
        a_c = json["access_token"]
        r_f = json['refresh_token']
        r2 = requests.get("https://api.spotify.com/v1/me", headers = {"Authorization": f"Bearer {a_c}"})
        j2 = r2.json()
        email = j2["email"]
        ids = j2["id"]
        print(ids)
        name = j2["display_name"]
        pfp = j2["images"][1]["url"]
        search_query = "SELECT * FROM user_profiles WHERE id = %s"
        cursor.execute(search_query, (ids,))
        result = cursor.fetchone()

        if result:
            update_query = """
                UPDATE user_profiles
                SET access_token = %s, request_token = %s
                WHERE id = %s
            """
            cursor.execute(update_query, (a_c, r_f, ids))
            mydb.commit()
            return True, "Existing", ids

        else:
            insert_query = """
                INSERT INTO user_profiles (id, email, name, photo_url, latitude, longitude,  request_token, access_token, miles)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (ids, email, name, pfp, latitude, longitude, r_f, a_c, 0))
            mydb.commit()
            return True, "New", ids
    except:
        return False, "We went on wrong side", "exception"
    

@app.route("/api/deleteAcc", methods=['POST'])
def deleteAcc():
    mydb = connectSQL()
    cursor = mydb.cursor()
    data = request.get_json()
    ids = data.get("AccountId")
    delete_query = "DELETE FROM user_profiles WHERE id = %s"
    cursor.execute(delete_query, (ids,))
    mydb.commit()
    return {}, 200


@app.route("/api/getMiles", methods=['GET'])
def getMiles():
    mydb = connectSQL()
    cursor = mydb.cursor()
    data = request.args.get("AccountId")
    print(data)
    if data:
        cursor.execute('SELECT miles, name, photo_url, date_of_create FROM user_profiles WHERE id = %s', (data,))
        row = cursor.fetchone()
        print(row[0])
    else:
        print("INTRUDER HELP")

    return {"miles":row[0], "name":row[1], "photo_url":row[2], "date_of_create":row[3]}, 200

if __name__ == "__main__":
    app.run(port = 8000)
