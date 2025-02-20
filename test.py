#!/usr/bin/python

import sqlite3

conn = sqlite3.connect('./attendance.db')
cur = conn.cursor()
print("Opened database successfully")

cur.execute(
    "INSERT INTO student VALUES (2, 'John Doe', 'Web Programming', '2025-02-20 15:43:36', 2)")

conn.commit()
print("Records created successfully")
conn.close()
