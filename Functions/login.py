"""
This file handles the login proccess of the program. It handles the login of the user, registration of the user, and exiting out of the program
Author: Fredrik Larida
"""
from getpass import getpass
import re

def email_validity(email):
    # Simple regex pattern to validate email is in valid format
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None # Returns True if email matches the pattern

# Handles user registration, prompting for name, email, phone, and password
def register_user(conn):
    cur = conn.cursor()
    name = input("Enter your name: ")
    
    # Loop to validate that the email format entered is valid
    while True:
        email = input("Enter your email: ")
        if email_validity(email):
            break
        else:
            print("Invalid email format. Please enter a valid email (e.g., example@domain.com).")
            
    phone = input("Enter your phone number: ")
    
    # Loop to confirm a user's new password
    while True:
        password = getpass("Enter a password: ")
        password_confirmation = getpass("To confirm your password, please type your password again: ")
        
        if password == password_confirmation:
            # Getting new user id
            cur.execute("SELECT COALESCE(MAX(usr), 0) + 1 FROM users") # Getting the max usr id
            new_user_id = cur.fetchone()[0]

            # Inserting the new user details into the database
            cur.execute(''' INSERT INTO users (usr, name, email, phone, pwd) VALUES
                            (?, ?, ?, ?, ?); ''',
                            (new_user_id, name, email, phone, password))
            conn.commit()
            print(f"Registration successfull, your new user ID is {new_user_id}")
            break
        else:
            print("Passwords you entered do not match, please try again")
        
# Handles user login, checking the user ID and password against the database
def login_user(conn):
    cur = conn.cursor()
    usr = input("Enter your user ID: ")
    pwd = getpass("Enter your password: ")

    # Query to find the user details based on the provided user ID
    cur.execute(''' SELECT *
                    FROM users
                    WHERE usr = ?;  ''', (usr,))
    user = cur.fetchone()
    
    # Checks if user exists and password matches
    if user:
        # This checks if correct password was entered if the entered User ID is valid
        if user[4] == pwd:
            print("\n--------------------")
            print(f"Welcome {user[1]}!")
            print("--------------------\n")
            return True, user[0]
        else:
            print("Incorrect password. Please try again.")
            return False, None
    # This is prompting the user to try again if entered an invalid user ID
    else:
        print(f"Invalid user ID, please register or enter an existing account ID")
        return False, None


# Displays the login screen and handles login, registration, and exit actions
def login_screen(conn):
    while True:
        # Login screen. Prompts the user with the choice of logging in, registering, or exiting
        print("=================Login Screen=================")
        choice = input("""Welcome! Please select an action\n1. Login\n2. Register\n3. Exit\nChoice: """) 
        if choice == '1':
            success, user_id = login_user(conn)
            if success:
                return user_id # Returns user ID if login is successful
        elif choice == '2':
            register_user(conn) # Calls registration function
        elif choice == '3':
            print("Goodbye\n")
            return None # Exits login screen if user selects "Exit"
        else:
            print("Invalid action. Please try again.\n")