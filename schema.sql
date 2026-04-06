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

CREATE TABLE IF NOT EXISTS page_stats (
  statid      INTEGER PRIMARY KEY,
  target_type TEXT NOT NULL CHECK(target_type IN ('user','post')),
  target_id   INTEGER NOT NULL,
  visits      INTEGER NOT NULL DEFAULT 0,
  likes       INTEGER NOT NULL DEFAULT 0,
  UNIQUE(target_type, target_id)
);

CREATE TABLE IF NOT EXISTS page_likes (
  likeid      INTEGER PRIMARY KEY,
  userid      INTEGER NOT NULL,
  target_type TEXT NOT NULL CHECK(target_type IN ('user','post')),
  target_id   INTEGER NOT NULL,
  created     TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(userid, target_type, target_id),
  FOREIGN KEY(userid) REFERENCES userdata(userid) ON DELETE CASCADE
);