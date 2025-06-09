import json
import os
from datetime import datetime
import re

class Passenger:
    def __init__(self, name, passport, flight_no, seat):
        self.name = name
        self.passport = passport
        self.flight_no = flight_no
        self.seat = seat
        self.booking_id = self.generate_booking_id()

    def generate_booking_id(self):
        return f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}"

    def to_dict(self):
        return {
            "booking_id": self.booking_id,
            "name": self.name,
            "passport": self.passport,
            "flight_no": self.flight_no,
            "seat": self.seat
        }

class AirlineSystem:
    def __init__(self, data_file="reservations.json"):
        self.data_file = data_file
        self.reservations = []
        self.available_flights = ["FL101", "FL102", "FL103"]
        self.seats = [f"{row}{letter}" for row in range(1, 11) for letter in "ABCDEF"]
        self.load_reservations()

    def load_reservations(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                try:
                    data = json.load(f)
                    self.reservations = [Passenger(d["name"], d["passport"], d["flight_no"], d["seat"]) 
                                       for d in data]
                except json.JSONDecodeError:
                    self.reservations = []

    def save_reservations(self):
        with open(self.data_file, 'w') as f:
            json.dump([r.to_dict() for r in self.reservations], f, indent=4)

    def validate_passport(self, passport):
        return bool(re.match(r'^[A-Z0-9]{9}$', passport))

    def book_ticket(self, name, passport, flight_no, seat):
        if not name.strip():
            raise ValueError("Name cannot be empty")
        if not self.validate_passport(passport):
            raise ValueError("Invalid passport number (9 alphanumeric characters required)")
        if flight_no not in self.available_flights:
            raise ValueError("Invalid flight number")
        if seat not in self.seats:
            raise ValueError("Invalid seat")
        if any(r.seat == seat and r.flight_no == flight_no for r in self.reservations):
            raise ValueError("Seat already booked")
        
        passenger = Passenger(name, passport, flight_no, seat)
        self.reservations.append(passenger)
        self.save_reservations()
        return passenger.booking_id

    def cancel_reservation(self, booking_id):
        initial_length = len(self.reservations)
        self.reservations = [r for r in self.reservations if r.booking_id != booking_id]
        if len(self.reservations) < initial_length:
            self.save_reservations()
            return True
        return False

    def view_reservations(self):
        return [r.to_dict() for r in self.reservations]

    def search_reservations(self, query, reservations=None):
        if reservations is None:
            reservations = self.reservations
        
        if not query:
            return reservations
        
        if len(reservations) == 0:
            return []
        
        reservations.sort(key=lambda x: x.name.lower())
        mid = len(reservations) // 2
        mid_name = reservations[mid].name.lower()
        query = query.lower()

        if mid_name == query:
            return [reservations[mid]]
        elif len(reservations) == 1:
            return [reservations[0]] if query in mid_name else []
        
        if query < mid_name:
            return self.search_reservations(query, reservations[:mid])
        else:
            return self.search_reservations(query, reservations[mid:])

def display_menu():
    print("\nAirline Ticket Reservation System")
    print("1. Book a Ticket")
    print("2. Cancel a Reservation")
    print("3. View All Reservations")
    print("4. Search Reservations")
    print("5. Exit")

def main():
    system = AirlineSystem()
    while True:
        display_menu()
        try:
            choice = input("Enter your choice (1-5): ").strip()
            if choice == "1":
                print("\nAvailable flights:", ", ".join(system.available_flights))
                name = input("Enter name: ").strip()
                passport = input("Enter passport number (9 alphanumeric characters): ").strip()
                flight_no = input("Enter flight number: ").strip()
                print("Available seats:", ", ".join(system.seats[:10]), "...")
                seat = input("Enter seat (e.g., 1A): ").strip()
                try:
                    booking_id = system.book_ticket(name, passport, flight_no, seat)
                    print(f"Booking confirmed! Booking ID: {booking_id}")
                except ValueError as e:
                    print(f"Error: {e}")

            elif choice == "2":
                booking_id = input("Enter booking ID to cancel: ").strip()
                if system.cancel_reservation(booking_id):
                    print("Reservation cancelled successfully")
                else:
                    print("Booking ID not found")

            elif choice == "3":
                reservations = system.view_reservations()
                if not reservations:
                    print("No reservations found")
                else:
                    print("\nAll Reservations:")
                    for res in reservations:
                        print(f"ID: {res['booking_id']}, Name: {res['name']}, Passport: {res['passport']}, "
                              f"Flight: {res['flight_no']}, Seat: {res['seat']}")

            elif choice == "4":
                query = input("Enter name to search: ").strip()
                results = system.search_reservations(query)
                if not results:
                    print("No matching reservations found")
                else:
                    print("\nSearch Results:")
                    for res in results:
                        print(f"ID: {res.booking_id}, Name: {res.name}, Passport: {res.passport}, "
                              f"Flight: {res.flight_no}, Seat: {res.seat}")

            elif choice == "5":
                print("Exiting system. Goodbye!")
                break

            else:
                print("Invalid choice. Please select 1-5.")

        except EOFError:
            print("\nEOF detected. Exiting system.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()