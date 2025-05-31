#!/bin/bash  
echo "Deleting old Database"  
rm -rf ./database.sqlite3
echo "Creating new Database"
sqlite3 database.sqlite3 < projectSchema.sql
echo "Inserting data"
python3 insertScript.py
echo "Running database manipulator"
python3 databaseManipulator.py
