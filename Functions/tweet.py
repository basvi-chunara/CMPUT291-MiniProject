"""
File that handles functionality 3, the composing of tweets and reply tweets
Author: Annie Ding
"""

import datetime

def make_tweet(conn, user, replyto_tid):
    cur = conn.cursor()
    t_info = {"tid": None, "writer_id": user, "text": None, "tdate": None, "ttime": None, "replyto_tid": replyto_tid}
    user_tweet = input("Enter tweet: ") # get the text, date, and time of the tweet
    t_dtime = datetime.datetime.now()
    t_tokens = user_tweet.split()
    if (len(t_tokens) == 0): # check if the tweet is empty
        print("Invalid tweet.")
        return
    mentioned_tags = []

    for token in t_tokens: # validate if the hashtags are valid and get all hashtags
        if token == "#":
            print("Invalid hashtag.")
            return
        if token[0] == "#":
            mentioned_tags.append(token)
    
    if (len(mentioned_tags) > len(set(tweet.lower() for tweet in mentioned_tags))): # check if a hashtag is repeated
        print("Invalid tweet - repeated hashtags.")
        return
    
    t_info["tdate"] = f"{t_dtime.year}-{t_dtime.month}-{t_dtime.day}"
    t_info["ttime"] = f"{t_dtime.hour}:{t_dtime.minute}:{t_dtime.second:0>2d}"
    t_info["text"] = user_tweet
    cur.execute("SELECT MAX(tid) FROM tweets;") #get max tweet id then add 1 for unique id
    t_info["tid"] = cur.fetchone()[0] + 1

    # add tweet to database
    cur.execute('''INSERT INTO tweets(tid, writer_id, text, tdate, ttime, replyto_tid) VALUES (?, ?, ?, ?, ?, ?);''', (t_info['tid'], t_info['writer_id'], t_info['text'], t_info['tdate'], t_info['ttime'], t_info['replyto_tid']))
    conn.commit()
    for tag in mentioned_tags: # add the mentioned tags to approrpriate table
        cur.execute('''INSERT INTO hashtag_mentions(tid, term) VALUES (?, ?);''', (t_info['tid'], tag))
        conn.commit()
    
    print("Successfully tweeted!")
    return

    