import sqlite3
from datetime import datetime
from db_interaction_connection import get_connection
#Import function to start connection to database

from db_interaction_log import (
    log_flight_status
) #Import function to log status change in FlightStatusLog

##----------------------------------------------------------------------------
#Following functions used to retrieve data from Flight table, based upon specified criteria

#Gets Flights from database by their status. Also handles retrieving all flights
def get_flights_by_status(status):
    conn = get_connection()
    cur = conn.cursor()

    if status.lower() == "all":
        sql = "SELECT * FROM Flights"
        cur.execute(sql)
    else:
        sql = "SELECT * FROM Flights WHERE status = ?"
        cur.execute(sql, (status,))

    results = cur.fetchall()
    conn.close()
    return results

#Retrieves Flights by ID of arrival destination
def get_flights_by_arrival_id(arrival_id):
    conn = get_connection()
    cur = conn.cursor()
    sql = "SELECT * FROM Flights WHERE arrival_destination_ID = ?"
    cur.execute(sql, (arrival_id,))
    results = cur.fetchall()
    conn.close()
    return results#

#Retrieves Flights by ID of destination
def get_flights_by_destination_id(dest_id):
    conn = get_connection()
    cur = conn.cursor()
    sql = "SELECT * FROM Flights WHERE destination_ID = ?"
    cur.execute(sql, (dest_id,))
    results = cur.fetchall()
    conn.close()
    return results

#Retrieves Flights by country name of leaving location
def get_flights_by_destination_country(country):
    conn = get_connection()
    cur = conn.cursor()
    sql = """
        SELECT Flights.*
        FROM Flights
        JOIN destinations ON Flights.destination_ID = destinations.destination_ID
        WHERE destinations.country = ?
    """
    cur.execute(sql, (country,))
    results = cur.fetchall()
    conn.close()
    return results

#Retrieves Flights by country name of destination
def get_flights_by_arrival_country(country):
    conn = get_connection()
    cur = conn.cursor()
    sql = """
        SELECT Flights.*
        FROM Flights
        JOIN destinations ON Flights.arrival_destination_ID = destinations.destination_ID
        WHERE destinations.country = ?
    """
    cur.execute(sql, (country,))
    results = cur.fetchall()
    conn.close()
    return results

#Retrieves Flights by departure date
def get_flights_by_date(date_str):
    conn = get_connection()
    cur = conn.cursor()
    sql = """
        SELECT *
        FROM Flights
        WHERE DATE(departure_date_time) = ?
    """
    cur.execute(sql, (date_str,))
    results = cur.fetchall()
    conn.close()
    return results

##----------------------------------------------------------------------------

def add_new_flight():
    '''
    Function to handle adding a new Flight to database, requesting relevant table fields from user
    ''' 
    try:
        print("\n--- Add New Flight ---")
        personal_id = int(input("Enter Pilot's Personal ID: "))
        destination_id = int(input("Enter Departure Destination ID: "))
        arrival_id = int(input("Enter Arrival Destination ID: "))
        departure_str = input("Enter Departure Date and Time (YYYY-MM-DD HH:MM:SS): ")
        datetime.strptime(departure_str, "%Y-%m-%d %H:%M:%S")  #Validate date time format
        flight_time = int(input("Enter Flight Time in minutes: "))
        status = "NotDeparted" #Automatically logged status as NotDeparted

        conn = get_connection()
        cur = conn.cursor()
        #SQL insert statment
        sql = """
            INSERT INTO Flights (personal_ID, destination_ID, arrival_destination_ID, departure_date_time, flight_time, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        cur.execute(sql, (personal_id, destination_id, arrival_id, departure_str, flight_time, status))
        conn.commit()

        flight_id = cur.lastrowid  #Get the auto-generated Flight ID
        conn.close()

        log_flight_status(flight_id, status, departure_str) #Passes relevant information to FlightStatusLog to "log" status change (initial entry) of flight
        print("Flight added and logged successfully.")

    except ValueError: #Error handling
        print("Invalid input. Please check your values and date format.")
    except Exception as e:
        print(f"Failed to add new flight: {e}")

##-------------------------------------------------
#Following functions used to update status of entry into "Flight" table. Use of two "helper functions" to prevent code re-use
#Helper Functions: update_flight_status_helper and prompt_and_update_departure_time
#If Flight "Cancelled", then on selection of option in Main, passes "Cancelled to "update_flight_status_helper" for appropriate logging
#For other options("Arrived", "OnRoute", and "Delayed"), "upate_flight_function" prompts user for entry, and passes to "update_flight_status_helper". If "DElayed" option selected, then "prompt_and_update_departure_time" run to prompt and update departure time
#All changes to status are are logged, including new deparure time when delayed

#Called when "Deleting" a Flight (changing status to "Cancelled"). Passes "Cancelled" status to "update_flight_status_helper"
def cancel_flight_by_id(flight_id):
    update_flight_status_helper(flight_id, "Cancelled")

#Checks input status, and if appropriate, passes to "update_flight_status_helper"
def update_flight_status(flight_id):
    valid_statuses = ["Arrived", "OnRoute", "Delayed"]
    
    while True:
        new_status = input("Enter new status (choose from Arrived, OnRoute, Delayed): ").strip()

        if new_status == "Cancelled":
            print("Status update to 'Cancelled' is not permitted using this function.")
            return
        elif new_status in valid_statuses:
            update_flight_status_helper(flight_id, new_status)
            break
        else:
            print(f"'{new_status}' is not a valid status. Please enter Arrived, OnRoute, or Delayed.")
    
    new_status = input("Enter new status (excluding 'Cancelled' or 'OnRoute'): ")

#If run (when new status is "Delayed") will promtp user to input new departure time
def prompt_and_update_departure_time(cur, flight_id):

    new_departure = input("Enter new departure time (YYYY-MM-DD HH:MM:SS): ")
    try:
        datetime.strptime(new_departure, "%Y-%m-%d %H:%M:%S")
        cur.execute("UPDATE Flights SET departure_date_time = ? WHERE flight_ID = ?", (new_departure, flight_id))
        print("Departure time updated.")
        return new_departure
    except ValueError:
        print("Invalid datetime format. Departure time not updated.")
        return None

#Runs SQL lines to update Flights table with new status
def update_flight_status_helper(flight_id, new_status):
    try:
        conn = get_connection()
        cur = conn.cursor()

        #Check if flight exists and get departure date
        cur.execute("SELECT departure_date_time FROM Flights WHERE flight_ID = ?", (flight_id,))
        result = cur.fetchone()

        if result is None:
            print("No flight found with that ID.")
            return

        departure_time = result[0]

        #If delayed, prompt for and update the departure time
        if new_status == "Delayed":
            updated_time = prompt_and_update_departure_time(cur, flight_id)
            if updated_time:
                departure_time = updated_time

        #Update status
        cur.execute("UPDATE Flights SET status = ? WHERE flight_ID = ?", (new_status, flight_id))
        conn.commit()
        conn.close()

        #Log the update
        log_flight_status(flight_id, new_status, departure_time)
        print(f"Flight ID {flight_id} status updated to '{new_status}'.")

    except Exception as e:
        print(f"Failed to update flight status: {e}")
