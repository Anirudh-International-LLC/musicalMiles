import time
import requests
import mysql.connector
import schedule
from datetime import datetime

def connectSQL():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="musicalMiles"
    )

def refresh_tokens():
    try:
        # Connect to the database
        connection = connectSQL()
        cursor = connection.cursor()

        client_id = "18cd51e587a34060b5bfa3a32363441f"

        # Get the id, access_token, and refresh_token columns from the database
        query = "SELECT id, access_token, request_token FROM user_profiles"
        cursor.execute(query)
        results = cursor.fetchall()

        for row in results:
            ids, access_token, refresh_token = row

            # Send the refresh_token to Spotify and get new access_token
            response = requests.post("https://accounts.spotify.com/api/token", data={
                'grant_type': "refresh_token",
                'refresh_token': refresh_token,
                'client_id': client_id
            }, headers={'Content-Type': "application/x-www-form-urlencoded"})

            if response.status_code == 200:
                json = response.json()
                new_access_token = json['access_token']
                new_refresh_token = json.get('refresh_token', refresh_token)  # Use the old refresh token if new one is not provided

                # Update the access_token and refresh_token columns in the database
                update_query = "UPDATE user_profiles SET access_token = %s, request_token = %s WHERE id = %s"
                new_values = (new_access_token, new_refresh_token, ids)
                cursor.execute(update_query, new_values)
                connection.commit()
            else:
                print(f"Failed to refresh token for user {ids}: {response.json()}")

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
        time.sleep(1800)
        refresh_tokens()

refresh_tokens()
