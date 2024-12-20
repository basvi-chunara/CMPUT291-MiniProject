"""
Main program of the project. Handles all the main processes
Authors: Annie Ding, Basvi Chunara, Fredrik Larida
"""

import sqlite3
import argparse
from login import login_screen
from display_tweets import tweet_display
from list_followers import followers_list
from search_tweets import search_tweets, show_tweets
from tweet import make_tweet
from search_user import search_user

# Initializes the database connection and enables foreign keys
def initialize_db(db_name):
    # 
    conn = sqlite3.connect(db_name)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# Displays the main menu and handles the user's choices
def main_menu(conn, user_id):
    while True:
        print("\n=================Main Menu=================")
        print("1. Search for Tweets")
        print("2. Search for Users")
        print("3. Compose a Tweet")
        print("4. List Followers")
        print("5. Logout")
        print("6. Go back to main feed")

        choice = input("Choose an option:")
        # Option to search for tweets by keywords
        if choice == '1':
            print("\n=================Tweet Search=================")
            keywords = input("Enter keywords to search (separated by spaces) or press enter to cancel search: ")
            # keywords = keywords.split()
            if not keywords:
                print("Search cancelled\n")
                continue
            else:
                show_tweets(conn, keywords, user_id)  # Passes control to `show_tweets` with the selected keywords
        # Option to search for a user
        elif choice == '2':
            search_user(conn, user_id)
        # Option to make a new tweet
        elif choice == '3':
            make_tweet(conn, user_id, None)
        # Option to list the user's follower list
        elif choice == '4':
            followers_list(conn, user_id)
        # Option to logout
        elif choice == '5':
            print("Logging out")
            return
        # Option to go back to the main tweet feed
        elif choice == '6':
            tweet_display(conn, user_id) 
        # Handles the user selecting invalid inputs
        else:
            print("Invalid action. Try again")
            
# Main function that handles the arguments, initialize the database, and start the program
def main():
    # Parsing command-line arguments for name of databse
    parser = argparse.ArgumentParser()
    parser.add_argument("db_name")
    args = parser.parse_args()

    # Initializing databse with the given name file
    conn = initialize_db(args.db_name)

    #Starting the login and main menu loop
    while True:
        user_id = login_screen(conn) # Prompting the login 
        if user_id:
            tweet_display(conn, user_id) # Displaying the main feed after successful login
            main_menu(conn, user_id)    # Show main menu options 
        else:
            break # Exit loop if login fails


if __name__ == '__main__':
    main()
