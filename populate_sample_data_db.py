import sqlite3
from faker import Faker
from datetime import date
from datetime import datetime, timedelta
import random

#Set Up
fake_gb = Faker('en_GB') # Use UK specific formatting for Pilot addresses
db_conn = sqlite3.connect("flight_management.db")
cursor = db_conn.cursor()

def generate_fake_pilots(n):
    for _ in range(n):
        #Generate name and DOB
        first = fake_gb.first_name()
        last = fake_gb.last_name()
        dob_obj = fake_gb.date_of_birth(minimum_age=21, maximum_age=65)
        dob_str = dob_obj.strftime('%Y-%m-%d')

        # Generate UK-style address fields
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

        #Construct unique email using name and ID
        email = f"{first.lower()}.{last.lower()}.{personal_id}"

        #Update email in record
        cursor.execute("""
            UPDATE Pilots SET email = ? WHERE personal_ID = ?
        """, (email, personal_id))


def generate_fake_destinations(n):
    for _ in range(n):
        country = fake_gb.country()
        name = fake_gb.city()
        cost = round(random.uniform(50, 1500), 2)
        timezone = random.randint(-12, 14)

        cursor.execute("""
            INSERT INTO Destinations (country, name, cost, timezone)
            VALUES (?, ?, ?, ?)""",
            (country, name, cost, timezone))



def generate_fake_flights(n):
    #Fetch foreign keys from Pilots and Destination table
    cursor.execute("SELECT personal_ID FROM Pilots")
    pilot_ids = [row[0] for row in cursor.fetchall()]

    if len(pilot_ids) == 0:
        print("ERROR: No pilots found. Cannot generate flights.")
        return

    cursor.execute("SELECT destination_ID FROM Destinations")
    dest_ids = [row[0] for row in cursor.fetchall()]

    if len(dest_ids) < 2:
        print("ERROR: Need at least 2 distinct destinations to generate flights (departure != arrival).")
        return

    status_plan = (
        ['NotDeparted'] * int(0.15 * n) +
        ['Delayed']     * int(0.15 * n) +
        ['OnRoute']     * int(0.10 * n) +
        ['Arrived']     * int(0.40 * n) +
        ['Cancelled']   * (n - int(0.15 * n + 0.15 * n + 0.10 * n + 0.40 * n))  # Remainder
    )
    
    random.shuffle(status_plan) #Shuffle to prevent all status types being grouped

    for i, status in enumerate(status_plan):
        pilot_id = random.choice(pilot_ids)
        departure_id = random.choice(dest_ids)
        arrival_id = random.choice([d for d in dest_ids if d != departure_id])
        flight_time = random.randint(30, 480) #Random time in minutes

        # Generate departure time based on status
        if status == 'NotDeparted':
            dep_dt = datetime.now() + timedelta(days=random.randint(1, 30), hours=random.randint(0, 23), minutes=random.randint(0, 59))

        elif status == 'Delayed':
            dep_dt = datetime.now() + timedelta(days=random.randint(1, 5), hours=random.randint(0, 23), minutes=random.randint(0, 59))

        elif status == 'Arrived':
            dep_dt = datetime.now() - timedelta(minutes=flight_time)

        elif status == 'OnRoute':
            # Departed already but flight is still ongoing
            end_time = datetime.now() + timedelta(minutes=random.randint(1, flight_time - 1))
            dep_dt = end_time - timedelta(minutes=flight_time)

        elif status == 'Cancelled':
            dep_dt = datetime.now() + timedelta(days=random.randint(-15, 15))

        else:
            dep_dt = datetime.now()  #Fallback
            print(f"WARNING: Unknown status '{status}' at flight {i+1}. Using current time as fallback for departure.")

        dep_str = dep_dt.strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute("""
            INSERT INTO Flights (personal_ID, destination_ID, arrival_destination_ID, departure_date_time, flight_time, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (pilot_id, departure_id, arrival_id, dep_str, flight_time, status))


def generate_status_logs():
    # Fetch all flights and their current status, departure time, and flight duration
    cursor.execute("SELECT flight_ID, status, departure_date_time, flight_time FROM Flights")
    flights = cursor.fetchall()

    log_entries = []  # Collect all logs before inserting

    # Define chance of delayed status per flight type
    delay_probs = {
        'OnRoute': 0.3,
        'Arrived': 0.4,
        'Cancelled': 0.2
    }

    for flight in flights:
        flight_id, current_status, departure_str, flight_time = flight
        dep_dt = datetime.strptime(departure_str, '%Y-%m-%d %H:%M:%S')
        delay_occurred = False

        # 1. Always log "NotDeparted" at some point before departure
        creation_time = dep_dt - timedelta(days=random.randint(2, 10))
        log_entries.append((flight_id, 'NotDeparted', dep_dt.strftime('%Y-%m-%d %H:%M:%S'), creation_time.strftime('%Y-%m-%d %H:%M:%S')))

        # 2. Possibly log "Delayed" if within configured probability
        if current_status in delay_probs and random.random() < delay_probs[current_status]:
            delay_occurred = True
            original_dep = dep_dt - timedelta(minutes=random.randint(30, 180))
            delay_log_time = creation_time + timedelta(hours=random.randint(1, 48))
            log_entries.append((flight_id, 'Delayed', original_dep.strftime('%Y-%m-%d %H:%M:%S'), delay_log_time.strftime('%Y-%m-%d %H:%M:%S')))

        # 3. Now add other logs depending on final status
        if current_status == 'Delayed':
            pass  # Already handled above

        elif current_status == 'OnRoute':
            actual_dep = dep_dt if not delay_occurred else original_dep + timedelta(minutes=random.randint(30, 180))
            log_entries.append((flight_id, 'OnRoute', dep_dt.strftime('%Y-%m-%d %H:%M:%S'), actual_dep.strftime('%Y-%m-%d %H:%M:%S')))

        elif current_status == 'Arrived':
            actual_dep = dep_dt if not delay_occurred else dep_dt - timedelta(minutes=random.randint(30, 180))
            arrival_time = actual_dep + timedelta(minutes=flight_time)
            log_entries.append((flight_id, 'OnRoute', actual_dep.strftime('%Y-%m-%d %H:%M:%S'), actual_dep.strftime('%Y-%m-%d %H:%M:%S')))
            log_entries.append((flight_id, 'Arrived', actual_dep.strftime('%Y-%m-%d %H:%M:%S'), arrival_time.strftime('%Y-%m-%d %H:%M:%S')))

        elif current_status == 'Cancelled':
            cancel_time = dep_dt + timedelta(minutes=random.randint(-60, 60))
            log_entries.append((flight_id, 'Cancelled', dep_dt.strftime('%Y-%m-%d %H:%M:%S'), cancel_time.strftime('%Y-%m-%d %H:%M:%S')))

    # Sort logs by log_date_time and insert into DB
    for flight_id, status, dep_time, log_time in sorted(log_entries, key=lambda x: x[3]):
        cursor.execute("""
            INSERT INTO FlightStatusLog (flight_ID, status, departure_date_time, log_date_time)
            VALUES (?, ?, ?, ?)
        """, (flight_id, status, dep_time, log_time))

if __name__ == "__main__":
    try:
    # All functions calls here
        generate_fake_pilots(10)
        generate_fake_destinations (10)
        generate_fake_flights (10)
        generate_status_logs ()

        db_conn.commit()

    except Exception as e:
        print(f"An error occurred: {e}")
        db_conn.rollback() # Rollback changes on error

    finally:
        db_conn.close()
        print("Database connection closed.")

