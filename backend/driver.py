import asyncio
import aiohttp
import mysql.connector
from datetime import datetime
from math_app import len_of_two_points
from decimal import Decimal

async def connectSQL():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root1234",
        database="musicalMiles"
    )

async def fetch_currently_playing(session, access_token):
    url = "https://api.spotify.com/v1/me/player/currently-playing"
    headers = {"Authorization": f"Bearer {access_token}"}
    async with session.get(url, headers=headers) as response:
        if response.status != 200:
            return None
        return await response.json()

async def update_miles():
    while True:
        connection = None
        cursor = None
        try:
            connection = await connectSQL()
            cursor = connection.cursor()
            query = "SELECT id, access_token, miles, latitude, longitude FROM user_profiles"
            cursor.execute(query)
            results = cursor.fetchall()

            async with aiohttp.ClientSession() as session:
                for row in results:
                    ids, access_token, miles, latitude, longitude = row

                    json = await fetch_currently_playing(session, access_token)
                    if not json or not json.get("is_playing"):
                        print(f"Failed to fetch currently playing track for user {ids}")
                        continue

                    try:
                        artist = json["item"]["artists"][0]["name"]
                        if not artist:
                            continue

                        q2 = "SELECT latitude, longitude FROM music_groups WHERE Name = %s"
                        cursor.execute(q2, (artist,))
                        result = cursor.fetchone()

                        if result is None:
                            print(f"Artist {artist} not found in music_groups")
                            continue

                        new_lat, new_lon = result
                        distance = len_of_two_points(
                            float(latitude), float(longitude),
                            float(new_lat), float(new_lon)
                        )

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
                    finally:
                        cursor.fetchall()  # Ensure all results are fetched to avoid unread result errors

        except mysql.connector.Error as err:
            print(f"Database connection or query error: {err}")
        except Exception as e:
            print(f"Unexpected error: {e}")
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

        await asyncio.sleep(60)  # Run this task every minute

async def refresh_tokens():
    while True:
        connection = None
        cursor = None
        try:
            connection = await connectSQL()
            cursor = connection.cursor()
            client_id = "18cd51e587a34060b5bfa3a32363441f"
            query = "SELECT id, access_token, request_token FROM user_profiles"
            cursor.execute(query)
            results = cursor.fetchall()

            async with aiohttp.ClientSession() as session:
                for row in results:
                    ids, access_token, refresh_token = row

                    response = await session.post("https://accounts.spotify.com/api/token", data={
                        'grant_type': "refresh_token",
                        'refresh_token': refresh_token,
                        'client_id': client_id
                    }, headers={'Content-Type': "application/x-www-form-urlencoded"})

                    if response.status == 200:
                        json = await response.json()
                        new_access_token = json['access_token']
                        new_refresh_token = json.get('refresh_token', refresh_token)

                        update_query = "UPDATE user_profiles SET access_token = %s, request_token = %s WHERE id = %s"
                        new_values = (new_access_token, new_refresh_token, ids)
                        cursor.execute(update_query, new_values)
                        connection.commit()
                    else:
                        print(f"Failed to refresh token for user {ids}: {await response.json()}")

        except mysql.connector.Error as err:
            print(f"Database error: {err}")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            if cursor:
                cursor.fetchall()  # Ensure all results are fetched to avoid unread result errors
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

        await asyncio.sleep(1800)  # Run this task every 30 minutes

async def main():
    await asyncio.gather(
        update_miles(),
        refresh_tokens()
    )

if __name__ == "__main__":
    asyncio.run(main())
