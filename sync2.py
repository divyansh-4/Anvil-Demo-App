import anvil.server
import sqlite3
import anvil.server
from datetime import datetime

ANVIL_UPLINK_KEY = "server_EUULOP6PWUBMCRVWHL6SUTVD-LYUQJELFCMQWM33V"
anvil.server.connect(ANVIL_UPLINK_KEY)

conn = sqlite3.connect("movies.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    movie_name TEXT NOT NULL,
    year INTEGER NOT NULL,
    director TEXT NOT NULL,
    summary TEXT NOT NULL
);
''')
conn.commit()

@anvil.server.callable
def add_movie2(movie_data):
    """
    Adds a new movie to the SQLite database, preventing duplicates.
    """
    # print("adding")
    # print(movie_data)
    if movie_data.get('movie_name') and movie_data.get('year') and movie_data.get('director') and movie_data.get('summary'):
        try:
            cursor.execute(
                "INSERT INTO movies (movie_name, year, director, summary) VALUES (?, ?, ?, ?)",
                (movie_data['movie_name'], movie_data['year'], movie_data['director'], movie_data['summary'])
            )
            conn.commit()
            return "Movie added successfully"
        except sqlite3.IntegrityError:
            return "Movie already exists in the database"

@anvil.server.callable
def update_movie2(movie, movie_data):
    """
    Updates an existing movie in the database, searching by movie_name, year, and director.
    """

    if movie_data.get('movie_name') and movie_data.get('year') and movie_data.get('director') and movie_data.get('summary'):
        cursor.execute(
            """UPDATE movies 
               SET summary = ?, movie_name = ?, year = ?, director = ?
               WHERE movie_name = ? AND year = ? AND director = ?""",
            (movie_data['summary'], movie_data['movie_name'], movie_data['year'], movie_data['director'],
             movie["movie_name"], movie["year"], movie["director"])
        )
        conn.commit()
        
        if cursor.rowcount == 0:
            print("No matching movie found in SQLite")
            return "No matching movie found in SQLite"
        
        print("Movie updated successfully")
        return "Movie updated successfully"

    return "Invalid movie data"


@anvil.server.callable
def delete_movie2(movie):
    """
    Deletes a movie from the database based on movie_name, year, and director.
    """
    print(movie,"**********************************")
    cursor.execute(
        "DELETE FROM movies WHERE movie_name = ? AND year = ? AND director = ?",
        (movie["movie_name"], movie["year"], movie["director"])
    )
    conn.commit()
    return "Movie deleted successfully"

anvil.server.wait_forever()
