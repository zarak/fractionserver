import sqlite3

connection = sqlite3.connect('data.db')
cursor = connection.cursor()

create_table = "CREATE TABLE IF NOT EXISTS articles (id INTEGER PRIMARY KEY, feed text, date text, url text, title text, description text)"
cursor.execute(create_table)

connection.commit()
connection.close()
