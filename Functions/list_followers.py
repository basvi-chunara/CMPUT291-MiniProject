"""
File that handles the 4th functionality of the program, displaying the followers list.
It also allows the user to choose one of their followers to see their stats and allows them to follow them
Author: Fredrik Larida
"""

import sqlite3

# Function that returns the tweets of follower that the user chooses when looking at following list
def follower_tweets(conn, follower_id, offset):
    cur = conn.cursor()
    
    cur.execute(''' SELECT 
                    t.text, 
                    t.tdate AS tweet_date, 
                    t.ttime AS tweet_time,
                    u.name AS original_author,
                    NULL AS retweeted_by
                FROM tweets t
                JOIN users u ON u.usr = t.writer_id
                WHERE writer_id = ?
                
                UNION ALL
                
                SELECT 
                    t.text,
                    r.rdate AS tweet_date,
                    NULL AS tweet_time,
                    u.name AS original_author,
                    rt.name AS retweeted_by
                FROM retweets r
                JOIN tweets t ON t.tid = r.tid
                JOIN users u ON u.usr = t.writer_id
                JOIN users rt ON rt.usr = r.retweeter_id
                WHERE retweeter_id = ?
                
                ORDER by tdate DESC, ttime DESC
                LIMIT 3 OFFSET ?''',
                (follower_id, follower_id, offset))
    recent_tweets = cur.fetchall()
    return recent_tweets

# Function that handles the procces of following the follower that the user chooses
def follow_follower(conn, user_id, follower_id):
    cur = conn.cursor()
    try:
        # This allows the follower to be followed as long as the user is not following them yet
        cur.execute(''' INSERT INTO follows(flwer, flwee, start_date)
                    VALUES (?, ?, DATE('now'))''',
                    (user_id, follower_id))
        conn.commit()
        print("You are now following this user")
    except sqlite3.IntegrityError:
        # Checks if the user is already following this person. If they are the following message pops up
        print("You are already following this user.")
    
def user_details(conn, follower_id):
    # This function queries and returns the follower's tweet count, following count, and the amount of followers they have
    cur = conn.cursor()

    # Query for counting the amount of tweets and retweets they made
    cur.execute(''' SELECT COUNT(*)
                    FROM tweets t
                    LEFT JOIN retweets r ON t.tid = r.tid
                    WHERE t.writer_id = ? OR r.retweeter_id = ?;''',
                    (follower_id,follower_id))
    tweet_count = cur.fetchone()[0]

    # Query that counts how many accounts they follow
    cur.execute(''' SELECT COUNT(*)
                    FROM follows 
                    WHERE flwer = ?;''',
                    (follower_id,))
    following_count = cur.fetchone()[0]

    # Query that counts how many followers they have
    cur.execute(''' SELECT COUNT(*)
                    FROM follows
                    WHERE flwee = ?;''',
                    (follower_id,))
    follower_count = cur.fetchone()[0]
    
    return tweet_count, following_count, follower_count

