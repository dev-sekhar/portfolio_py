import mysql.connector
from mysql.connector import Error


def cleanup_database(host, database, user, password):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host,
            port=3306,
            database='portfolio',
            user='root',
            password='root'
        )
        if connection.is_connected():
            print("Connected to MySQL database")

        cursor = connection.cursor()

        # Disable foreign key checks to allow truncating both tables
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute("TRUNCATE TABLE stock_prices")
        cursor.execute("TRUNCATE TABLE tickers")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        connection.commit()
        print("Database cleanup completed: 'stock_prices' and 'tickers' tables have been cleared.")

    except Error as e:
        print(f"Error during database cleanup: {e}")

    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")


if __name__ == "__main__":
    # Configure your MySQL credentials here
    cleanup_database(host='127.0.0.1', database='portfolio',
                     user='root', password='root')
