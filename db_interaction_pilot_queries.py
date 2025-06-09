##File contains logic associated with inputting/retrievign data from Pilots table using SQL commands

from db_interaction_connection import get_connection
#Import function to start connection to database

def delete_pilot_by_id(pilot_id):
    '''
    Function to delete entry fromn Pilot table, by personal_ID
    Note SQL restrictions prevent delete if personal_ID assigned to flight, however restriction also enforced in Python below
    '''
    try:
        conn = get_connection()
        cur = conn.cursor()

        #Check if pilot is assigned to any flights
        cur.execute("SELECT flight_ID FROM Flights WHERE personal_ID = ?", (pilot_id,))
        flight = cur.fetchone()

        if flight:
            print(f"Cannot delete pilot: assigned to Flight ID {flight[0]}")
            return

        #If pilot not assigned, delete
        cur.execute("DELETE FROM Pilots WHERE personal_ID = ?", (pilot_id,))
        conn.commit()
        print(f"Pilot ID {pilot_id} deleted successfully.")

    except Exception as e:
        print(f"Error while deleting pilot: {e}")
    finally:
        conn.close()

def view_all_pilots(format_table):
    '''
    View all entries in Pilot table along with all associated meta-data
    '''
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM Pilots")#SQL statements, view all entries in Pilot table
        rows = cur.fetchall()
        conn.close()

        if not rows: #Error handling if table empty
            print("No pilot records found.")
            return []

        headers = ["Pilot ID", "First Name", "Surname", "DOB", "Email"]
        formatted_rows = []

        for row in rows: #Adds @flyme.com to end of email, remove unnessecary characters from database storage
            row = list(row)
            row[4] = f"{row[4]}@flyme.com" if "@" not in row[4] else row[4]
            formatted_rows.append(row)

        if format_table: #Pulls formatting table requirements from Main.py
            format_table(formatted_rows, headers)
        
        return formatted_rows
    
    except Exception as e:
        print(f"Failed to retrieve pilot information: {e}")
        return []

def add_new_pilot():
    '''
    Add new pilot, entering all required info
    '''
    try: #Requests info from User
        print("\n--- Add New Pilot ---")
        first_name = input("Enter first name: ")
        surname = input("Enter surname: ")
        dob = input("Enter date of birth (YYYY-MM-DD): ")
        email = input("Enter email: ")

        conn = get_connection()
        cur = conn.cursor() #SQL Insert statement
        cur.execute("""
            INSERT INTO Pilots (first_name, surname, DOB, email)
            VALUES (?, ?, ?, ?)
        """, (first_name, surname, dob, email))
        conn.commit()
        conn.close()

        print("New pilot added successfully.")

    except Exception as e:
        print(f"Failed to add new pilot: {e}")

def reassign_pilot(flight_id):
    '''
    Re-assign a pilot id on a specified flight
    '''
    try:
        new_pilot_id = input("Enter new Pilot ID to assign to this flight: ")

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE Flights SET personal_ID = ? WHERE flight_ID = ?", (new_pilot_id, flight_id))
        conn.commit()
        conn.close()

        print(f"Flight ID {flight_id} now assigned to Pilot ID {new_pilot_id}.")

    except Exception as e:
        print(f"Failed to reassign pilot: {e}")

def count_total_pilots():
    '''
    Count number of entries in Pilot table
    '''
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM Pilots")
        result = cur.fetchone()
        conn.close()

        count = result[0] if result else 0
        print("-" * 100)
        print(f"\nTotal number of active pilots: {count}")
        return count

    except Exception as e:
        print(f"Failed to count pilots: {e}")
        return 0


def _get_flights_for_pilot(pilot_id, status_filter=None):
    try:
        conn = get_connection()
        cur = conn.cursor()

        #SQL code to retrieves flights assigned to a pilot with destination info and optional status filtering, calculating arrival time.
        base_sql = """
            SELECT
                p.personal_ID,
                p.first_name,
                f.flight_ID,
                f.departure_date_time,
                d1.destination_ID,
                d1.country,
                f.arrival_destination_ID,
                d2.country,
                DATETIME(f.departure_date_time, '+' || f.flight_time || ' minutes')
            FROM Pilots p
            JOIN Flights f ON p.personal_ID = f.personal_ID
            JOIN Destinations d1 ON f.destination_ID = d1.destination_ID
            JOIN Destinations d2 ON f.arrival_destination_ID = d2.destination_ID
            WHERE p.personal_ID = ?
        """
        params = [pilot_id]
        if status_filter:
            base_sql += " AND f.status != ?"
            params.append(status_filter)

        cur.execute(base_sql, tuple(params))
        rows = cur.fetchall()
        conn.close()

        return rows

    except Exception as e:
        print(f"Failed to retrieve flight data for pilot: {e}")
        return []

def view_all_flights_for_pilot(pilot_id, format_table):
    '''
    View Flights that a specific pilot is assigned too
    '''
    
    rows = _get_flights_for_pilot(pilot_id)
    headers = [
        "Pilot ID", "First Name", "Flight ID", "Departure Time",
        "Departure ID", "Departure Country", "Arrival ID", "Arrival Country", "Arrival Time"
    ]

    if format_table:
        format_table(rows, headers)


def view_active_flights_for_pilot(pilot_id, format_table):
    '''
    View Flights that a specific pilot is assigned too, removing any entries with Status "Assigned" (Upcoming/Ongoing Flights)
    '''
    rows = _get_flights_for_pilot(pilot_id, status_filter="Arrived")
    headers = [
        "Pilot ID", "First Name", "Flight ID", "Departure Time",
        "Departure ID", "Departure Country", "Arrival ID", "Arrival Country", "Arrival Time"
    ]

    if format_table:
        format_table(rows, headers)