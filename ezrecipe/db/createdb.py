import psycopg2
try:
    connection = psycopg2.connect(user = "stevenwei",
                                  password = "Chicago16",
                                  host = "127.0.0.1",
                                  port = "5432",
                                  database = "ezrecipe")

    cursor = connection.cursor()
    # Print PostgreSQL Connection properties
    create_recipe_table_query = "CREATE TABLE recipes ( \
                                recipe_id INTEGER PRIMARY KEY, \
                                recipe_name TEXT \
                                )"

    create_ingredients_table_query = "CREATE TABLE ingredients ( \
                                    ingredient_id INTEGER PRIMARY KEY, \
                                    ingredient_name TEXT \
                                    )"

    create_recipe_ingredients_table_query = "CREATE TABLE recipe_ingredients ( \
                                            recipe_ingredient_id INTEGER PRIMARY KEY, \
                                            recipe_id INTEGER, \
                                            ingredient_id INTEGER, \
                                            recipe_name TEXT \
                                            ingredient_name TEXT \
                                            )" 

    # Print PostgreSQL version
    cursor.execute(create_recipe_table_query)
    cursor.execute(create_ingredients_table_query)
    cursor.execute(create_recipe_ingredients_table_query)
    connection.commit()

except (Exception, psycopg2.DatabaseError) as error :
    print ("Error while creating database to PostgreSQL", error)
finally:
    #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")