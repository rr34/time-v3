import sys, os
import mariadb
import pandas as pd
import json

def sql_execute(text, user_input, result_type):
    try:
        conn = mariadb.connect(
            user=os.getenv('MYSQL_USER'),
            host=os.getenv('MYSQL_HOST'),
            password=os.getenv('MYSQL_PASSWORD'),
            port=int(os.getenv('MYSQL_PORT')),
            database=os.getenv('MYSQL_DATABASE')
        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB platform: {e}")
        sys.exit(1)
    cur = conn.cursor()

    if user_input and result_type:
        cur.execute(text, user_input)
    elif not user_input:
        cur.execute(text)

    if result_type == 'dataframe':
        result_fetched = cur.fetchall()
        columns = [c[0] for c in cur.description]
        cur.close()
        conn.close()
        result_df = pd.DataFrame(result_fetched, columns=columns)
        return result_df
    elif result_type == 'listtuples':
        result_fetched = cur.fetchall()
        cur.close()
        conn.close()
        return result_fetched
    elif result_type == 'listsinglefield':
        result_fetched = cur.fetchall()
        cur.close()
        conn.close()
        results = [x[0] for x in result_fetched]
        return results
    elif result_type == 'listdictionaries':
        result_fetched = cur.fetchall()
        columns = [c[0] for c in cur.description]
        results = []
        for result in result_fetched:
            results.append(dict(zip(columns,result)))
        cur.close()
        conn.close()
        return results
    elif result_type == 'updatedb':
        conn.commit()
        cur.close()
        conn.close()
        return