import random
from database import query_database,create_table_from_csv,create_table

srid  = 4326

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
    
    db_query = "drop table %s if exists;" % (db_table)
    query_database(db_query)

    create_table(db_table,headers.keys(),headers.values())
    create_table_from_csv(db_table,filepath)
    query_database("create extension postgis;")

    # db_query = "ALTER TABLE %s ADD COLUMN coordinates geometry;" % (db_table)
    db_query = "select AddGeometryColumn('%s', 'coordinates', %d, 'POINT', 2);" % (db_table,srid)
    query_database(db_query)

    # db_query = "UPDATE %s this SET coordinates = ( select ST_POINT( other.longitude, other.latitude ) from %s other where this.geonameid = other.geonameid);" % (db_table,db_table)
    db_query = "UPDATE %s SET coordinates = ST_POINT( longitude, latitude );" % (db_table)

    query_database(db_query)

def query_bbox(tablename,bbox,type_filter):
    # query all points in bbox
    db_query = "select name,longitude,latitude,feature_code from %s where coordinates && ST_makeEnvelope(%f,%f,%f,%f,%d) and feature_class in ('%s');" % (db_table,*bbox,srid,"','".join(type_filter))
    # db_query = "select name,st_astext(coordinates),feature_code from %s where (longitude between %f and %f) and (latitude between %f and %f) and feature_class in ('%s');" % (db_table,*bbox,"','".join(type_filter))
    result = query_database(db_query)
    # print(*result,sep="\n")
    print(len(result), "number of hits")
    return result

def test_db_setup(tablename):
    db_query = "select name,longitude,latitude,feature_class from %s where name='Stellingen';" % (db_table)
    result = query_database(db_query)
    print(result)

def make_random_bbox(max_extent,map_size):
    x_space = max_extent[2] - max_extent[0] - map_size[0]
    y_space = max_extent[3] - max_extent[1] - map_size[1]
    x_min = random.uniform(max_extent[0], max_extent[0] + x_space)
    y_min = random.uniform(max_extent[1], max_extent[1] + y_space)
    bbox = [x_min, y_min, x_min + map_size[0], y_min + map_size[1]]
    print(bbox)
    return bbox

def sample_bboxes(tablename, max_extent, map_size, number_samples, type_filter=["A","H","L","P","R","S","T","U","V"]):
    # get contents for a range of bboxes
    result_set = []
    
    for n in range(number_samples):
        bbox = make_random_bbox(max_extent, map_size)
        bbox_result = query_bbox(db_table, bbox, type_filter)
        result_set.append((bbox, bbox_result))
    return result_set

def bbox_to_geojson(filename, bbox):
    outstring = '{ "type": "FeatureCollection","features": ['
        
    outstring += '{ "type": "Feature","geometry": {"type": "Polygon", "coordinates": [['
    points = [(bbox[0],bbox[1]),(bbox[2],bbox[1]),(bbox[2],bbox[3]),(bbox[0],bbox[3]),(bbox[0],bbox[1])]
    for point in points:
        outstring +=  " [ %f,%f ]," % point # lon, lat
    outstring = outstring[:-1] # remove trailing comma
    outstring += ' ]]}, "properties": { '
    outstring += ''
    outstring += ' } },'

    outstring = outstring[:-1] # remove trailing comma
    outstring += ' ] }'
    
    with open(filename, "w", encoding="utf-8") as file:
        file.write(outstring)

def points_to_geojson(filename, list_points, list_properties):
    outstring = '{ "type": "FeatureCollection","features": ['
        
    for idx,point in enumerate(list_points):
        outstring += '{ "type": "Feature","geometry": {"type": "Point", "coordinates": ['
        outstring +=  "%f,%f" % tuple(map(float,point)) # lon, lat
        outstring += ' ]}, "properties": { '
        props = map(lambda o: '"%s":"%s"'%(o[0],o[1]), list_properties[idx].items())
        outstring += ', '.join(props)
        outstring += ' } },'

    outstring = outstring[:-1] # remove trailing comma
    outstring += ' ] }'

    with open(filename, "w", encoding="utf-8") as file:
        file.write(outstring)

db_table = "gn_de"


max_extent = [9.7008,53.363,10.3435,53.7383] # xmin, ymin, xmax, ymax
type_filter = ["P"]

# 1:5.000 -  Die einzelnen Kartenblätter der Deutschen Grundkarte haben eine Ausdehnung von 40 cm × 40 cm gleich 2 km × 2 km. 
# 1:25.000 – 10 Längenminuten und 6 Breitenminuten gleich 12,6 km bis 10,6 km × 11,1 km
# 1:50.000 – 20 Längenminuten und 12 Breitenminuten gleich 25,2 km bis 21,2 km × 22,2 km
# 1:100.000 – 40 Längenminuten und 24 Breitenminuten gleich 50,4 km bis 42,4 km × 44,4 km
# 1:200.000 – 80 Längenminuten (1° 20‘) und 48 Breitenminuten gleich 108,8 km bis 84,8 km × 88,8 km
map_sizes_from_scale = {
      5000 : [0.03333,0.02],
     25000 : [0.16667,0.1],
     50000 : [0.33333,0.05],
    100000 : [0.66667,0.025],
    200000 : [1.33333,0.0125]
}

samples = sample_bboxes(db_table,max_extent,map_sizes_from_scale[25000],4,type_filter)
points = list(map(lambda s: s[1:3],samples[0][1]))
props = list(map(lambda s: dict(zip(["name","feature_code"],[s[0]]+list(s[3:]))),samples[0][1]))
print(props)
points_to_geojson("test.json",points,props)
bbox_to_geojson("bbox.json",samples[0][0])