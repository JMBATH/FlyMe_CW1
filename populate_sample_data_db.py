import sqlite3
from faker import Faker
from datetime import date
from datetime import datetime, timedelta
import random

#Set Up
fake_gb = Faker('en_GB') #Use UK specific formatting for Pilot addresses
db_conn = sqlite3.connect("flight_management.db")
cursor = db_conn.cursor()

def generate_fake_pilots(n, cursor, db_conn):
    '''
    Function to generate fake pilot information, primarily using Faker Library
    '''
    for _ in range(n):
        #Generate name and DOB from Faker function with restrictions on age
        first = fake_gb.first_name()
        last = fake_gb.last_name()
        dob_obj = fake_gb.date_of_birth(minimum_age=21, maximum_age=65)
        dob_str = dob_obj.strftime('%Y-%m-%d')

        #Generate UK-style address fields
        postcode = fake_gb.postcode()[:8]  #Constraint of 8 added to meet database CHECK requirements
        city = fake_gb.city()
        street = fake_gb.street_address()

        #Insert all fake data, excluding email as personal_ID first required
        cursor.execute("""
            INSERT INTO Pilots (first_name, surname, DOB, email, postcode, city, street)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (first, last, dob_str, 'placeholder', postcode, city, street))

        #Fetch auto-generated ID
        personal_id = cursor.lastrowid

        #Construct unique email using name and ID {first_name.lastname.ID number}
        email = f"{first.lower()}.{last.lower()}.{personal_id}"

        #Update email in record
        cursor.execute("""
            UPDATE Pilots SET email = ? WHERE personal_ID = ?
        """, (email, personal_id))


def generate_fake_destinations(n, cursor, db_conn):
    '''
    Function to generate fake destination information, primarily using Faker Library or random values within specified range
    '''
    for _ in range(n):
        country = fake_gb.country() #Faker country
        name = fake_gb.city() #Faker city
        cost = round(random.uniform(50, 1500), 2) #Cost between specified range to 2.d.p
        timezone = random.randint(-12, 14) #Random timezone range to realsitic range

        #SQL INSERT statement
        cursor.execute("""
            INSERT INTO Destinations (country, name, cost, timezone)
            VALUES (?, ?, ?, ?)""",
            (country, name, cost, timezone))



def generate_fake_flights(cursor, db_conn):
    '''
    Function to generate fake Flights information, all generated by hand due to complexity of FlightLogStatus and small sample size required
    '''
    flight_data = [
        #personal_ID, destination_ID, arrival_destination_ID, departure_date_time (string), flight_time (minutes), status
        (8, 1, 7, '2025-01-05 14:30:00', 60, 'Arrived'),
        (2, 4, 10, '2025-06-04 09:55:00', 480, 'Arrived'),
        (6, 8, 6, '2025-03-04 16:55:00', 30, 'Arrived'),
        (2, 6, 4, '2025-04-03 15:30:00', 65, 'Cancelled'),
        (1, 9, 1, '2025-06-08 15:30:00', 34, 'Delayed'),
        (5, 9, 10, '2025-06-06 10:53:00', 345, 'OnRoute'),
        (9, 10, 5, '2025-05-13 16:20:00', 250, 'Arrived'),
        (3, 3, 2, '2025-08-30 20:35:00', 185, 'NotDeparted'),
        (7, 5, 1, '2025-05-13 16:20:00', 209, 'Arrived'), 
        (10, 7, 1, '2025-10-19 19:30:00', 401, 'NotDeparted'),
    ]
    #SQL INSERT statement
    insert_sql = '''
        INSERT INTO Flights (
            personal_ID,
            destination_ID,
            arrival_destination_ID,
            departure_date_time,
            flight_time,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?)
        '''
    try:
        cursor.executemany(insert_sql, flight_data)
    except sqlite3.IntegrityError as e:
        print(f"A database integrity error occurred during flight insertion: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during flight insertion: {e}")

def generate_status_logs(cursor, db_conn):
    '''
    Function to generate fake FlightsStatusLog information, all generated by hand due to complexity of FlightLogStatus, randomness required within specifi range and small sample size required
    '''
    log_data = [
        # flight_ID, status, departure_date_time, log_date_time
        (1, 'NotDeparted', '2025-01-05 14:30:00', '2024-05-12 09:36:00'),
        (2, 'NotDeparted', '2025-06-04 01:45:00', '2024-05-12 09:50:00'),
        (1, 'OnRoute', '2025-01-05 14:30:00', '2025-01-05 14:30:00'),
        (1, 'Arrived', '2025-01-05 14:30:00', '2025-01-05 15:30:00'),
        (3, 'NotDeparted', '2025-03-04 16:25:00', '2025-01-08 10:39:42'),
        (4, 'NotDeparted', '2025-04-03 13:46:00', '2025-01-08 10:56:22'),
        (5, 'NotDeparted', '2025-06-07 15:30:00', '2025-01-08 12:55:44'),
        (4, 'Delayed', '2025-04-03 15:30:00', '2025-01-22 12:55:11'),
        (6, 'NotDeparted', '2025-06-06 10:53:00', '2025-01-24 18:08:33'),
        (7, 'NotDeparted', '2025-05-13 11:26:00', '2025-02-12 14:24:00'),
        (4, 'Cancelled', '2025-04-03 15:30:00', '2025-02-23 03:02:48'),
        (3, 'OnRoute', '2025-03-04 16:25:00', '2025-03-04 16:25:00'), 
        (5, 'Delayed', '2025-06-08 15:30:00', '2025-03-04 16:28:11'), 
        (3, 'Arrived', '2025-03-04 16:25:00', '2025-03-04 16:55:00'), 
        (8, 'NotDeparted', '2025-08-30 20:35:00', '2025-05-19 11:01:30'),
        (9, 'NotDeparted', '2025-05-14 20:49:00', '2025-05-19 11:01:39'),
        (10, 'NotDeparted', '2025-10-19 19:30:00', '2025-05-19 11:25:24'),
        (7, 'OnRoute', '2025-05-13 11:26:00', '2025-05-13 11:26:00'),
        (7, 'Arrived', '2025-05-13 16:20:00', '2025-05-13 16:20:00'), 
        (9, 'Delayed', '2025-05-14 21:33:00', '2025-05-14 09:30:01'), 
        (9, 'OnRoute', '2025-05-14 21:33:00', '2025-05-14 21:33:00'), 
        (9, 'Arrived', '2025-05-15 02:02:00', '2025-05-15 02:02:00'), 
        (2, 'Delayed', '2025-06-04 01:55:00', '2025-06-04 01:15:00'), 
        (2, 'OnRoute', '2025-06-04 01:55:00', '2025-06-04 01:55:00'), 
        (2, 'Arrived', '2025-06-04 09:55:00', '2025-06-04 09:55:00'), 
        (6, 'OnRoute', '2025-06-06 10:53:00', '2025-06-06 10:53:00'), 
    ]

    #Insert SQL statement
    insert_sql = '''
        INSERT INTO FlightStatusLog (
            flight_ID,
            status,
            departure_date_time,
            log_date_time
        )
        VALUES (?, ?, ?, ?)
        '''
    try:
        cursor.executemany(insert_sql, log_data)
        db_conn.commit() #Commit changes to the database
    
    #Error handling
    except sqlite3.IntegrityError as e:
        print(f"A database integrity error occurred during flight status log insertion: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during flight status log insertion: {e}")

try:
    # All functions calls here
        generate_fake_pilots(10, cursor, db_conn)
        generate_fake_destinations (10, cursor, db_conn)
        generate_fake_flights(cursor, db_conn)
        generate_status_logs (cursor, db_conn)

        db_conn.commit()

        print("\nDatabase population successful and changes committed.")

except Exception as e:
        print(f"An error occurred: {e}")
        db_conn.rollback() # Rollback changes on error

finally:
        db_conn.close()
        print("Database connection closed.")

