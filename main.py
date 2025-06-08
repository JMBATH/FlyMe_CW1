from datetime import datetime

#---------------------------------------------------------------------------------------------------------------------------------
#Importing functions from each relevant file to be called in Main when selected from menu options

#Calling functions related to queries from Flight table
from db_interaction_flight_queries import (
    get_flights_by_status,
    get_flights_by_arrival_id,
    get_flights_by_destination_id,
    get_flights_by_destination_country,
    get_flights_by_arrival_country,
    get_flights_by_date,
    add_new_flight,
    cancel_flight_by_id,
    update_flight_status,
)

#Calling functions related to queries from Pilot table
from db_interaction_pilot_queries import (
    delete_pilot_by_id,
    view_all_pilots,
    add_new_pilot,
    count_total_pilots,
    reassign_pilot,
    view_all_flights_for_pilot,
    view_active_flights_for_pilot,
)

#Calling functions related to queries from Destination table
from db_interaction_destination_queries import (
    view_all_destinations,
    delete_destination_by_id,
    update_destination,
    find_flights_by_destination,
    add_new_destination,
    view_destinations_by_cost,
    view_unassigned_destinations,
)

#Calling functions related to queries from FlightStatusLog table
from db_interaction_log_out import (
    view_delayed_flights_with_duration,
    view_average_delay_duration,
)

#---------------------------------------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------------------------------------
#Functions related to different menu views, and sub menu views shown in Terminal Window
def show_menu():
    '''
    Main menu used to select appropriate sub-menu's  
    '''

    print("\nHello, Welcome to")
    print("===== FlyMe Flight Management System =====")
    print("1. View Flights")
    print("2. Manage Flights (Add, Delete or Update Status)")
    print("3. View and Update Pilot Details")
    print("4. Manage Pilot Scheldule")
    print("5. View and Manage Locations")
    print("6. View Delays")
    print("7. Exit\n")

def show_flight_menu():
    '''
    Sub-menu used to show Flights from different criteria 
    '''

    print("\n--- View Flights ---")
    print("1. View All Flights")
    print("2. Flights by Status")
    print("3. Flights by Destination ID")
    print("4. Flights by Destination Country")
    print("5. Flights by Departure ID")
    print("6. Flights by Departure Country")
    print("7. Flights by Date")
    print("8. Back to Main Menu\n")

def show_flight_update_menu():
    '''
    Sub-menu used to update and add Flights
    '''
    
    print("\n--- Update Flights ---")
    print("1. Add Flights")
    print("2. Cancel Flight")
    print("3. Update Flight Status")
    print("4. Back to Main Menu\n")

def show_pilot_manage_menu():
    '''
    Sub-menu used to update, view and add Pilots
    '''
    print("\n--- Update and View Pilots ---")
    print("1. Add Pilot")
    print("2. Delete Pilot")
    print("3. View Pilots")
    print("4. Number of Active Pilots")
    print("5. Back to Main Menu\n")

def show_pilot_scheldule_menu():
    '''
    Sub-menu used to view Pilots scheldules (relationship between Pilots and Flights table)
    '''
    
    print("\n--- Manage Pilots Scheldule---")
    print("1. Re-assign Pilot")
    print("2. Pilot Scheldule and History")
    print("3. Pilots Scheldule")
    print("4. Back to Main Menu\n")

def show_destination_manage_menu():
    '''
    Sub-menu used to update, view and add Destinations
    Also handles more complex views, like sorting destination by cost or if no flights assigned
    '''

    print("\n--- Update and View Locations ---")
    print("1. View all Locations")
    print("2. Delete Location")
    print("3. Add Location")
    print("4. Add Location")
    print("5. See Flights Assigned to Location")
    print("6. See Location Cost, Sort By Cost")
    print("7. View Destinations with No Assigned Flights")
    print("8. Back to Main Menu\n")

def show_delay_manage_menu():
    '''
    Sub-menu used to view information related to delays
    '''

    print("\n--- Delay Information ---")
    print("1. Show Delayed Flights")
    print("2. Average Time of Delay")
    print("3. Back to Main Menu\n")

#---------------------------------------------------------------------------------------------------------------------------------
#Function related to table formating
def format_table(rows, headers):
    col_widths = [max(len(str(cell)) for cell in col) for col in zip(*([headers] + rows))]
    row_format = " | ".join("{:<" + str(width) + "}" for width in col_widths)

    print("\n" + row_format.format(*headers))
    print("-" * (sum(col_widths) + 3 * (len(headers) - 1)))
    for row in rows:
        print(row_format.format(*row))

#---------------------------------------------------------------------------------------------------------------------------------
#Main Function
#Handles User Input, menu/sub-menu display and relevent Function calling

