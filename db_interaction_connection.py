import sqlite3

#Function to connect to database. Function called across code, and can be simply editted here if database location changes
def get_connection():
    return sqlite3.connect("flight_management.db")