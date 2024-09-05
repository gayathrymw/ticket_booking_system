import customtkinter as ctk
from tkinter import messagebox
import psycopg2
from datetime import datetime

# Database connection
conn = psycopg2.connect(
    dbname="Movie_Booking",
    user="postgres",
    password="postgres",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# Set appearance mode and color theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Global variable to store the logged-in user's ID
current_user_id = None

# Main Application Window
class MovieTicketApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Movie Ticket Booking System")
        self.geometry("600x400")

        # Main Menu
        self.create_main_menu()

    def create_main_menu(self):
        ctk.CTkLabel(self, text="Welcome to Movie Ticket Booking System", font=("Arial", 20)).pack(pady=20)

        ctk.CTkButton(self, text="Register", command=self.open_register_window, font=("Arial", 14)).pack(pady=10)
        ctk.CTkButton(self, text="Login", command=self.open_login_window, font=("Arial", 14)).pack(pady=10)

    def open_register_window(self):
        register_window = RegisterWindow(self)
        register_window.grab_set()

    def open_login_window(self):
        login_window = LoginWindow(self)
        login_window.grab_set()

# Registration Window
class RegisterWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Register")
        self.geometry("400x400")

        ctk.CTkLabel(self, text="First Name").pack(pady=5)
        self.first_name = ctk.CTkEntry(self)
        self.first_name.pack(pady=5)

        ctk.CTkLabel(self, text="Last Name").pack(pady=5)
        self.last_name = ctk.CTkEntry(self)
        self.last_name.pack(pady=5)

        ctk.CTkLabel(self, text="Email").pack(pady=5)
        self.email = ctk.CTkEntry(self)
        self.email.pack(pady=5)

        ctk.CTkLabel(self, text="Phone Number 1").pack(pady=5)
        self.phone1 = ctk.CTkEntry(self)
        self.phone1.pack(pady=5)

        ctk.CTkLabel(self, text="Phone Number 2").pack(pady=5)
        self.phone2 = ctk.CTkEntry(self)
        self.phone2.pack(pady=5)

        ctk.CTkLabel(self, text="Password").pack(pady=5)
        self.password = ctk.CTkEntry(self, show="*")
        self.password.pack(pady=5)

        ctk.CTkButton(self, text="Submit", command=self.register_user).pack(pady=20)

    def register_user(self):
        # Fetch input data
        first_name = self.first_name.get()
        last_name = self.last_name.get()
        email = self.email.get()
        phone1 = self.phone1.get()
        phone2 = self.phone2.get()
        password = self.password.get()

        # Insert data into database
        try:
            cursor.execute(
                "INSERT INTO Customer (first_name, last_name, email_id, phone_no1, phone_no2, password) VALUES (%s, %s, %s, %s, %s, %s)",
                (first_name, last_name, email, phone1, phone2, password)
            )
            conn.commit()
            messagebox.showinfo("Success", "Registration Successful")
            self.destroy()
        except psycopg2.IntegrityError as e:
            conn.rollback()
            messagebox.showerror("Error", f"Error occurred: {e}. Check your input data.")

# Login Window
class LoginWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Login")
        self.geometry("300x200")

        ctk.CTkLabel(self, text="Email").pack(pady=5)
        self.email = ctk.CTkEntry(self)
        self.email.pack(pady=5)

        ctk.CTkLabel(self, text="Password").pack(pady=5)
        self.password = ctk.CTkEntry(self, show="*")
        self.password.pack(pady=5)

        ctk.CTkButton(self, text="Login", command=self.login_user).pack(pady=20)

    def login_user(self):
        global current_user_id
        # Fetch input data
        email = self.email.get()
        password = self.password.get()

        # Verify user in database
        cursor.execute("SELECT c_id FROM Customer WHERE email_id = %s AND password = %s", (email, password))
        user = cursor.fetchone()

        if user:
            current_user_id = user[0]
            #print(current_user_id)
            messagebox.showinfo("Success", "Login Successful")
            self.destroy()
            locations_window = LocationsWindow(self.parent)
            locations_window.grab_set()
        else:
            messagebox.showerror("Error", "Invalid credentials")

# Locations Window
class LocationsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Available Locations")
        self.geometry("600x500")  # Increased height to accommodate new elements

        # Fetch customer's name
        cursor.execute("SELECT first_name, last_name FROM Customer WHERE c_id = %s", (current_user_id,))
        customer = cursor.fetchone()
        customer_name = f"{customer[0]} {customer[1]}" if customer else "Customer"

        # Welcome message with customer's name
        ctk.CTkLabel(self, text=f"Welcome, {customer_name}!", font=("Arial", 20)).pack(pady=20)

        ctk.CTkLabel(self, text="Select a Location", font=("Arial", 18)).pack(pady=10)

        # Fetch unique locations from the database
        cursor.execute("SELECT DISTINCT location FROM Theatre")
        locations = [location[0] for location in cursor.fetchall()]

        # Create a dropdown menu (combobox) for location selection
        self.location_var = ctk.StringVar()
        self.location_dropdown = ctk.CTkComboBox(self, variable=self.location_var, values=locations,
                                                 font=("Arial", 14), width=200,
                                                 command=self.on_location_select)
        self.location_dropdown.pack(pady=20)

        # Label to prompt user
        self.prompt_label = ctk.CTkLabel(self, text="Please select a location from the dropdown menu",
                                         font=("Arial", 14))
        self.prompt_label.pack(pady=20)

        # Button to view previous bookings
        ctk.CTkButton(self, text="View Previous Bookings", command=self.view_previous_bookings,
                      font=("Arial", 14)).pack(pady=20)

        ctk.CTkButton(self, text="Logout", command=self.logout, font=("Arial", 14)).pack(pady=20)

    def on_location_select(self, selected_location):
        if selected_location:
            movies_window = MoviesWindow(self, selected_location)
            movies_window.grab_set()
    def logout(self):
        global current_user_id
        current_user_id = None
        self.destroy()
        app.create_main_menu()

    def view_previous_bookings(self):
        previous_bookings_window = PreviousBookingsWindow(self)
        previous_bookings_window.grab_set()

class PreviousBookingsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Previous Bookings")
        self.geometry("800x600")

        ctk.CTkLabel(self, text="Your Booking History", font=("Arial", 20, "bold")).pack(pady=20)

        # Create a frame for the scrollable content
        self.scroll_frame = ctk.CTkScrollableFrame(self, width=700, height=450)
        self.scroll_frame.pack(pady=10)

        # Fetch and display booking history
        self.fetch_and_display_bookings()

        ctk.CTkButton(self, text="Close", command=self.destroy, font=("Arial", 14)).pack(pady=20)

    def fetch_and_display_bookings(self):
        try:
            cursor.execute("""
                SELECT t.ticket_no, m.movie_name, th.tname, ms.show_starttime, ms.show_endtime, 
                        t.seat_no1, t.seat_no2, t.seat_no3, t.seat_no4, t.seat_no5, 
                        t.price, t.show_date
                FROM Ticket t
                JOIN Movie_Show ms ON t.show_id = ms.show_id
                JOIN Movie m ON ms.movie_name = m.movie_name
                JOIN Theatre th ON ms.tid = th.tid
                WHERE t.c_id = %s
                ORDER BY t.show_date DESC, ms.show_starttime DESC
            """, (current_user_id,))

            bookings = cursor.fetchall()

            if not bookings:
                ctk.CTkLabel(self.scroll_frame, text="No previous bookings found.", font=("Arial", 16)).pack(
                    pady=10)
            else:
                for booking in bookings:
                    booking_frame = ctk.CTkFrame(self.scroll_frame)
                    booking_frame.pack(fill="x", padx=10, pady=10)

                    ticket_no, movie, theatre, start_time, end_time, *seats, price, show_date = booking
                    seats = [seat for seat in seats if seat is not None]

                    booking_info = f"""
                    Date: {show_date.strftime('%Y-%m-%d')}
                    Movie: {movie}
                    Theatre: {theatre}
                    Time: {start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}
                    Seats: {', '.join(map(str, seats))}
                    Total Price: ₹{price}
                    """

                    ctk.CTkLabel(booking_frame, text=booking_info.strip(), font=("Arial", 14), justify="left").pack(
                        pady=10)

        except psycopg2.Error as e:
            messagebox.showerror("Database Error", f"An error occurred while fetching booking history: {str(e)}")

# Movies Window
class MoviesWindow(ctk.CTkToplevel):
    def __init__(self, parent, location):
        super().__init__(parent)
        self.title("Movies")
        self.geometry("600x400")

        ctk.CTkLabel(self, text=f"Movies playing in {location}", font=("Arial", 20)).pack(pady=20)

        # Fetch and display movies playing in the selected location
        cursor.execute("""
            SELECT DISTINCT m.movie_name
            FROM Movie m
            JOIN Movie_Show ms ON m.movie_name = ms.movie_name
            JOIN Theatre t ON ms.tid = t.tid
            WHERE t.location = %s
        """, (location,))
        movies = cursor.fetchall()

        for movie in movies:
            movie_button = ctk.CTkButton(self, text=movie[0], font=("Arial", 14),
                                         command=lambda m=movie[0], l=location: self.show_movie_details(m, l))
            movie_button.pack(pady=5)

        ctk.CTkButton(self, text="Back to Locations", command=self.destroy).pack(pady=20)

    def show_movie_details(self, movie_name, location):
        movie_details_window = MovieDetailsWindow(self, movie_name, location)
        movie_details_window.grab_set()

class MovieDetailsWindow(ctk.CTkToplevel):
    def __init__(self, parent, movie_name, location):
        super().__init__(parent)
        self.title(f"{movie_name} - Details")
        self.geometry("700x600")

        # Main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Fetch movie details
        cursor.execute("""
            SELECT *
            FROM Movie
            WHERE movie_name = %s
        """, (movie_name,))
        movie_details = cursor.fetchone()

        if movie_details:
            # Movie title
            ctk.CTkLabel(main_frame, text=movie_name, font=("Arial", 24, "bold")).pack(pady=(0, 20))

            # Movie details
            details_frame = ctk.CTkFrame(main_frame)
            details_frame.pack(fill="both", expand=True, padx=10, pady=10)

            details = [
                ("Release Date", movie_details[1]),
                ("Rating", movie_details[3]),
                ("Language", movie_details[4]),
                ("Actor", movie_details[5]),
                ("Actress", movie_details[6]),
                ("Director", movie_details[7]),
                ("Producer", movie_details[8]),
                ("Music Director", movie_details[9]),
                ("DOP", movie_details[10]),
                ("Description", movie_details[2])
            ]

            for label, value in details:
                detail_row = ctk.CTkFrame(details_frame)
                detail_row.pack(fill="x", padx=5, pady=2)
                ctk.CTkLabel(detail_row, text=f"{label}:", font=("Arial", 14, "bold")).pack(side="left", padx=5)
                ctk.CTkLabel(detail_row, text=str(value), font=("Arial", 14)).pack(side="left", padx=5)

            # Description
            #ctk.CTkLabel(details_frame, text="Description:", font=("Arial", 14, "bold")).pack(anchor="w", padx=5, pady=(10, 0))
            #ctk.CTkLabel(details_frame, text=movie_details[2], wraplength=600, justify="left").pack(padx=5, pady=5)

        # Theatres showing the movie
        ctk.CTkLabel(main_frame, text="Theatres Showing This Movie", font=("Arial", 18, "bold")).pack(pady=(20, 10))

        cursor.execute("""
            SELECT DISTINCT t.tname
            FROM Theatre t
            JOIN Movie_Show ms ON t.tid = ms.tid
            WHERE ms.movie_name = %s AND t.location = %s
        """, (movie_name, location))
        theatres = cursor.fetchall()

        for theatre in theatres:
            ctk.CTkButton(
                main_frame, 
                text=theatre[0], 
                command=lambda t=theatre[0]: self.show_showtimes(t, movie_name),
                font=("Arial", 14)
            ).pack(pady=5, padx=20, fill="x")

        # Back button
        ctk.CTkButton(
            main_frame, 
            text="Back to Movies", 
            command=self.destroy, 
            font=("Arial", 14)
        ).pack(pady=20)

    def show_showtimes(self, theatre_name, movie_name):
        showtime_window = ShowtimeWindow(self, theatre_name, movie_name)
        showtime_window.grab_set()

# Theatre Window
class TheatreWindow(ctk.CTkToplevel):
    def __init__(self, parent, movie_name, location):
        super().__init__(parent)
        self.title("Theatres")
        self.geometry("600x400")

        ctk.CTkLabel(self, text=f"Theatres showing {movie_name} in {location}", font=("Arial", 20)).pack(pady=20)

        # Fetch and display theatres showing the selected movie in the selected location
        cursor.execute("""
            SELECT DISTINCT t.tname
            FROM Theatre t
            JOIN Movie_Show ms ON t.tid = t.tid
            WHERE ms.movie_name = %s AND t.location = %s
        """, (movie_name, location))
        theatres = cursor.fetchall()

        for theatre in theatres:
            theatre_button = ctk.CTkButton(self, text=theatre[0], font=("Arial", 14),
                                           command=lambda t=theatre[0], m=movie_name: self.show_showtimes(t, m))
            theatre_button.pack(pady=5)

        ctk.CTkButton(self, text="Back to Movies", command=self.destroy).pack(pady=20)

    def show_showtimes(self, theatre_name, movie_name):
        showtime_window = ShowtimeWindow(self, theatre_name, movie_name)
        showtime_window.grab_set()

# Showtime Window
class ShowtimeWindow(ctk.CTkToplevel):
    def __init__(self, parent, theatre_name, movie_name):
        super().__init__(parent)
        self.title("Showtimes")
        self.geometry("600x400")

        ctk.CTkLabel(self, text=f"Showtimes for {movie_name} at {theatre_name}", font=("Arial", 20)).pack(pady=20)

        # Fetch and display showtimes for the selected movie and theatre
        cursor.execute("""
            SELECT ms.show_starttime, ms.show_endtime, ms.Screen_no
            FROM Movie_Show ms
            JOIN Theatre t ON ms.tid = t.tid
            WHERE ms.movie_name = %s AND t.tname = %s
        """, (movie_name, theatre_name))
        showtimes = cursor.fetchall()

        for showtime in showtimes:
            showtime_button = ctk.CTkButton(self, text=f"Start: {showtime[0]}, End: {showtime[1]}, Screen: {showtime[2]}", 
                                            font=("Arial", 14),
                                            command=lambda st=showtime[0], et=showtime[1], sn=showtime[2]: 
                                                self.select_seats(movie_name, theatre_name, st, et, sn))
            showtime_button.pack(pady=5)

        ctk.CTkButton(self, text="Back to Theatres", command=self.destroy).pack(pady=20)

    def select_seats(self, movie_name, theatre_name, start_time, end_time, screen_no):
        seat_selection_window = SeatSelectionWindow(self, movie_name, theatre_name, start_time, end_time, screen_no)
        seat_selection_window.grab_set()

# Seat Selection Window
class SeatSelectionWindow(ctk.CTkToplevel):
    def __init__(self, parent, movie_name, theatre_name, start_time, end_time, screen_no):
        super().__init__(parent)
        self.title("Seat Selection")
        self.geometry("400x300")
        self.movie_name = movie_name
        self.theatre_name = theatre_name
        self.start_time = start_time
        self.end_time = end_time
        self.screen_no = screen_no

        ctk.CTkLabel(self, text="Select number of seats:", font=("Arial", 16)).pack(pady=20)

        self.seat_count = ctk.CTkEntry(self, width=50)
        self.seat_count.pack(pady=10)

        ctk.CTkButton(self, text="Confirm Seats", command=self.confirm_seats).pack(pady=20)

    def confirm_seats(self):
        try:
            num_seats = int(self.seat_count.get())
            if num_seats <= 0:
                raise ValueError("Number of seats must be positive")
            elif num_seats > 5:
                raise ValueError("Maximum 5 seats can be booked at a time")
            
            seat_confirmation_window = SeatConfirmationWindow(self, self.movie_name, self.theatre_name, 
                                                              self.start_time, self.end_time, self.screen_no, num_seats)
            seat_confirmation_window.grab_set()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

# Modified Seat Confirmation Window
class SeatConfirmationWindow(ctk.CTkToplevel):
    def __init__(self, parent, movie_name, theatre_name, start_time, end_time, screen_no, num_seats):
        super().__init__(parent)
        self.title("Seat Confirmation")
        self.geometry("400x500")
        self.movie_name = movie_name
        self.theatre_name = theatre_name
        self.start_time = start_time
        self.end_time = end_time
        self.screen_no = screen_no
        self.num_seats = num_seats
        self.discount_amount = 0
        self.offer_id = None

        ctk.CTkLabel(self, text="Confirm your seats:", font=("Arial", 16)).pack(pady=20)

        self.seats = []
        for i in range(num_seats):
            seat = f"A{i + 1}"
            self.seats.append(seat)
            ctk.CTkLabel(self, text=f"Seat {seat}: ₹150", font=("Arial", 14)).pack(pady=5)

        self.total_price = num_seats * 150
        self.price_label = ctk.CTkLabel(self, text=f"Total Price: ₹{self.total_price}", font=("Arial", 16, "bold"))
        self.price_label.pack(pady=20)

        self.discount_button = ctk.CTkButton(self, text="Apply Discount", command=self.open_discount_window)
        self.discount_button.pack(pady=10)

        ctk.CTkButton(self, text="Confirm Booking", command=self.confirm_booking).pack(pady=20)

    def open_discount_window(self):
        discount_window = DiscountWindow(self)
        discount_window.grab_set()

    def update_price(self, discount_amount, offer_id):
        self.discount_amount = discount_amount
        self.offer_id = offer_id
        self.total_price -= discount_amount
        self.price_label.configure(text=f"Total Price: ₹{self.total_price} (Discount: ₹{discount_amount})")
            # Disable the discount button after applying a discount
        self.discount_button.configure(state="disabled")



    def confirm_booking(self):
        global current_user_id
        if current_user_id is None:
            messagebox.showerror("Error", "Please log in to book tickets")
            return

        # Get the show_id
        cursor.execute("""
            SELECT ms.show_id
            FROM Movie_Show ms
            JOIN Theatre t ON ms.tid = t.tid
            WHERE ms.movie_name = %s AND t.tname = %s AND ms.show_starttime = %s AND ms.Screen_no = %s
        """, (self.movie_name, self.theatre_name, self.start_time, self.screen_no))
        
        result = cursor.fetchone()
        if result is None:
            raise ValueError("Show not found")
        show_id = result[0]

        # Insert ticket information
        cursor.execute("""
            INSERT INTO Ticket (c_id, seat_no1, seat_no2, seat_no3, seat_no4, seat_no5, price, show_date, show_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING ticket_no
        """, (current_user_id, 
                int(self.seats[0][1:]) if len(self.seats) > 0 else None,
                int(self.seats[1][1:]) if len(self.seats) > 1 else None,
                int(self.seats[2][1:]) if len(self.seats) > 2 else None,
                int(self.seats[3][1:]) if len(self.seats) > 3 else None,
                int(self.seats[4][1:]) if len(self.seats) > 4 else None,
                self.total_price,
                datetime.now().date(),
                show_id))
        
        ticket_no = cursor.fetchone()[0]

        # If a discount was applied, insert into Ticket_Discount table
        if self.offer_id:
            cursor.execute("""
                INSERT INTO Ticket_Discount (ticket_no, offer_id)
                VALUES (%s, %s)
            """, (ticket_no, self.offer_id))

        conn.commit()

        ticket_window = TicketWindow(self, self.movie_name, self.theatre_name, self.start_time, 
                                    self.end_time, self.screen_no, self.seats, self.total_price, 
                                    self.discount_amount, ticket_no)
        ticket_window.grab_set()
        #self.destroy()
'''
            messagebox.showinfo("Success", f"Booking confirmed! Ticket number: {ticket_no}")
            self.after(100, lambda: self.create_ticket_window(ticket_no))
            self.destroy()

        except (psycopg2.Error, ValueError) as e:
            conn.rollback()
            messagebox.showerror("Error", f"Booking failed: {str(e)}")
            print(f"Error details: {e}")  # For debugging

    def create_ticket_window(self, ticket_no):
        ticket_window = TicketWindow(self.parent, self.movie_name, self.theatre_name, self.start_time, 
                                     self.end_time, self.screen_no, self.seats, self.total_price, 
                                     self.discount_amount, ticket_no)
        ticket_window.grab_set()
'''

# Modified Discount Window
class DiscountWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Apply Discount")
        self.geometry("300x200")

        ctk.CTkLabel(self, text="Enter Offer ID:", font=("Arial", 16)).pack(pady=20)

        self.offer_id_entry = ctk.CTkEntry(self, width=100)
        self.offer_id_entry.pack(pady=10)

        ctk.CTkButton(self, text="Apply", command=self.apply_discount).pack(pady=20)

    def apply_discount(self):
        offer_id = self.offer_id_entry.get()
        try:
            # Check if the offer_id exists in the Discount table
            cursor.execute("SELECT discount_amt FROM Discount WHERE offer_id = %s", (offer_id,))
            result = cursor.fetchone()
            if result:
                discount_amount = result[0]
                self.parent.update_price(discount_amount, offer_id)
                messagebox.showinfo("Success", f"Discount of ₹{discount_amount} applied successfully!")
                self.destroy()
            else:
                messagebox.showerror("Error", "Invalid Offer ID")
        except psycopg2.Error as e:
            messagebox.showerror("Database Error", str(e))

# Modified Ticket Window
class TicketWindow(ctk.CTkToplevel):
    def __init__(self, parent, movie_name, theatre_name, start_time, end_time, screen_no, seats, total_price, discount_amount, ticket_no):
        super().__init__(parent)
        self.parent = parent
        self.title("Your Ticket")
        self.geometry("400x550")

        ctk.CTkLabel(self, text="Your Ticket", font=("Arial", 20, "bold")).pack(pady=20)

        ticket_info = f"""
        Ticket Number: {ticket_no}
        Movie: {movie_name}
        Theatre: {theatre_name}
        Date: {datetime.now().strftime('%Y-%m-%d')}
        Time: {start_time} - {end_time}
        Screen: {screen_no}
        Seats: {', '.join(seats)}
        Original Price: ₹{len(seats) * 150}
        Discount Applied: ₹{discount_amount}
        Total Price: ₹{total_price}
        """

        ctk.CTkLabel(self, text=ticket_info, font=("Arial", 14), justify="left").pack(pady=20)

        ctk.CTkButton(self, text="Back to Main Menu", command=self.back_to_main_menu).pack(pady=20)

    def back_to_main_menu(self):
        self.destroy()
        locations_window = LocationsWindow(self.parent)
        locations_window.grab_set()

if __name__ == "__main__":
    app = MovieTicketApp()
    app.mainloop()