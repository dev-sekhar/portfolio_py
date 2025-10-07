def get_db_connection():
    import os
    import mysql.connector
    from mysql.connector import Error

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
