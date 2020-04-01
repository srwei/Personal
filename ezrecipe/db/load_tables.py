import psycopg2
import csv

try:
    connection = psycopg2.connect(user = "stevenwei",
                                  password = "Chicago16",
                                  host = "127.0.0.1",
                                  port = "5432",
                                  database = "ezrecipe")

    cursor = connection.cursor()

    try:
        with open('/Users/stevenwei/Programming/Projects/Personal/ezrecipe/recipes.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                cursor.execute("INSERT INTO recipes VALUES (%s, %s, %s)", row)
            print("Successfully inserted into recipe table")
    except:
        print("Failed insert into recipe table")

    try:
        with open('/Users/stevenwei/Programming/Projects/Personal/ezrecipe/all_ingredients.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                cursor.execute("INSERT INTO ingredients VALUES (%s, %s)", row)
            print("Successfully inserted into the ingredients table")
    except:
        print("Failed inserting into the ingredients table")

    try:
        with open('/Users/stevenwei/Programming/Projects/Personal/ezrecipe/all_recipe_ingredients.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                cursor.execute("INSERT INTO recipe_ingredients VALUES (DEFAULT, %s, %s, %s, %s)", row)
            print("Successfully inserted into the recipe ingredients table")
    except:
        print("Failed inserting into the recipe ingredients table")

    connection.commit()

    # Print PostgreSQL version

except (Exception, psycopg2.DatabaseError) as error :
    print ("Error while creating database to PostgreSQL", error)
finally:
    #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")