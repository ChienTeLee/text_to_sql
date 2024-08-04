import json
import sqlite3
from pathlib import Path


def create_db(database_names):
    # get spider sql files
    sql_files = [Path("./dataset/spider/database").joinpath(name).joinpath("schema.sql") for name in database_names]

    # create db
    con = sqlite3.connect("spider.db")
    cur = con.cursor()
    for f in sql_files:
        with open(f, 'r') as file:
            sql_text = file.read()
            cur.executescript(sql_text)
    con.commit()

    # check
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cur.fetchall()
    if tables:
        print("Tables in the database:")
        for table in tables:
            print(table[0])
    else:
        print("No table found")
    
    # close db
    con.close()



def create_metadata(database_names):
    # create table metadata
    with open("./dataset/spider/tables.json", 'r') as file:
        data = json.load(file)
    data = [x for x in data if x["db_id"] in database_names]
    with open("table_schema.txt", 'w') as file:
        json.dump(data, file, indent=4)


def main():
    database_names = ["department_management", "farm", "student_assessment"]
    create_db(database_names)
    create_metadata(database_names)


if __name__ == "__main__":
    main()