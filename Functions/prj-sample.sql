PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE tweets (
    tid         int,
    writer_id   int,
    text        text,
    tdate       date, 
    ttime       time,
    replyto_tid int,
    PRIMARY KEY (tid),
    FOREIGN KEY (writer_id) REFERENCES users(usr) ON DELETE CASCADE,
    FOREIGN KEY (replyto_tid) REFERENCES tweets(tid) ON DELETE CASCADE
);
INSERT INTO tweets VALUES(101,1,'John talks about database management #Database','2024-10-20','09:00:00',NULL);
INSERT INTO tweets VALUES(102,2,'Emma replies to John''s thoughts #ReplyToJohn','2024-10-21','10:00:00',101);
INSERT INTO tweets VALUES(103,3,'Leo comments on the CMPUT291 project #CMPUT291Project','2024-10-22','11:00:00',NULL);
CREATE TABLE retweets (
    tid         int,
    retweeter_id   int, 
    writer_id      int, 
    spam        int,
    rdate       date,
    PRIMARY KEY (tid, retweeter_id),
    FOREIGN KEY (tid) REFERENCES tweets(tid) ON DELETE CASCADE,
    FOREIGN KEY (retweeter_id) REFERENCES users(usr) ON DELETE CASCADE,
    FOREIGN KEY (writer_id) REFERENCES users(usr) ON DELETE CASCADE
);
INSERT INTO retweets VALUES(101,2,1,0,'2024-10-25');
INSERT INTO retweets VALUES(103,1,3,1,'2024-10-25');
CREATE TABLE hashtag_mentions (
    tid         int,
    term        text,
    PRIMARY KEY (tid, term),
    FOREIGN KEY (tid) REFERENCES tweets(tid) ON DELETE CASCADE
);
INSERT INTO hashtag_mentions VALUES(101,'#Database');
INSERT INTO hashtag_mentions VALUES(102,'#ReplyToJohn');
INSERT INTO hashtag_mentions VALUES(103,'#CMPUT291Project');
CREATE TABLE users (
    usr         int PRIMARY KEY,
    name        text,
    email       text,
    phone       int,
    pwd         text
);
INSERT INTO users VALUES(1,'John','john@example.com',1234567891,'pass1');
INSERT INTO users VALUES(2,'Emma','emma@example.com',9876543212,'pass2');
INSERT INTO users VALUES(3,'Leo','leo@example.com',5432167893,'pass3');
CREATE TABLE follows (
    flwer       int,
    flwee       int,
    start_date  date,
    PRIMARY KEY (flwer, flwee),
    FOREIGN KEY (flwer) REFERENCES users(usr) ON DELETE CASCADE,
    FOREIGN KEY (flwee) REFERENCES users(usr) ON DELETE CASCADE
);
INSERT INTO follows VALUES(1,2,'2023-01-20');
INSERT INTO follows VALUES(2,3,'2023-02-14');
INSERT INTO follows VALUES(3,1,'2023-03-01');
CREATE TABLE lists (
    owner_id    int,
    lname       text,
    PRIMARY KEY (owner_id, lname),
    FOREIGN KEY (owner_id) REFERENCES users(usr) ON DELETE CASCADE
);
INSERT INTO lists VALUES(1,'Favorites');
INSERT INTO lists VALUES(2,'ProjectIdeas');
INSERT INTO lists VALUES(3,'ToDoList');
CREATE TABLE include (
    owner_id    int,
    lname       text,
    tid         int,
    PRIMARY KEY (owner_id, lname, tid),
    FOREIGN KEY (owner_id, lname) REFERENCES lists(owner_id, lname) ON DELETE CASCADE,
    FOREIGN KEY (tid) REFERENCES tweets(tid) ON DELETE CASCADE
);
INSERT INTO include VALUES(1,'Favorites',101);
INSERT INTO include VALUES(2,'ProjectIdeas',102);
INSERT INTO include VALUES(3,'ToDoList',103);
COMMIT;
