"""
Function that handles functionality 1, the searching of a tweet and searching of a hashtag
Author: Basvi Chunara
"""

import sqlite3
from tweet import make_tweet  # Importing make_tweet function

def validate_keywords(keywords):
    # Spliting the keywords by commas and remove extra spaces
    keyword_list = [kw.strip().lower() for kw in keywords.split(",")]
    
    # Checking for duplicate hashtags (case-insensitive)
    hashtags = {kw.lower() for kw in keyword_list if kw.startswith("#")}
    if len(hashtags) != sum(1 for kw in keyword_list if kw.startswith("#")):
        return False, "Duplicate hashtags are not allowed."
    
    # Checking if there are commas without spaces by comparing lengths
    if len(keyword_list) != len(keywords.split(",")):
        return False, "Each comma should be followed by a space."

    return True, keyword_list
def search_tweets(conn, keywords, page=1):
    query = """
    SELECT tweets.tid, tweets.writer_id, tweets.text, tweets.tdate, tweets.ttime 
    FROM tweets
    LEFT JOIN hashtag_mentions ON tweets.tid = hashtag_mentions.tid
    WHERE
        ((' ' || LOWER(tweets.text) || ' ') LIKE '% ' || ? || ' %' AND ? NOT LIKE '#%')
        OR (LOWER(hashtag_mentions.term) = ? AND ? LIKE '#%')
        OR (LOWER(hashtag_mentions.term) = ?)
    ORDER BY tweets.tdate DESC, tweets.ttime DESC
    LIMIT 5 OFFSET ?; 
    """ 
    
    tweets = []
    offset = (page - 1) * 5
    for keyword in keywords:
        var_hash="#"+keyword
        cursor = conn.execute(query, (keyword.strip("#"), keyword, keyword, keyword,var_hash, offset))
        tweets += cursor.fetchall()
    
    return tweets

def get_tweet_stats(conn, tid):
    # statistics retrieval for retweets and replies
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM retweets WHERE tid = ?", (tid,))
    retweets_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM tweets WHERE replyto_tid = ?", (tid,))
    replies_count = cur.fetchone()[0]
    return retweets_count, replies_count

def compose_reply(conn, user_id, original_tid):
    
    
    print("\nCompose your reply:")
    
    make_tweet(conn, user_id, original_tid)  # Calling make_tweet with the original tweet ID as replyto_tid
    print("Reply posted successfully.")
def retweet(conn, user_id, original_tid):
    cur = conn.cursor()
    
    # Fetching the original tweet's details to ensure it exists and to identify the original writer
    cur.execute("SELECT writer_id, text FROM tweets WHERE tid = ?", (original_tid,))
    original_tweet = cur.fetchone()
    
    if original_tweet:
        writer_id, original_text = original_tweet
        print("\nRetweeting the following:")
        print(f"Original Tweet: {original_text}")

        # Checking if the user has already retweeted this tweet
        cur.execute("SELECT spam FROM retweets WHERE tid = ? AND retweeter_id = ?", (original_tid, user_id))
        retweet_entry = cur.fetchone()
        if retweet_entry:
            # If a retweet already exists, setting spam to 1
            print("You cannot retweet more than once.")
            cur.execute(
                "UPDATE retweets SET spam = 1 WHERE tid = ? AND retweeter_id = ?",
                (original_tid, user_id)
            )
            conn.commit()  # Committing the changes
            print("Retweet marked as spam.")
        else:
            try:
                # Inserting the retweet into the retweets table
                cur.execute(
                    "INSERT INTO retweets (tid, retweeter_id, writer_id, spam, rdate) VALUES (?, ?, ?, 0, DATE('now'))",
                    (original_tid, user_id, writer_id)
                )
                conn.commit()  # Committing the transaction to save the retweet
                print("Retweet posted successfully.")

            except sqlite3.IntegrityError:
                # This error will occur if the retweeter has already retweeted this tweet
                print("You have already retweeted this tweet.")
    else:
        print("Original tweet not found.")

def show_tweets(conn, keywords, user_id):
    # Validate keywords input
    is_valid, keyword_list_or_error = validate_keywords(keywords)
    if not is_valid:
        print("Error:", keyword_list_or_error)
        return
    page = 1

    while True:
        # Fetching tweets based on keywords and current page
        tweets = search_tweets(conn, keyword_list_or_error, page)
        
        if not tweets:
            print("No tweets found.")
            break

        # Displaying tweets with index numbers for selection
        print("\nTweet Results:")
        for idx, tweet in enumerate(tweets, 1):
            print(f"{idx}. Tweet ID: {tweet[0]}, Writer ID: {tweet[1]}")
            print(f"   Text: {tweet[2]}")
            print(f"   Date: {tweet[3]}, Time: {tweet[4]}")
            print("-----------")

        # Prompting the user to select a tweet by number or paginate
        if len(tweets) < 5:
            print("End of search results")
            choice = input("\nSelect a tweet by number to view statistics, or type 'exit' to go back: ").strip().lower()
        else:
            choice = input("\nSelect a tweet by number to view statistics, 'more' to see more tweets, or 'exit' to go back: ").strip().lower()

        if choice == 'more':
            page += 1  # Incrementing page to fetch the next set of tweets
            continue
        elif choice.isdigit():
            selected_index = int(choice) - 1
            if 0 <= selected_index < len(tweets):
                selected_tweet_id = tweets[selected_index][0]
                # Retrieving and display tweet statistics
                stats = get_tweet_stats(conn, selected_tweet_id)
                print(f"\nTweet Statistics:")
                print(f"Retweets: {stats[0]}, Replies: {stats[1]}")
                # Prompting the user for additional actions on the tweet
                action = input("Enter 'reply' to reply, 'retweet' to retweet, or 'back' to return to tweet list: ").strip().lower()
                
                if action == 'reply':
                    compose_reply(conn, user_id, selected_tweet_id)
                elif action == 'retweet':
                    retweet(conn, user_id, selected_tweet_id)
                elif action == 'back':
                    continue
                else:
                    print("Invalid choice.")
            else:
                print("Invalid choice. Please select a valid tweet number.")
        elif choice == 'exit':
            break
        else:
            print("Invalid input.")
