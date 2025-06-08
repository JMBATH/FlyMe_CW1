# FlyMe_CW1
Database and Cloud (CM500292) Coursework1 Github repository

Main.py 
Covers all logic related to menu's, output to terminal, menu views and function calling.
All functions are recorded in seperate files, named after what parts of database these functions generally interact with.
Main.py calls required functions, passes some of required input/formatting, and handles output to terminal

setup_db.py
Running this file set's up SQL database, making all required tables, and associated restrictions/attributes
Review this file for SQL syntax for tables
Database file is called flight_management.db

populate_sample_data_db.py
File that fills in sample data into the database. Adds 10 entries to each database, exclduing log, which has 23 to capture all possible iterations
Pilot and Destination table populated with fake data from Faker library
Flights and FlightStatusLog filled with specific generated data. This is because of the low number of samples needed, and complexity of logic related to log table did not warrant time spent generating complex code.