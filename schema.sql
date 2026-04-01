PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS userdata (
  userid     INTEGER PRIMARY KEY,
  username   TEXT UNIQUE NOT NULL,
  password   TEXT NOT NULL,
  pfp        BLOB,
  joindate   TEXT
);

CREATE TABLE IF NOT EXISTS posts (
  postid     INTEGER PRIMARY KEY,
  userid     INTEGER NOT NULL,
  title      TEXT,
  content    TEXT,
  timestamp  INTEGER,
  FOREIGN KEY (userid) REFERENCES userdata(userid) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS comments (
  commentid  INTEGER PRIMARY KEY,
  postid     INTEGER NOT NULL,
  userid     INTEGER NOT NULL,
  content    TEXT,
  timestamp  INTEGER,
  FOREIGN KEY (postid) REFERENCES posts(postid) ON DELETE CASCADE,
  FOREIGN KEY (userid) REFERENCES userdata(userid) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS pages (
  pageid     INTEGER PRIMARY KEY,
  visits     INTEGER,
  likes      INTEGER
);
