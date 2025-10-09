import os
import mysql.connector
from mysql.connector import Error
from sqlalchemy import create_engine

def get_db_connection():
    host = os.getenv('DB_HOST', '127.0.0.1')
    port = int(os.getenv('DB_PORT', 3306))
    database = os.getenv('DB_NAME')
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')

    return mysql.connector.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password,
        auth_plugin='mysql_native_password',
        connection_timeout=5
    )

def get_db_engine():
    host = os.getenv('DB_HOST', '127.0.0.1')
    port = int(os.getenv('DB_PORT', 3306))
    database = os.getenv('DB_NAME')
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')

    if not all([host, database, user, password]):
        raise ValueError("Database connection details are not fully configured in environment variables.")

    conn_str = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
    return create_engine(conn_str)
