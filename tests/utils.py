
import sqlite3
import random
import datetime
import tempfile
from faker import Faker
import os 

def generate_fake_duckdb():
	filename =  tempfile.mkstemp(prefix="sqlite2duckdb_duck", suffix=".duckdb")[1]
	if os.path.exists(filename):
		os.remove(filename)

	return filename

def generate_fake_sqlite():
	
	temp_file_path = tempfile.mkstemp(prefix="sqlite2duckdb", suffix=".sqlite")[1]
	print(f"Create temp sqlite db at {temp_file_path}")
	fake = Faker()

	conn = sqlite3.connect(temp_file_path)
	cursor = conn.cursor()

	# Create sqlite database 
	cursor.execute('''
	    CREATE TABLE IF NOT EXISTS data (
	        id INTEGER PRIMARY KEY,
	        integer_col INTEGER,
	        real_col REAL,
	        text_col TEXT,
	        boolean_col BOOLEAN,
	        date_col DATE,
	        time_col TIME,
	        datetime_col DATETIME,
	        blob_col BLOB,
	        numeric_col NUMERIC,
	        null_col NULL
	    )
	''')

	# Generate fake data 
	def generate_fake_data():
	    integer_col = random.randint(1, 1000)
	    real_col = random.uniform(1.0, 1000.0)
	    text_col = fake.text(max_nb_chars=20)
	    boolean_col = random.choice([True, False])
	    date_col = fake.date()
	    time_col = fake.date_time()
	    datetime_col = fake.date_time()
	    blob_col = fake.binary(length=10)
	    numeric_col = random.choice([integer_col, real_col])
	    null_col = None
	    return (integer_col, real_col, text_col, boolean_col, date_col, time_col, datetime_col, blob_col, numeric_col, null_col)


	for _ in range(1000):

	    cursor.execute('''
	        INSERT INTO data (integer_col, real_col, text_col, boolean_col, date_col, time_col, datetime_col, blob_col, numeric_col, null_col)
	        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
	    ''', generate_fake_data())

	# Sauvegarde (commit) des changements et fermeture de la connexion
	conn.commit()
	conn.close()

	return temp_file_path