def main():
    while True:
        show_menu() #Main menu which leads to sub-menu's
        choice = input("Select an option: ")

        if choice == "1": #Choice 1, View Flight Info, gives access to submenu
            while True:
                show_flight_menu()
                sub_choice = input("Select a flight view option: ")

                if sub_choice == "1": #View all flights
                    flights = get_flights_by_status("all") #Calls gets_flights_by_status but passes "all" which displays all data
                    headers = ["Flight ID", "Personal ID", "Destination ID", "Arrival Destination ID", "Departure Time", "Flight Time", "Status"]
                    format_table(flights, headers)
                    input("\nPress Enter to return to the flight menu...")

                elif sub_choice == "2": #Displays Flights of specified Status
                    status = input("Enter flight status (e.g., Arrived, Cancelled): ")
                    flights = get_flights_by_status(status)
                    headers = ["Flight ID", "Personal ID", "Destination ID", "Arrival Destination ID", "Departure Time", "Flight Time", "Status"]
                    format_table(flights, headers) #Calls table for formatting
                    input("\nPress Enter to return to the flight menu...")
                
                elif sub_choice == "3": #Displays flights going to sepcified Destination (from ID)
                    dest_ID = input("Enter Destination Country ID: ")
                    flights = get_flights_by_destination_id(dest_ID)
                    headers = ["Flight ID", "Personal ID", "Destination ID", "Arrival Destination ID", "Departure Time", "Flight Time", "Status"]
                    format_table(flights, headers)
                    input("\nPress Enter to return to the flight menu...")

                elif sub_choice == "4": #Displays flights going to sepcified Destination (from country name)
                    dest_name = input("Enter Destination Country: ")
                    flights = get_flights_by_destination_country(dest_name)
                    headers = ["Flight ID", "Personal ID", "Destination ID", "Arrival Destination ID", "Departure Time", "Flight Time", "Status"]
                    format_table(flights, headers)
                    input("\nPress Enter to return to the flight menu...")
                
                elif sub_choice == "5": #Displays flights going to sepcified Departure Location (from ID)
                    arr_name = input("Enter Departure Country ID: ")
                    flights = get_flights_by_arrival_id(arr_name)
                    headers = ["Flight ID", "Personal ID", "Destination ID", "Arrival Destination ID", "Departure Time", "Flight Time", "Status"]
                    format_table(flights, headers)
                    input("\nPress Enter to return to the flight menu...")

                elif sub_choice == "6": #Displays flights going to sepcified Departure Location (from country name)
                    arr_name = input("Enter Departure Country: ")
                    flights = get_flights_by_arrival_country(arr_name)
                    headers = ["Flight ID", "Personal ID", "Destination ID", "Arrival Destination ID", "Departure Time", "Flight Time", "Status"]
                    format_table(flights, headers)
                    input("\nPress Enter to return to the flight menu...")

                elif sub_choice == "7": #Displays flights going to sepcified Departure Date
                    date = input("Enter Departure Date (YYYY-MM-DD): ")
                    try:
                        datetime.strptime(date, "%Y-%m-%d")
                        flights = get_flights_by_date(date)
                        headers = ["Flight ID", "Personal ID", "Destination ID", "Arrival Destination ID", "Departure Time", "Flight Time", "Status"]
                        format_table(flights, headers)
                    except ValueError:
                        print("Invalid date format. Please use YYYY-MM-DD.")
                    input("\nPress Enter to return to the flight menu...")

                elif sub_choice == "8": #Leave sub-menu and return to menu
                    break

                else:
                    print("Option not yet implemented or invalid. Try again.")

        elif choice == "2": #Main menu Option 2 - Flight Update, Add or Cancel
            while True:
                show_flight_update_menu()
                sub_choice = input("Select a flight update option: ")

                if sub_choice == "1": #Runs Function to add a new entry to Flights
                    add_new_flight()
                    input("\nPress Enter to return to the flight menu...")

                elif sub_choice == "2": #Runs Function to cancel a entry in Flights (does not delete entry, but updates Status to "Cancelled")
                    flight_id = input("Enter Flight ID Number: ")
                    cancel_flight_by_id(flight_id)
                    input("\nPress Enter to return to the flight menu...")
                
                elif sub_choice == "3": #Runs Function to update flight Status (will not run "Cancelled", but updates Status for "OnRoute", "NotDeparted", "Arrived")
                    status_update_ID = input("Enter Flight ID Number: ")
                    update_flight_status(status_update_ID)
                    input("\nPress Enter to return to the flight menu...")

                elif sub_choice == "4": #Stop sub-menu, return to Main menu
                    break

                else: #Error/Invalid Input Handling
                    print("Option not yet implemented or invalid. Try again.")

        elif choice == "3": #Main menu Option 3 - Pilot Table view, add and manage options
            while True:
                show_pilot_manage_menu()
                sub_choice = input("Select a option: ")

                if sub_choice == "1": #Runs Function to add new Pilot
                    add_new_pilot()
                    input("\nPress Enter to return to the Pilot Manager menu...")

                elif sub_choice == "2": #Runs Function to delete a Pilot (if not assigned to flight)
                    pilot_id = input("Enter Pilot ID Number to be Removed: ")
                    delete_pilot_by_id(pilot_id)
                    input("\nPress Enter to return to the Pilot Manager menu...")
                
                elif sub_choice == "3": #Runs Function to view all Pilots in database and associated information (address, email, etc.)
                    view_all_pilots(format_table)
                    input("\nPress Enter to return to the Pilot Manager menu...")

                elif sub_choice == "4": #Runs Function to COUNT and display number of Pilots in Pilots Table
                    count_total_pilots()
                    input("\nPress Enter to return to the Pilot Manager menu...")

                elif sub_choice == "5": #Exit submenu, return to Main Menu
                    break

                else:
                    print("Option not yet implemented or invalid. Try again.")

        elif choice == "4": #Main menu Option 4 - Pilot scheldule information (interaction between Pilots and Flights table)
            while True:
                show_pilot_scheldule_menu()
                sub_choice = input("Select a option: ")

                if sub_choice == "1": #Reassign Pilot on Flight
                    pilot_id = input("Enter Pilot ID Number: ")
                    reassign_pilot(pilot_id)
                    input("\nPress Enter to return to the pilot menu...")

                elif sub_choice == "2": #View all Flights a specific Pilot has flown/will fly
                    pilot_id = input("Enter Pilot ID Number: ")
                    view_all_flights_for_pilot(pilot_id, format_table)
                    input("\nPress Enter to return to the pilot menu...")
                
                elif sub_choice == "3": #View all Flights a specific Pilot will fly (does not show Flights with Status "Arrived")
                    view_active_flights_for_pilot(pilot_id, format_table)
                    input("\nPress Enter to return to the pilot menu...")

                elif sub_choice == "4": #Exit sub-menu, return to Main Menu
                    break

                else: #Error/Invalid input handling
                    print("Option not yet implemented or invalid. Try again.")

        elif choice == "5":  #Main menu Option 5 - Destination Information, Add, Deleting and Cost
            while True:
                show_destination_manage_menu()
                sub_choice = input("Select a option: ")

                if sub_choice == "1": #Runs Function to view all entries in Destination Table
                    view_all_destinations(format_table)
                    input("\nPress Enter to return to the destination menu...")

                elif sub_choice == "2": #Delete Destination from Destination ID (if not in Flights table)
                    destination_id = input("Enter Destination ID Number: ")
                    delete_destination_by_id(destination_id)
                    input("\nPress Enter to return to the destination menu...")
                
                elif sub_choice == "3": #Run Function to add new entry to Destination table
                    add_new_destination()
                    input("\nPress Enter to return to the destination menu...")

                elif sub_choice == "4": #Run Function to update destination information in Destination table
                    destination_id = input("Enter Destination ID Number: ")
                    update_destination(destination_id)
                    input("\nPress Enter to return to the destination menu...")

                elif sub_choice == "5": #Run Function to find Flights flying/flown to a entry in Destination table
                    destination_id = input("Enter Destination ID Number: ")
                    find_flights_by_destination(destination_id, format_table)
                    input("\nPress Enter to return to the destination menu...")

                elif sub_choice == "6": #Run Function to view destinations, sorting by cost in descending order
                    view_destinations_by_cost(format_table)
                    input("\nPress Enter to return to the destination menu...")

                elif sub_choice == "7": #Run Function to view Destinations entries not assigned to a entry in Flights
                    view_unassigned_destinations(format_table)
                    input("\nPress Enter to return to the destination menu...")

                elif sub_choice == "8": #Exity sub-menu, return to Main menu
                    break

                else: #Error/Invalid input handling
                    print("Option not yet implemented or invalid. Try again.")

        elif choice == "6": #Main Menu Option 6 - "Delayed" Flights view and calculations
            while True:
                show_delay_manage_menu()
                sub_choice = input("Select a option: ")

                if sub_choice == "1": #Calls function to view all flights that have ever had "Delayed" status and caluclate length of time of delay
                    view_delayed_flights_with_duration(format_table)
                    input("\nPress Enter to return to the delay menu...")

                elif sub_choice == "2":
                    view_average_delay_duration() #Calls function to calculcate average time of flight delay
                    input("\nPress Enter to return to the delay menu...")

                elif sub_choice == "3": #Exit sub-menu, return to Main menu
                    break

                else: #Error/Invalid Input Handling
                    print("Option not yet implemented or invalid. Try again.")

        elif choice == "7": #Exit Main menu and .quit program
            print("Exiting... Thanks for using FlyMe Management System. Goodbye!")
            break

        else: #Invalid Input/Error handling
            print("Invalid option. Try again.")

if __name__ == "__main__":
    main()