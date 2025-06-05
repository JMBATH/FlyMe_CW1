#setup_dy.py
#Code to create SQLite database and all required table for flight management system
#Tables only created if do not already exist


import sqlite3 #Import the sqlite3 module needed to interact with SQL data/make tables

#Function to make tables and database
def create_database():
    
    #Connect to SQLite database file (or create if doesn't exist). File called 'flight_management.db'
    db_conn = sqlite3.connect('flight_management.db')

    #Create table to store personal details for pilots
    db_conn.execute('''
    CREATE TABLE IF NOT EXISTS Pilots (
        personal_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        surname TEXT NOT NULL,
        dob DATE NOT NULL CHECK (dob <= DATE('now')),
        email TEXT NOT NULL UNIQUE,
        postcode TEXT NOT NULL CHECK (LENGTH(postcode) <=8),
        city TEXT NOT NULL,
        street TEXT NOT NULL
        );
    ''')

    #Create the table to store flight destinations and costs
    db_conn.execute('''
    CREATE TABLE IF NOT EXISTS Destinations (
        destination_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        country TEXT NOT NULL,
        name TEXT NOT NULL,
        cost REAL NOT NULL CHECK(cost >=0),
        timezone INTEGER NOT NULL CHECK(timezone between -23 AND 23)
        );
    ''')

    #Create flight table to store information on individual schelduled flights
    db_conn.execute(''' 
    CREATE TABLE IF NOT EXISTS Flights (
        flight_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        personal_ID INTEGER NOT NULL,
        destination_ID INTEGER NOT NULL,
        arrival_destination_ID INTEGER NOT NULL,
        departure_date_time DATETIME NOT NULL CHECK(departure_date_time >=DATETIME('now')),
        flight_time INTEGER NOT NULL CHECK(flight_time >=0),
        status TEXT NOT NULL CHECK(status IN('NotDeparted', 'Delayed', 'OnRoute', 'Arrived', 'Cancelled')),
        FOREIGN KEY (personal_ID) REFERENCES Pilots(personal_ID) ON DELETE RESTRICT,
        FOREIGN KEY (destination_ID) REFERENCES Destinations(destination_ID) ON DELETE RESTRICT,
        FOREIGN KEY (arrival_destination_ID) REFERENCES Destinations(destination_ID) ON DELETE RESTRICT
        );
    ''')

    #Create FlightStatusLog table to track changes with flight status
    db_conn.execute(''' 
    CREATE TABLE IF NOT EXISTS FlightStatusLog (
        log_ID INTEGER PRIMARY KEY AUTOINCREMENT,             
        flight_ID INTEGER NOT NULL,
        status TEXT CHECK(status IN('NotDeparted', 'Delayed', 'OnRoute', 'Arrived', 'Cancelled')),
        departure_date_time DATETIME NOT NULL,
        log_date_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (flight_ID) REFERENCES Flights(flight_ID) ON DELETE RESTRICT
        );
    ''')

    #Save changes to database
    db_conn.commit()

    #Close the database connection
    db_conn.close()

    print("Databases successfully created")

    #Entry point: Only run this fucntion if this script is executed directly
if __name__ == "__main__":
    create_database()
