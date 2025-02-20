#!/usr/bin/python

import sqlite3

conn = sqlite3.connect('./attendance')
print("Opened database successfully")

conn.execute(
    "INSERT INTO student VALUES (1, 'John Doe', 'Web Programming', '2025-02-20 15:43:36')")

conn.commit()
print("Records created successfully")
conn.close()
