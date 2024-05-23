import sqlite3 
import duckdb 
from tests import utils
import os 

from sqlite2duckdb.__main__ import sqlite_to_duckdb

def test_conversion():

	duckdb_path = utils.generate_fake_duckdb()
	sqlite_path = utils.generate_fake_sqlite()

	sqlite_to_duckdb(sqlite_path, duckdb_path)

	
	

	
	
	
