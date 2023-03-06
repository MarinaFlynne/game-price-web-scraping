#!/usr/bin/env python
"""
This is a small program that automates the creation of an initial database
"""
import sqlite3
import os

DATABASE_FILENAME = "games.db"


def main():
    """
    Main function of the program
    """
    # Check if database already exists
    connection = sqlite3.connect(DATABASE_FILENAME)
    cursor = connection.cursor()
    if os.path.exists(DATABASE_FILENAME):
        print("Database exists already")

        # get every table in database and print the name of the table along with the number of rows
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_list = cursor.fetchall()
        for table in table_list:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            row_count = cursor.fetchone()[0]
            print(f"Database contains table '{table_name}' with {row_count} rows.")

        # get input from user
        prompt = "Would you like to erase database and create a new one? (y/n): "
        answer = input(prompt).lower()
        if answer == "y" or "yes":
            # delete database and create new one
            connection.close()
            os.remove(DATABASE_FILENAME)
            print(f"Deleted database '{DATABASE_FILENAME}'.")
        else:
            print("Exited database setup.")
            return

    # create database
    connection = sqlite3.connect(DATABASE_FILENAME)
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE games (title VARCHAR, link VARCHAR, price INT, used_price INT);")
    connection.commit()
    connection.close()
    print(f"Created database '{DATABASE_FILENAME}'.")


if __name__ == "__main__":
    main()
