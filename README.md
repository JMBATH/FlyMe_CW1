# FlyMe_CW1
Database and Cloud (CM500292) Coursework1 Github repository

## Purpose
Program is a command-line interface used to interact with a flight management database.
It is built using Python and SQLite and demonstrates relational database management, user interaction, and SQL query integration through Python.

- The system avoids direct SQL errors by pre-checking foreign key conditions (e.g., pilots assigned to flights).
- Python handles menu flow and input validation, while SQL performs most of the data work.
- Logging is handled separately to show best practice in separation of concerns.

## Database design
The system uses a relational database implemented in SQLite. Their are 4 related tables include as outlined below:

- **Pilots**: Holds details on available pilots and required information
personal_ID (PK), first_name, surname, DOB, email, postcode, city, street
- **Flights**: Holds details of all flights, both past, current and future
flight_ID (PK), personal_ID (fk)(Pilot assigned to flight), destination_ID (fk), arrival_destination_ID (fk, destination_ID), flight time, status
- **Destinations**: Holds details of all available locations for arrival/departure of flights
destination_ID (PK), country, name, timezone (difference to UTC), cost
- **FlightStatusLog**: Tracks flight status changes with timestamps for when the change occurred and the change in departure time. Used to track if a flight is Delayed and for how long. Tracks historical status of all Flights
log_ID (PK), flight_ID (fk), status, departure datetime, log datetime

Foreign key relationships are used between Flights - Pilots, Flights - Destinations and Flights - FlightStatusLog.

## Core Functionality
Brief summary of core functions/interactions with database
- Add, update, and delete pilots, destinations, and flights
- Reassign pilots to flights
- Log and track flight status updates (NotDeparted, Delayed, etc.)
- Calculate delay duration and average delay duration using SQL `JULIANDAY()`
- View flights filtered by destination, pilot, or status
- Summary queries:
  - Destinations ordered by cost
  - Unassigned destinations (via `LEFT JOIN`)
  - Average delay across flights

## Menu Navigation

The CLI is structured with a main menu which lead to nested menus:
- **Main Menu** Navigates to:
  - Flight Views
  - Flight Manegement
  - Pilot Management
  - Pilot Schelduling
  - Destination Management
  - Flight Log Queries

Each submenu presents numbered options that call query and logic functions based on user input.

## File Structure

- `main.py`: Command Line Display logic, function calling and menu navigation
- `db_interaction_connection.py`: Database connection function
- `db_interaction_flight_queries.py`: SQL queries for managing flights
- `db_interaction_log.py`: Functions for tracking and reporting flight status changes (function called when Flight table updated to log as appropriate)
- `db_interaction_pilot.py`: SQL queries for managing pilots
- `db_interaction_destination.py`: SQL queries for managing destinations
- `db_interaction_log_out.py`: Functions for calculating and view "Delayed" flights
- `flight_management.db`: SQLite database

## SQL Techniques Demonstrated

- `JOIN`, `LEFT JOIN`, and multi-table relationships
- `GROUP BY` and `AVG()` for aggregation
- `CHECK`, `DEFAULT`, and `FOREIGN KEY` constraints
- `ORDER BY`, `LIMIT`, and subquery logic
- Time calculations using `JULIANDAY()`