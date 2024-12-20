"""
Complimentary file that contains the displaying of tweets on the main feed. On seperate file just for better readability
Author: Fredrik Larida
"""

import sqlite3

def tweet_display(conn, user_id):
    cur = conn.cursor()
    offset = 0

    while True:
        # Query that returns all the tweets and retweets made by the users that has the current user as the follower
        # Use UNION to combine tweets and retweets with tweet_date for sorting
        cur.execute('''
            SELECT 
                t.tdate AS tweet_date,
                t.ttime AS tweet_time,
                u.name AS original_author,
                t.text,
                NULL AS retweeted_by,
                t.tid AS tweet_id
            FROM follows f
            JOIN tweets t ON t.writer_id = f.flwee
            JOIN users u ON u.usr = t.writer_id
            WHERE f.flwer = ?

            UNION ALL

            SELECT 
                r.rdate AS tweet_date,
                t.ttime AS tweet_time,
                u.name AS original_author,
                t.text,
                rt.name AS retweeted_by,
                t.tid AS tweet_id
            FROM follows f
            JOIN retweets r ON r.retweeter_id = f.flwee
            JOIN tweets t ON t.tid = r.tid
            JOIN users u ON u.usr = t.writer_id
            JOIN users rt ON rt.usr = r.retweeter_id
            WHERE f.flwer = ?

            ORDER BY tweet_date DESC, tweet_time DESC
            LIMIT 5 OFFSET ?;
        ''', (user_id, user_id, offset))

        tweets = cur.fetchall()
        
        # If the query returns and there are no tweets
        if not tweets:
            print("No tweets to display. Start following users to see more.")
            break
        
        print("\n=================Main feed=================")
        
        # The displaying of the tweets
        # while True:
        for tweet in tweets:
            if tweet[4]:  # If there's a retweeter's name, it's a retweet
                print(f"Retweet Date: {tweet[0]} Time: None TID: {tweet[5]}\n{tweet[4]} retweeted {tweet[2]}'s tweet\n{tweet[3]}\n")
            else:
                print(f"Date: {tweet[0]} Time: {tweet[1]} TID: {tweet[5]}\n{tweet[2]} tweeted\n{tweet[3]}\n")

        # Check if there are fewer than 5 tweets to determine if we reached the end
        if len(tweets) < 5:
            print("No additional tweets to display.")
            break

        # Prompt to see more tweets or go to the main menu
        
        next_action = input("Enter 'menu' to go to the main menu or 'more' to see more tweets: ").strip().lower()
        print("\n")
        if next_action == 'menu':
            return True
        elif next_action == 'more':
            offset += 5
        else:
            print("Invalid choice. Please choose again")
            break