def follower_details(conn, follower_id, user_id, user_name):
    # This function prints the details of a follower if they are selected
    # cur = conn.cursor()
    
    # Retrieving the stats
    tweet_count, following_count, follower_count = user_details(conn, follower_id)
    
    # Starting from the top of the table
    offset = 0

    # Calling on the function to retrievce the recent tweets
    recent_tweets = follower_tweets(conn, follower_id, offset)

    # Displaying the details
    print(f"\n{user_name}'s Details:")
    print(f"Tweet count: {tweet_count}")
    print(f"Follows: {following_count}")
    print(f"Followers: {follower_count}")
    
    
    if not recent_tweets:
        # If they do not have any tweets
        print("No tweets to display")
    else:
        # If they do have recent tweets
        print("\nRecent tweets:")
        for tweet in recent_tweets:
            if tweet[4]:  # If there's a retweeter's name, it's a retweet
                print(f"Retweet Date: {tweet[1]} Time: {tweet[2]}\n{tweet[4]} retweeted {tweet[3]}'s tweet\n{tweet[0]}\n")
            else:
                print(f"Date: {tweet[1]} Time: {tweet[2]}\n{tweet[3]} tweeted\n{tweet[0]}\n")
    
    # Displays options to follow, see more tweets, or go back to followers            
    while True: 
        
        print("\nOptions:")
        print("1. Follow this user.")
        print("2. See more tweets.")
        print("3. Go back to followers list.")
        action = input("Choose an action (1/2/3): ").strip()
        
        if action == '1':
            # Follow the selected follower
            follow_follower(conn, user_id, follower_id)
            # Refresh and display the updated follower stats
            tweet_count, following_count, follower_count = user_details(conn, follower_id)
            print(f"\n{user_name}'s Details:")
            print(f"Tweet count: {tweet_count}")
            print(f"Follows: {following_count}")
            print(f"Followers: {follower_count}")
            if not recent_tweets:
                print("No tweets to display")
            else:
                print("\nRecent tweets:")
                for tweet in recent_tweets:
                    if tweet[4]:  # If there's a retweeter's name, it's a retweet
                        print(f"Retweet Date: {tweet[1]} Time: {tweet[2]}.\n{tweet[4]} retweeted {tweet[3]}'s tweet\n{tweet[0]}\n")
                    else:
                        print(f"Date: {tweet[1]} Time: {tweet[2]}\n{tweet[3]} tweeted\n{tweet[0]}\n")
        elif action == '2':
            # Increase the offset and displays more tweets
            offset += 3
            more_tweets = follower_tweets(conn, follower_id, offset)
            if not more_tweets:
                print("\nNo more tweets to display")
            else:
                for tweet in more_tweets:
                    if tweet[4]:  # If there's a retweeter's name, it's a retweet
                        print(f"\nRetweet Date: {tweet[2]} Time: {tweet[2]}\n{tweet[4]} retweeted {tweet[3]}'s tweet\n{tweet[0]}\n")
                    else:
                        print(f"\nDate: {tweet[1]} Time: {tweet[2]}\n{tweet[3]} tweeted\n{tweet[0]}\n")
                
        elif action == '3':
            break # Go back to followers list
        else:
            print("Invalid action. Please select again")
            
# Function to display the list of followers with options to view a specific follower's details, see more followers, or exit        
def followers_list(conn, user_id):
    cur = conn.cursor()
    
    offset = 0
    while True:
        # Query to get the list of followers for the user
        cur.execute(''' SELECT u.usr, u.name
                        FROM users u
                        JOIN follows f ON u.usr = f.flwer
                        WHERE f.flwee = ?
                        LIMIT 5 OFFSET ?; ''',
                        (user_id, offset))
        followers = cur.fetchall()
        
        if followers:
            print("\n=================Followers=================")
            for flwer_num, (follower_id, follower_name) in enumerate(followers, 1):
                print(f"{flwer_num}. {follower_name}")
        else:
            print("\nYou do not have any follwoers")
            break
        
        # Display prompt based on the number of followers in the list
        if len(followers) < 5:
            # If less than 5 on the list, immediately asks them to either choose a follower or exit
            print("End of followers list\n")
            print("Select a follower in current list by number to see more details or type 'exit' to go back to main menu")
            choice = input("Select your choice: ").strip().lower()
        else:
            print("Select a follower in current list by number to see more details, or type 'more' to see more followers, or 'exit' to go back to main menu")
            choice = input("Select your choice: ").strip().lower()

        if choice == 'more':
            offset += 5 # Increasing the offset to fetch more followers
            continue
        elif choice.isdigit():
            # The proccess of choosing a follower and seeing their stats
            choice = int(choice) - 1
            if 0 <= choice < len(followers):
                follower_details(conn, followers[choice][0], user_id, followers[choice][1])
            else:
                print("Invalid choice.") # If the user enters a number that is not displayed
        elif choice == 'exit':
            break # Go back to the menu
        else:
            print("Invalid input.") # If the user chooses an incorrect input
