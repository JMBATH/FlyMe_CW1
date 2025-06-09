##File handles logic associated with transferring data to FlightStatusLog from Flight table, when a "Status" is updated

from db_interaction_connection import get_connection
#Import function to start connection to database
from datetime import datetime

#Inserts a log entry into FlightStatusLog, when a flights status is updated or flight made
def log_flight_status(flight_id, status, departure_datetime):
    try:
        conn = get_connection()
        cur = conn.cursor()
        sql = """
            INSERT INTO FlightStatusLog (flight_ID, status, departure_date_time, log_date_time)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """
        cur.execute(sql, (flight_id, status, departure_datetime))
        conn.commit()
    except Exception as e:
        print(f"Failed to log flight status: {e}")
    finally:
        conn.close()
