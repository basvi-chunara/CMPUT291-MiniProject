"""
File that handles functionality 2, the searching for a user
Author: Fredrik Larida
"""
import sqlite3

# Function to retrieve the tweets and retweets of a user
def user_flwee_tweets(conn, searched_id, offset):
    cur = conn.cursor()
    
    # Query to fetch and retweets of the user, limiting to 3 and starting at whatever offset that is inputted when the function is called
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
                (searched_id, searched_id, offset))
    recent_tweets = cur.fetchall()
    return recent_tweets

# Function to follow a user if they are not already followed
def follow_user(conn, user_id, searched_id):
    cur = conn.cursor()
    try:
        # Preventing the user from following themselves
        if user_id == searched_id:
            print("You cannot follow yourself")
        else:
            # Inserts a row into the follows database
            cur.execute(''' INSERT INTO follows(flwer, flwee, start_date)
                        VALUES (?, ?, DATE('now'))''',
                        (user_id, searched_id))
            conn.commit()
            print("You are now following this user")
    except sqlite3.IntegrityError:
        # Handles the case where the user is already following the perons
        print("You are already following this user.")

# Function to display the details of the searched user
def user_details(conn, searched_id, user_id, user_name):
    # cur = conn.cursor()
    
    # Retrieve stats of the user
    tweet_count, following_count, follower_count = user_stats(conn, searched_id)
    
    tweet_offset = 0
    recent_tweets = user_flwee_tweets(conn, searched_id, tweet_offset)

    # Displaying the details
    print(f"\n{user_name}'s Details:")
    print(f"Tweet count: {tweet_count}")
    print(f"Follows: {following_count}")
    print(f"Followers: {follower_count}")
    
    # Displaying tweets if available
    if not recent_tweets:
        print("No tweets to display")
    else:
        print("\nRecent tweets:")
        for tweet in recent_tweets:
            if tweet[4]:  # If there's a retweeter's name, it's a retweet
                print(f"Retweet Date: {tweet[1]} Time: {tweet[2]}.\n{tweet[4]} retweeted {tweet[3]}'s tweet\n{tweet[0]}\n")
            else:
                print(f"Date: {tweet[1]} Time: {tweet[2]}\n{tweet[3]} tweeted\n{tweet[0]}\n")
    
    # Loop to provide options to follow, see more tweets, or return to search           
    while True:
        print("\nOptions:")
        print("1. Follow this user.")
        print("2. See more tweets.")
        print("3. Go back to search.")
        action = input("Choose an action (1/2/3): ").strip()
        
        if action == '1':
            # Follow the user
            follow_user(conn, user_id, searched_id)
            # Refresh and display the new updated user stats
            tweet_count, following_count, follower_count = user_stats(conn, searched_id)
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
            # Increasing offset to display more tweets
            tweet_offset += 3
            more_tweets = user_flwee_tweets(conn, searched_id, tweet_offset)
            if not more_tweets:
                print("No more tweets to display")
            else:
                for tweet in more_tweets:
                    if tweet[4]:  # If there's a retweeter's name, it's a retweet
                        print(f"\nRetweet Date: {tweet[1]} Time: {tweet[2]}.\n{tweet[4]} retweeted {tweet[3]}'s tweet\n{tweet[0]}\n")
                    else:
                        print(f"\nDate: {tweet[1]} Time: {tweet[2]}\n{tweet[3]} tweeted\n{tweet[0]}\n")
        elif action == '3':
            break
        else:
            print("Invalid action. Please select again")

# Function to retrieve and return a user's tweet count, following count, and followers count
def user_stats(conn, searched_id):
    cur = conn.cursor()

    # Query for the user's tweet and retweet count
    cur.execute(''' SELECT COUNT(*)
                    FROM tweets t
                    LEFT JOIN retweets r ON t.tid = r.tid
                    WHERE t.writer_id = ? OR r.retweeter_id = ?;''',
                    (searched_id, searched_id))
    tweet_count = cur.fetchone()[0]
    
    # Query for the user's following count
    cur.execute(''' SELECT COUNT(*)
                    FROM follows 
                    WHERE flwer = ?;''',
                    (searched_id,))
    following_count = cur.fetchone()[0]

    # Query for the user's follower count
    cur.execute(''' SELECT COUNT(*)
                    FROM follows
                    WHERE flwee = ?;''',
                    (searched_id,))
    follower_count = cur.fetchone()[0]
    
    return tweet_count, following_count, follower_count 
    
# Function to search for a user by keyword and display options
def search_user(conn, user_id):
    cur = conn.cursor()
    search_offset = 0 
    
    user_key = input("\nEnter keyword to search users (or press Enter to cancel): ").lower()
        
    # Handles the search cancellation
    if user_key == '':
        print("Search cancelled\n")
        return  
    
    search_key = f"%{user_key}%"
    
    while True:
        # Query to search for users matching the keyword, ordered by name length
        cur.execute(''' SELECT u.usr, u.name 
                        FROM users u
                        WHERE lower(u.name) LIKE ?
                        ORDER BY LENGTH(u.name) ASC
                        LIMIT 5 OFFSET ?''',
                        (search_key, search_offset))
        results = cur.fetchall()
        
        # Displaying the search results
        if results:
            print("\n=================Search results=================")
            for search_num, (searched_id, searched_name) in enumerate(results, 1):
                print(f"{search_num}. Name: {searched_name}    ID:{searched_id}")
        else:
            print(f"No users that has '{user_key}' in their username")
            break
        
        # Provide options for more results or selecting a user by number    
        if len(results) < 5:
            print("End of search results")
            print("\nSelect a user in current list by number (not ID) to see more details or type 'exit' to go back to main menu")
            choice = input("Select your choice: ").strip().lower()
        else:
            print("Select a user in current list by number (not ID) to see more details, or type 'more' to see more followers, or 'exit' to go back to main menu")
            choice = input("Select your choice: ").strip().lower()   
        
        if choice == 'more':
            # Increasing the offset for next set of results 
            search_offset += 5
            
        elif choice.isdigit():
            choice = int(choice) - 1
            if 0 <= choice < len(results):
                user_details(conn, results[choice][0], user_id, results[choice][1])
            else:
                print("Invalid choice")     
        elif choice == 'exit':
            break
        else:
            print("Invalid input.")
                
            
            
            
            
            
