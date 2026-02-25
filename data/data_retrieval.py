"""
Goal: Query my database for some filepaths, confirm their existence.
"""
import sqlite3

def main():
    # Connect to database.
    # Get data. 
    # Close connection. 
    # Check for files. 
    statement = "SELECT * FROM dev_Files WHERE TRUE;"
    conn = None

    try:
        conn = sqlite3.connect("songs.db")
        cur = conn.cursor()
        res = cur.execute(statement).fetchall()
        print(res)
    
    except:
        print(f'An error occured during statement execution:\n    {statement}')
        if (conn != None): conn.close()
        return
    
    # Check for files existence. 
    try:
        for record in res:
            with open(record[2], "r") as file:
                if file:
                    print("file exists")
    finally:
        cur.close()
        conn.close()

    
    

if __name__ == "__main__":
    main()
