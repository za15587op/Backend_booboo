import psycopg2
from psycopg2.extras import RealDictCursor

def get_connection():
    try:
        DATABASE_URL = 'postgresql://booboo_user:Qx5ppaxRzA6LVwrucJHOEAL4FRxuXcAB@dpg-ctrlcsrtq21c738tsubg-a.singapore-postgres.render.com:5432/booboo'

        conn = psycopg2.connect(DATABASE_URL)
        print("Database connection successful!")
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None
    
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

conn = get_connection()
if conn:
    conn.close()