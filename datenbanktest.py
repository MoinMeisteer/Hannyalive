import mysql.connector
from mysql.connector import Error

host_name = "localhost"
user_name = "admin"
user_password = "Awgraben12345678@"
db_name = "hannyatest"

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

def check_table_structure():
    connection = create_connection()
    query = "DESCRIBE songs"
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    for row in result:
        print(row)
    cursor.close()
    connection.close()

check_table_structure()