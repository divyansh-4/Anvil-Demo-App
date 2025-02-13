import anvil.server
import sqlite3
import json
# Replace with your Uplink key
UPLINK_KEY = "server_EUULOP6PWUBMCRVWHL6SUTVD-LYUQJELFCMQWM33V"
DB_PATH = "movies2.db"

# Connect to Anvil's Uplink
anvil.server.connect(UPLINK_KEY)

def get_connection():
    """Returns a new connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # To allow dict-like row access
    return conn

def get_id_field(table_name):
    """Returns the unique identifier field based on the table name."""
    id_field = {
        'candidates': 'uid',
        'org': 'proj_uid',
        'projects': 'uid',
        'users': 'email',
        'candidateprojectmapping': 'candidate_uid',
        'projectrecord': 'candidate_uid',
        'questions': 'uid'
    }
    return id_field.get(table_name, 'id')

@anvil.server.callable
def fetch_all_rows(table_name):
    """Fetches all rows from the given table."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table_name}")
    rows = cur.fetchall()
    print(f"SELECT * FROM {table_name}")
    print([dict(row) for row in rows])
    return [dict(row) for row in rows]

@anvil.server.callable
def add_row(table_name, **kwargs):
    """Adds a new row to the given table."""
    conn = get_connection()
    columns = ', '.join(kwargs.keys())
    placeholders = ', '.join('?' for _ in kwargs)

    for value in values:
        if isinstance(value, (dict, list)):
            value = json.dumps(value)

    values = tuple(kwargs.values())
    
    query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

    print(f"Executing query {query} with values {values}")

    cur = conn.cursor()
    cur.execute(query, values)
    conn.commit()
    return cur.lastrowid

@anvil.server.callable
def update_row(table_name, primary_key, **new_data):
    """
    Updates all columns of an existing row identified by its primary key,
    serializing any complex data types like lists or dictionaries.
    """
    conn = get_connection()
    print(new_data)

    # id_field = get_id_field(table_name) # ORIGINAL
    ### GS MODIFICATION FOR COMPOSITE PRIMARY KEY
    if type(primary_key) is str:
        id_field = f'{get_id_field(table_name)} =?'
        primary_key_values=primary_key
    elif type(primary_key) is dict:
        id_field=' AND '.join([f'{k} = ?' for k in primary_key])
        primary_key_values=[primary_key[k] for k in primary_key]
    
    try:
        cur = conn.cursor()

        # Get all columns dynamically
        cur.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cur.fetchall()]  # Column names are in the second field
        
        print(columns)
        
        # Prepare update query dynamically
        updates = []
        values = []

        for column in columns[1:]:  # Skip the first column (assumed primary key)
            if column in new_data:
                value = new_data[column]

                # Serialize complex types like lists or dictionaries
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)

                updates.append(f"{column} = ?")
                values.append(value)

        # Build the query
        # query = f"UPDATE {table_name} SET {', '.join(updates)} WHERE {id_field} = ?" # ORIGINAL
        #### GS MODIFICATION FOR COMPOSITE PRIMARY KEY
        query = f"UPDATE {table_name} SET {', '.join(updates)} WHERE {id_field}"
        # values.append(primary_key) # ORIGINAL
        #### GS MODIFICATION FOR COMPOSITE PRIMARY KEY
        if type(primary_key) is str:
            values.append(primary_key_values)
        elif type(primary_key) is dict:
            values+=primary_key_values

        # Debug log
        print(f"Executing Query: {query} | Values: {values}")

        # Execute the query
        cur.execute(query, values)
        conn.commit()
        print("Row updated successfully.")

    except Exception as e:
        print(f"Error while updating row: {e}")
        raise
    finally:
        conn.close()


@anvil.server.callable
def delete_row(table_name, primary_key):
    """Deletes a row by its unique identifier (primary key)."""
    conn = get_connection()
    # id_field = get_id_field(table_name)
    ### GS MODIFICATION FOR COMPOSITE PRIMARY KEY
    if type(primary_key) is str:
        id_field = f'{get_id_field(table_name)} =?'
        primary_key_values=primary_key
    elif type(primary_key) is dict:
        id_field=' AND '.join([f'{k} = ?' for k in primary_key])
        primary_key_values=[primary_key[k] for k in primary_key]
    
    query = f"DELETE FROM {table_name} WHERE {id_field} = ?"
    #### GS MODIFICATION FOR COMPOSITE PRIMARY KEY
    #### GS MODIFICATION FOR COMPOSITE PRIMARY KEY
    values=[]
    if type(primary_key) is str:
        values.append(primary_key_values)
    elif type(primary_key) is dict:
        values+=primary_key_values

    query = f"DELETE FROM {table_name} WHERE {id_field}"
    print("Executing DELETE Query:", query)  # Log the query for debugging
    print("With key:", primary_key_values)  # Log the row ID
    cur = conn.cursor()
    cur.execute(query,values)
    conn.commit()

@anvil.server.callable
def get_row_by_id(table_name, primary_key):
    """Fetches a row by its unique identifier (primary key)."""
    conn = get_connection()
    # id_field = get_id_field(table_name)
    ### GS MODIFICATION FOR COMPOSITE PRIMARY KEY
    if type(primary_key) is str:
        id_field = f'{get_id_field(table_name)} =?'
        primary_key_values=primary_key
    elif type(primary_key) is dict:
        id_field=' AND '.join([f'{k} = ?' for k in primary_key])
        primary_key_values=[primary_key[k] for k in primary_key]

    # query = f"SELECT * FROM {table_name} WHERE {id_field} = ?"
    #GS MODIFICATION FOR COMPOSITE KEY
    query = f"SELECT * FROM {table_name} WHERE {id_field}"

#### GS MODIFICATION FOR COMPOSITE PRIMARY KEY
    values=[]
    if type(primary_key) is str:
        values.append(primary_key_values)
    elif type(primary_key) is dict:
        values+=primary_key_values

    print("Executing SELECT Query:", query)  # Log the query for debugging
    print("With Values:", primary_key_values)  # Log the row ID
    cur = conn.cursor()
    cur.execute(query,values)
    row = cur.fetchone()
    return dict(row) if row else None

### GS to deal with q.any_of - tuple values passed from wrapper
def flatten(l):
    f = [item for sublist in l for item in (sublist if (isinstance(sublist, list) or isinstance(sublist,tuple)) else [sublist])]
    return f

def construct_fields(conditions):
    fields=[]
    for k in conditions:
        if type(conditions[k]) in [list,tuple] :
            if len(conditions[k])>0:
                or_condition=' OR '.join([f'{k} = ?' for n in range(len(conditions[k]))])
                fields.append(f"({or_condition})")
            else: fields.append(f'{k} = "" ')
        else:
            fields.append(f'{k} = ?')
    return ' AND '.join(flatten(fields))

## ADDED BY GS Fecth with condictions
@anvil.server.callable
def get_rows_by_conditions(table_name, conditions):
    """Fetches a row by its unique identifier (primary key)."""
    conn = get_connection()
    # id_field = get_id_field(table_name)
    # fields=' AND '.join([f'{k} = ?' for k in conditions])
    fields = construct_fields(conditions)
    values=flatten([conditions[k] for k in conditions])

    query = f"SELECT * FROM {table_name} WHERE {fields}"
    print("Executing SELECT Query:", query)  # Log the query for debugging
    print("With Values:", values)  # Log the row ID
    cur = conn.cursor()
    cur.execute(query,values)
    rows = cur.fetchall()
    return [dict(row) for row in rows]

print("SQLite Uplink server is running...")
anvil.server.wait_forever()


