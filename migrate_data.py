import psycopg2
from psycopg2 import sql

# Local database connection
local_conn = psycopg2.connect(
    dbname="Tsl_Nigeria_tv",
    user="postgres",
    password="1234",
    host="localhost"
)
local_cursor = local_conn.cursor()

# Railway database connection
railway_conn = psycopg2.connect(
    dbname="railway",
    user="postgres",
    password="WvLaWhIthyOSNaoBaRvxklhbGNKVMyRi",
    host="autorack.proxy.rlwy.net",
    port=24209
)
railway_cursor = railway_conn.cursor()

def copy_table_data(table_name):
    # Skip the django_migrations table to avoid conflicts with migration records
    if table_name == "django_migrations":
        print(f"Skipping table: {table_name}")
        return

    # Fetch all data from the local table
    local_cursor.execute(sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name)))
    rows = local_cursor.fetchall()

    # Fetch column names for the table
    local_cursor.execute(
        sql.SQL("SELECT column_name FROM information_schema.columns WHERE table_name = %s"),
        (table_name,)
    )
    columns = [row[0] for row in local_cursor.fetchall()]

    # Prepare the INSERT query for the Railway database with ON CONFLICT DO NOTHING to avoid duplicate key errors
    insert_query = sql.SQL(
        "INSERT INTO {} ({}) VALUES ({}) ON CONFLICT (id) DO NOTHING"
    ).format(
        sql.Identifier(table_name),
        sql.SQL(", ").join(map(sql.Identifier, columns)),
        sql.SQL(", ").join(sql.Placeholder() for _ in columns)
    )

    # Insert data into the Railway table
    for row in rows:
        try:
            railway_cursor.execute(insert_query, row)
        except Exception as e:
            print(f"Error inserting row into {table_name}: {e}")

    print(f"Copied data for table: {table_name}")

# Fetch all table names from the local database
local_cursor.execute(
    "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
)
tables = [row[0] for row in local_cursor.fetchall()]

# Copy data for each table
for table in tables:
    copy_table_data(table)

# Commit changes to the Railway database
railway_conn.commit()

# Close all connections
local_cursor.close()
local_conn.close()
railway_cursor.close()
railway_conn.close()

print("All tables and data migrated successfully!")
