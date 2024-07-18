import time
import requests
import mysql.connector
import schedule
from datetime import datetime
from math_app import len_of_two_points
from decimal import Decimal

def connectSQL():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="musicalMiles"
    )

def func():
    try:
        # Connect to the database
        connection = connectSQL()
        cursor = connection.cursor()
        client_id = "18cd51e587a34060b5bfa3a32363441f"
        query = "SELECT id, access_token, miles, latitude, longitude FROM user_profiles"
        cursor.execute(query)
        results = cursor.fetchall()
        
        for row in results:
            ids, access_token, miles, latitude, longitude = row
            
            response = requests.get(
                "https://api.spotify.com/v1/me/player/currently-playing",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if response.status_code != 200:
                print(f"Failed to fetch currently playing track for user {ids}")
                continue
            
            json = response.json()
            
            if json.get("is_playing"):
                try:
                    artist = json["item"]["artists"][0]["name"]
                    print(artist)
                    if not artist:
                        continue
                    
                    q2 = "SELECT latitude, longitude FROM music_groups WHERE Name = %s"
                    cursor.execute(q2, (artist,))
                    result = cursor.fetchone()
                    
                    if result is None:
                        print(f"Artist {artist} not found in music_groups")
                        continue
                    
                    new_lat, new_lon = result
                    print(new_lat, new_lon)
                    
                    distance = len_of_two_points(
                        float(latitude), float(longitude),
                        float(new_lat), float(new_lon)
                    )

                    # Convert miles to float for addition, then back to Decimal
                    new_miles = float(miles) + distance
                    miles = Decimal(new_miles)
                    
                    update_query = """
                        UPDATE user_profiles 
                        SET miles = %s, latitude = %s, longitude = %s 
                        WHERE id = %s
                    """
                    new_values = (miles, new_lat, new_lon, ids)
                    cursor.execute(update_query, new_values)
                    connection.commit()
                    print(f"Updated user {ids} with new miles and coordinates.")
                
                except Exception as e:
                    print(f"Error processing artist data for user {ids}: {e}")
                    continue

    except Exception as e:
        print(f"Database connection or query error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
        time.sleep(60)
        func()
func()

