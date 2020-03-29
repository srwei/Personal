import psycopg2
import csv 

try:
    connection = psycopg2.connect(user = "stevenwei",
                                  password = "Chicago16",
                                  host = "127.0.0.1",
                                  port = "5432",
                                  database = "ezrecipe")

    cursor = connection.cursor()

    with open('/Users/stevenwei/Programming/Projects/Personal/ezrecipe/test_recipe.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            cursor.execute("INSERT INTO recipes VALUES (%s, %s)", row)
        
    connection.commit()

except (Exception, psycopg2.DatabaseError) as error :
    print ("Error while creating database to PostgreSQL", error)
finally:
    #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")