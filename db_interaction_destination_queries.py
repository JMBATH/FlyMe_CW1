from db_interaction_connection import get_connection
#Import function to start connection to database

def view_all_destinations(format_table):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM Destinations")
        rows = cur.fetchall()
        conn.close()

        headers = ["Destination ID", "Country", "Name", "Cost", "Timezone (+/- UTC)"]
        if format_table:
            format_table(rows, headers)

    except Exception as e:
        print(f"Failed to retrieve destinations: {e}")

def delete_destination_by_id(destination_id):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT flight_ID FROM Flights
            WHERE destination_ID = ? OR arrival_destination_ID = ?
        """, (destination_id, destination_id))
        result = cur.fetchone()

        if result:
            print(f"Cannot delete: destination is assigned to Flight ID {result[0]}")
            return

        cur.execute("DELETE FROM Destinations WHERE destination_ID = ?", (destination_id,))
        conn.commit()
        print("Destination deleted.\n")

    except Exception as e:
        print(f"Error deleting destination: {e}")
    finally:
        conn.close()

def update_destination(destination_id):
    try:
        country = input("Enter new country: ")
        name = input("Enter new destination name: ")
        cost = float(input("Enter new cost: "))
        timezone = int(input("Enter new timezone (-12 to 14 to UTC): "))

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE Destinations
            SET country = ?, name = ?, cost = ?, timezone = ?
            WHERE destination_ID = ?
        """, (country, name, cost, timezone, destination_id))
        conn.commit()
        conn.close()

        print("Destination updated successfully.")

    except Exception as e:
        print(f"Failed to update destination: {e}")

def find_flights_by_destination(destination_id, format_table):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT f.flight_ID, d.destination_ID, d.name
            FROM Flights f
            JOIN Destinations d
            ON f.destination_ID = d.destination_ID OR f.arrival_destination_ID = d.destination_ID
            WHERE d.destination_ID = ?
        """, (destination_id,))

        rows = cur.fetchall()
        conn.close()

        headers = ["Flight ID", "Destination ID", "Destination Name"]
        if format_table:
            format_table(rows, headers)

    except Exception as e:
        print(f"Failed to find flights for destination: {e}")

def add_new_destination():
    try:
        print("\n--- Add New Destination ---")
        country = input("Enter country: ")
        name = input("Enter destination name: ")
        cost = float(input("Enter cost (must be >= 0): "))
        timezone = int(input("Enter timezone (-12 to 14): "))

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO Destinations (country, name, cost, timezone)
            VALUES (?, ?, ?, ?)
        """, (country, name, cost, timezone))
        conn.commit()
        conn.close()

        print("Destination added successfully.")

    except Exception as e:
        print(f"Failed to add new destination: {e}")


def view_destinations_by_cost(format_table):
    """
    Displays all destinations ordered by cost (descending).
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM Destinations ORDER BY cost DESC")
        rows = cur.fetchall()
        conn.close()

        headers = ["Destination ID", "Country", "Name", "Cost", "Timezone"]
        if format_table:
            format_table(rows, headers)

    except Exception as e:
        print(f"Failed to retrieve destinations by cost: {e}")

def view_unassigned_destinations(format_table):
    """
    Displays destinations not assigned to any flights.
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT d.*
            FROM Destinations d
            LEFT JOIN Flights f
            ON d.destination_ID = f.destination_ID OR d.destination_ID = f.arrival_destination_ID
            WHERE f.flight_ID IS NULL
        """)
        rows = cur.fetchall()
        conn.close()

        headers = ["Destination ID", "Country", "Name", "Cost", "Timezone"]
        if format_table:
            format_table(rows, headers)

    except Exception as e:
        print(f"Failed to retrieve unassigned destinations: {e}")