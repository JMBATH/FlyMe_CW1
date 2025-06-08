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


def show_menu():
    print("\nHello, Welcome to")
    print("===== FlyMe Flight Management System =====")
    print("1. View Flights")
    print("2. Manage Flights (Add, Delete or Update Status)")
    print("3. View Pilot Schedule")
    print("4. Assign Pilot to Flight")
    print("5. View All Destinations")
    print("6. Update Destination Info")
    print("7. Exit\n")

def show_flight_menu():
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
    print("\n--- Update Flights ---")
    print("1. Add Flights")
    print("2. Cancel Flight")
    print("3. Update Flight Status")
    print("4. Back to Main Menu\n")

def format_table(rows, headers):
    col_widths = [max(len(str(cell)) for cell in col) for col in zip(*([headers] + rows))]
    row_format = " | ".join("{:<" + str(width) + "}" for width in col_widths)

    print("\n" + row_format.format(*headers))
    print("-" * (sum(col_widths) + 3 * (len(headers) - 1)))
    for row in rows:
        print(row_format.format(*row))

def main():
    while True:
        show_menu()
        choice = input("Select an option: ")

        if choice == "1": #Choice 1, View Flight Info, gives access to submenu
            while True:
                show_flight_menu()
                sub_choice = input("Select a flight view option: ")

                if sub_choice == "1":
                    flights = get_flights_by_status("all")
                    headers = ["Flight ID", "Personal ID", "Destination ID", "Arrival Destination ID", "Departure Time", "Flight Time", "Status"]
                    format_table(flights, headers)
                    input("\nPress Enter to return to the flight menu...")

                elif sub_choice == "2":
                    status = input("Enter flight status (e.g., Arrived, Cancelled): ")
                    flights = get_flights_by_status(status)
                    headers = ["Flight ID", "Personal ID", "Destination ID", "Arrival Destination ID", "Departure Time", "Flight Time", "Status"]
                    format_table(flights, headers)
                    input("\nPress Enter to return to the flight menu...")
                
                elif sub_choice == "3":
                    dest_ID = input("Enter Destination Country ID: ")
                    flights = get_flights_by_destination_id(dest_ID)
                    headers = ["Flight ID", "Personal ID", "Destination ID", "Arrival Destination ID", "Departure Time", "Flight Time", "Status"]
                    format_table(flights, headers)
                    input("\nPress Enter to return to the flight menu...")

                elif sub_choice == "4":
                    dest_name = input("Enter Destination Country: ")
                    flights = get_flights_by_destination_country(dest_name)
                    headers = ["Flight ID", "Personal ID", "Destination ID", "Arrival Destination ID", "Departure Time", "Flight Time", "Status"]
                    format_table(flights, headers)
                    input("\nPress Enter to return to the flight menu...")
                
                elif sub_choice == "5":
                    arr_name = input("Enter Departure Country ID: ")
                    flights = get_flights_by_arrival_id(arr_name)
                    headers = ["Flight ID", "Personal ID", "Destination ID", "Arrival Destination ID", "Departure Time", "Flight Time", "Status"]
                    format_table(flights, headers)
                    input("\nPress Enter to return to the flight menu...")

                elif sub_choice == "6":
                    arr_name = input("Enter Departure Country: ")
                    flights = get_flights_by_arrival_country(arr_name)
                    headers = ["Flight ID", "Personal ID", "Destination ID", "Arrival Destination ID", "Departure Time", "Flight Time", "Status"]
                    format_table(flights, headers)
                    input("\nPress Enter to return to the flight menu...")

                elif sub_choice == "7":
                    date = input("Enter Departure Date (YYYY-MM-DD): ")
                    try:
                        datetime.strptime(date, "%Y-%m-%d")
                        flights = get_flights_by_date(date)
                        headers = ["Flight ID", "Personal ID", "Destination ID", "Arrival Destination ID", "Departure Time", "Flight Time", "Status"]
                        format_table(flights, headers)
                    except ValueError:
                        print("Invalid date format. Please use YYYY-MM-DD.")
                    input("\nPress Enter to return to the flight menu...")

                elif sub_choice == "8":
                    break

                else:
                    print("Option not yet implemented or invalid. Try again.")

        elif choice == "2":
            while True:
                show_flight_update_menu()
                sub_choice = input("Select a flight update option: ")

                if sub_choice == "1":
                    add_new_flight()
                    input("\nPress Enter to return to the flight menu...")

                elif sub_choice == "2":
                    flight_id = input("Enter Flight ID Number: ")
                    cancel_flight_by_id(flight_id)
                    input("\nPress Enter to return to the flight menu...")
                
                elif sub_choice == "3":
                    status_update_ID = input("Enter Flight ID Number: ")
                    update_flight_status(status_update_ID)
                    input("\nPress Enter to return to the flight menu...")

                elif sub_choice == "4":
                    break

                else:
                    print("Option not yet implemented or invalid. Try again.")

        elif choice == "3":
            get_pilot_schedule()
            input("\nPress Enter to return to the menu...")

        elif choice == "4":
            assign_pilot_to_flight()
            input("\nPress Enter to return to the menu...")

        elif choice == "5":
            destinations = get_all_destinations()
            headers = ["Destination ID", "City", "Country"]
            format_table(destinations, headers)
            input("\nPress Enter to return to the menu...")

        elif choice == "6":
            update_destination_info()
            input("\nPress Enter to return to the menu...")

        elif choice == "7":
            print("Exiting... Goodbye!")
            break

        else:
            print("Invalid option. Try again.")

if __name__ == "__main__":
    main()