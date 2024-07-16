import mysql.connector
from mysql.connector import Error
from mysql.connector import pooling
import logging
from cogs.config import logger, setup_logger

logging.basicConfig(level=logging.INFO)
db_logger = setup_logger('db')

host_name = "localhost"
user_name = "admin"
user_password = "Awgraben12345678@"
db_name = "hannyalive"

def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection

connection = create_connection()

def create_table():
    connection = create_connection()
    query = """
    CREATE TABLE IF NOT EXISTS songs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        url VARCHAR(2083) NOT NULL,
        title VARCHAR(255) NOT NULL,
        duration INT
    );
    """
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()


create_table()




def insert_song(url, title, duration):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        query = "INSERT INTO songs (url, title, duration) VALUES (%s, %s, %s)"
        cursor.execute(query, (url, title, duration))
        connection.commit()
        logging.info("Song erfolgreich in die Datenbank eingefügt.")
    except Error as e:
        logging.error(f"Fehler beim Einfügen des Songs: {e}")
    finally:
        cursor.close()
        connection.close()

def get_song_history():
    connection = create_connection()
    query = "SELECT title, duration FROM songs"
    cursor = connection.cursor()
    cursor.execute(query)
    return cursor.fetchall()

def get_all_songs():
    connection = create_connection()
    query = "SELECT url, title, duration, play_count FROM songs"
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()
    except Error as e:
        logging.error(f"Fehler beim Abrufen aller Songs: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_song_by_url(url):
    connection = create_connection()
    query = "SELECT * FROM songs WHERE url = %s"
    try:
        cursor = connection.cursor()
        cursor.execute(query, (url,))
        return cursor.fetchone()  # Return the first result
    except Error as e:
        logging.error(f"Error retrieving song by URL: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def increment_play_count(song_id):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        query = "UPDATE songs SET play_count = play_count + 1 WHERE id = %s"
        cursor.execute(query, (song_id,))
        connection.commit()
        logging.info(f"Abspielanzahl für Song mit ID {song_id} aktualisiert.")
    except Error as e:
        logging.error(f"Fehler beim Aktualisieren der Abspielanzahl: {e}")
    finally:
        cursor.close()
        connection.close()
