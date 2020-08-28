import psycopg2
import sys

import config

conn = None
# connect to DB with values read from DBconfig.json
def connectDB():
    try:
        global conn
        print(*config.db_creds.values())
        conn = psycopg2.connect("host={} port={} dbname={} user={} password={}".format(*config.db_creds.values()))
        
    except:
        print(sys.exc_info()[0])
        print("FATAL ERROR: could not connect to database!")
        exit()

def fetchCursor():
    if not conn:
        connectDB()
    try:
        cur = conn.cursor()
        return cur
    except psycopg2.InterfaceError:
        print("Reconnecting Database...")
        connectDB()
        return fetchCursor()

def query_database(db_query, all = True):
    cur = fetchCursor()
    try:
        # EXECUTE QUERY #
        cur.execute(db_query)
        pass
    except Exception as e:
        conn.rollback()
        print(e)
        pass
    # PARSE RESPONSE #
    results = []
    try:
        for row in cur.fetchall():
            if row[0] is not None:
                if not all:
                    results.append(row[0])
                else:
                    results.append(row) 
    except psycopg2.ProgrammingError as e:
        print(e)
    return results

def create_table(tablename, headernames, headertypes):
    headers = []
    for hname,htype in zip(headernames,headertypes):
        headers.append("%s %s" % (hname,htype))
    q = "create table %s ( %s )" % (tablename,",".join(headers))
    query_database(q)
    conn.commit()

def create_table_from_csv(tablename, csv_path):
    with open(csv_path, encoding = 'utf-8') as csv_fp:
        cur = fetchCursor()
        cur.copy_from(csv_fp,tablename,sep="\t",null="")
        conn.commit()