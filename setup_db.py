import argparse

from database import query_database,create_table_from_csv,create_table
import config

def initialise_geonames_table(tablename, filepath="geonames_DE/DE.txt"):
    headers = {
        "geonameid"         : "int",
        "name"              : "varchar(200)",
        "asciiname"         : "varchar(200)",
        "alternatenames"    : "varchar(10000)",
        "latitude"          : "float",
        "longitude"         : "float",
        "feature_class"     : "char(1)",
        "feature_code"      : "varchar(10)",
        "country_code"      : "varchar(2)",
        "cc2"               : "varchar(200)",
        "admin1_code"       : "varchar(20)",
        "admin2_code"       : "varchar(80)",
        "admin3_code"       : "varchar(20)",
        "admin4_code"       : "varchar(20)",
        "population"        : "bigint",
        "elevation"         : "int",
        "dem"               : "int",
        "timezone"          : "varchar(40)",
        "modification_date" : "date"
    }
    
    db_query = "drop table %s if exists;" % (tablename)
    query_database(db_query)

    create_table(tablename,headers.keys(),headers.values())
    create_table_from_csv(tablename,filepath)
    query_database("create extension postgis;")

    # db_query = "ALTER TABLE %s ADD COLUMN coordinates geometry;" % (tablename)
    db_query = "select AddGeometryColumn('%s', 'coordinates', %d, 'POINT', 2);" % (tablename,config.srid)
    query_database(db_query)

    # db_query = "UPDATE %s this SET coordinates = ( select ST_POINT( other.longitude, other.latitude ) from %s other where this.geonameid = other.geonameid);" % (tablename,tablename)
    db_query = "UPDATE %s SET coordinates = ST_POINT( longitude, latitude );" % (tablename)

    query_database(db_query)

def test_db_setup(tablename, testentry="Stellingen"):
    db_query = "select name,longitude,latitude,st_astext(coordinates),feature_class from %s where name='%s';" % (tablename,testentry)
    result = query_database(db_query)
    print(result)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="input geonames data file")
    parser.add_argument("--table", help="desired table name", default=config.db_table)
    args = parser.parse_args()
    # config.db_table = args.table
    initialise_geonames_table(args.table,args.file)
    # test_db_setup(args.table,placename)
