import sqlite3
from faker import Faker
from datetime import date
from datetime import datetime, timedelta
import random

#Set Up
fake_gb = Faker('en_GB') #Use UK specific formatting for Pilot addresses
db_conn = sqlite3.connect("flight_management.db")
cursor = db_conn.cursor()

def generate_fake_pilots(n):
    for _ in range(n):
        #Generate name and DOB
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

        #Generate departure time based on status
        if status == 'NotDeparted':
            dep_dt = datetime.now() + timedelta(days=random.randint(1, 30), hours=random.randint(0, 23), minutes=random.randint(0, 59))

        elif status == 'Delayed':
            dep_dt = datetime.now() + timedelta(days=random.randint(1, 5), hours=random.randint(0, 23), minutes=random.randint(0, 59))

        elif status == 'Arrived':
            dep_dt = datetime.now() - timedelta(random.randint(0, 60), minutes=flight_time)

        elif status == 'OnRoute':
            # Departed already but flight is still ongoing
            end_time = datetime.now() + timedelta(minutes=random.randint(1, flight_time - 1))
            dep_dt = end_time - timedelta(minutes=flight_time)

        elif status == 'Cancelled':
            dep_dt = datetime.now() + timedelta(days=random.randint(-60, 60))

        else:
            dep_dt = datetime.now()  #Fallback
            print(f"WARNING: Unknown status '{status}' at flight {i+1}. Using current time as fallback for departure.")

        dep_str = dep_dt.strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute("""
            INSERT INTO Flights (personal_ID, destination_ID, arrival_destination_ID, departure_date_time, flight_time, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (pilot_id, departure_id, arrival_id, dep_str, flight_time, status))


def generate_status_logs():
# Fetch flights sorted by flight_ID to ensure chronological NotDeparted logs
    cursor.execute("SELECT flight_ID, status, departure_date_time, flight_time FROM Flights ORDER BY flight_ID ASC")
    flights = cursor.fetchall()

    all_log_entries = []  # Collect all logs from all flights before sorting and inserting

    # Global start time for logs, relative to the current context time (Thursday, June 5, 2025 6:45:18 PM BST)
    # This ensures NotDeparted logs for earlier FlightIDs are truly earlier.
    global_log_base_time = datetime(2025, 3, 1, 0, 0, 0) # Start logs from March 1, 2025
    last_not_departed_log_time_tracker = global_log_base_time

    delay_prob = 0.35 # Overall chance for a flight to experience a delay

    for flight in flights:
        flight_id, current_flight_status, scheduled_dep_str, flight_time_minutes = flight
        scheduled_dep_dt = datetime.strptime(scheduled_dep_str, '%Y-%m-%d %H:%M:%S')

        # --- 1. Generate "NotDeparted" log entry (first log for any flight) ---
        # Ensure NotDeparted logs are sequential by flight_ID
        log_time_not_departed = last_not_departed_log_time_tracker + timedelta(minutes=random.randint(5, 15)) # Small random increment
        last_not_departed_log_time_tracker = log_time_not_departed # Update tracker for next flight ID

        all_log_entries.append((
            flight_id,
            'NotDeparted',
            scheduled_dep_str, # Always original scheduled time for NotDeparted
            log_time_not_departed.strftime('%Y-%m-%d %H:%M:%S')
        ))

        # --- Determine actual departure time and potential delay ---
        actual_departure_dt = scheduled_dep_dt
        delay_occurred = False
        
        # Simulate a delay for relevant flight types based on probability
        if current_flight_status in ['Delayed', 'OnRoute', 'Arrived', 'Cancelled'] and random.random() < delay_prob:
            delay_minutes = random.randint(30, 240) # Delay duration (0.5 to 4 hours)
            actual_departure_dt = scheduled_dep_dt + timedelta(minutes=delay_minutes)
            delay_occurred = True

            # --- 2. Generate "Delayed" status log entry if a delay occurred ---
            # IMPORTANT: For 'Delayed' status, departure_date_time in the log is the NEW (delayed) time
            new_delayed_departure_str = actual_departure_dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Log time for when the delay was announced/logged
            log_time_delayed = log_time_not_departed + timedelta(hours=random.randint(1, 48))
            # Ensure delay log is before actual (delayed) departure if flight is 'OnRoute'/'Arrived'
            if current_flight_status in ['OnRoute', 'Arrived'] and log_time_delayed >= actual_departure_dt:
                log_time_delayed = actual_departure_dt - timedelta(minutes=random.randint(5, 20)) # Just before delayed departure
            # Ensure delay log is after NotDeparted for flights still 'Delayed' or 'Cancelled'
            elif log_time_delayed < log_time_not_departed: # Should mostly be handled by random.randint(1,48) but as safeguard
                 log_time_delayed = log_time_not_departed + timedelta(minutes=random.randint(5, 60))

            all_log_entries.append((
                flight_id,
                'Delayed',
                new_delayed_departure_str, # Specific requirement: NEW delayed time for 'Delayed' status
                log_time_delayed.strftime('%Y-%m-%d %H:%M:%S')
            ))

        # --- Generate subsequent logs based on the flight's final status ---
        # For OnRoute, Arrived, Cancelled statuses, departure_date_time in log is always the ORIGINAL scheduled time
        
        if current_flight_status == 'OnRoute':
            # This flight has departed and is currently in transit
            # Log time for when the flight went 'OnRoute' (i.e., departed)
            log_time_on_route = actual_departure_dt + timedelta(minutes=random.randint(5, 30))
            all_log_entries.append((
                flight_id,
                'OnRoute',
                scheduled_dep_str, # ORIGINAL scheduled time
                log_time_on_route.strftime('%Y-%m-%d %H:%M:%S')
            ))

        elif current_flight_status == 'Arrived':
            # This flight has departed and arrived
            # Log time for when the flight went 'OnRoute' (i.e., departed)
            log_time_on_route = actual_departure_dt + timedelta(minutes=random.randint(5, 30))
            all_log_entries.append((
                flight_id,
                'OnRoute',
                scheduled_dep_str, # ORIGINAL scheduled time
                log_time_on_route.strftime('%Y-%m-%d %H:%M:%S')
            ))

            # Log time for when the flight 'Arrived'
            actual_arrival_dt = actual_departure_dt + timedelta(minutes=flight_time_minutes + random.randint(-15, 30)) # Add slight variance to flight time
            log_time_arrived = actual_arrival_dt + timedelta(minutes=random.randint(5, 30)) # Logged shortly after actual arrival
            all_log_entries.append((
                flight_id,
                'Arrived',
                scheduled_dep_str, # ORIGINAL scheduled time
                log_time_arrived.strftime('%Y-%m-%d %H:%M:%S')
            ))

        elif current_flight_status == 'Cancelled':
            # Flight was cancelled
            # Log time for cancellation. Can be before or after scheduled departure.
            # Ensure it's after the NotDeparted log and after Delayed log if applicable
            log_time_cancelled = scheduled_dep_dt + timedelta(minutes=random.randint(-120, 120)) # Within 2 hours of scheduled dep
            
            # Find the latest log time generated for this flight so far to ensure chronological order
            latest_prev_log_time = log_time_not_departed
            if delay_occurred:
                # If there was a delayed log, cancellation must be after it
                latest_prev_log_time = max(latest_prev_log_time, log_time_delayed)
            
            if log_time_cancelled < latest_prev_log_time:
                log_time_cancelled = latest_prev_log_time + timedelta(minutes=random.randint(10, 60))

            all_log_entries.append((
                flight_id,
                'Cancelled',
                scheduled_dep_str, # ORIGINAL scheduled time
                log_time_cancelled.strftime('%Y-%m-%d %H:%M:%S')
            ))


    # --- Sort all log entries by log_date_time globally before inserting ---
    sorted_log_entries = sorted(all_log_entries, key=lambda x: datetime.strptime(x[3], '%Y-%m-%d %H:%M:%S'))

    print("\n--- Inserting FlightStatusLog Entries ---")
    for flight_id, status, dep_time_str, log_time_str in sorted_log_entries:
        cursor.execute("""
            INSERT INTO FlightStatusLog (flight_ID, status, departure_date_time, log_date_time)
            VALUES (?, ?, ?, ?)
        """, (flight_id, status, dep_time_str, log_time_str))

try:
    # All functions calls here
        generate_fake_pilots(10)
        generate_fake_destinations (10)
        generate_fake_flights (10)
        generate_status_logs ()

        db_conn.commit()

        print("\nDatabase population successful and changes committed.")

except Exception as e:
        print(f"An error occurred: {e}")
        db_conn.rollback() # Rollback changes on error

finally:
        db_conn.close()
        print("Database connection closed.")

