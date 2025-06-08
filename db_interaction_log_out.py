from db_interaction_connection import get_connection

def view_delayed_flights_with_duration(format_table):
    """
    Displays flights that were delayed, including original and new departure times and delay duration.
    """
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                nf.flight_ID,
                nf.departure_date_time AS original_departure,
                df.departure_date_time AS delayed_departure,
                ROUND((JULIANDAY(df.departure_date_time) - JULIANDAY(nf.departure_date_time)) * 1440, 1) AS delay_minutes
            FROM FlightStatusLog nf
            JOIN FlightStatusLog df ON nf.flight_ID = df.flight_ID
            WHERE nf.status = 'NotDeparted' AND df.status = 'Delayed'
        """)

        rows = cur.fetchall()
        conn.close()

        headers = ["Flight ID", "Original Departure", "Delayed Departure", "Delay (min)"]
        if format_table:
            format_table(rows, headers)

    except Exception as e:
        print(f"Failed to retrieve delayed flight durations: {e}")

def view_average_delay_duration():
    """
    Calculates and displays the average delay time across all delayed flights.
    """
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                ROUND(AVG((JULIANDAY(df.departure_date_time) - JULIANDAY(nf.departure_date_time)) * 1440), 1) AS average_delay_minutes
            FROM FlightStatusLog nf
            JOIN FlightStatusLog df ON nf.flight_ID = df.flight_ID
            WHERE nf.status = 'NotDeparted' AND df.status = 'Delayed'
        """)

        result = cur.fetchone()
        conn.close()

        if result and result[0] is not None:
            print(f"Average delay across flights: {result[0]} minutes")
        else:
            print("No delayed flights found to calculate average.")

    except Exception as e:
        print(f"Failed to calculate average delay duration: {e}")