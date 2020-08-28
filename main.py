import random
from database import query_database
import config

def query_bbox(tablename,bbox,type_filter):
    # query all points in bbox
    db_query = "select name,longitude,latitude,feature_code from %s where coordinates && ST_makeEnvelope(%f,%f,%f,%f,%d) and feature_class in ('%s');" % (config.db_table,*bbox,config.srid,"','".join(type_filter))
    # db_query = "select name,st_astext(coordinates),feature_code from %s where (longitude between %f and %f) and (latitude between %f and %f) and feature_class in ('%s');" % (config.db_table,*bbox,"','".join(type_filter))
    result = query_database(db_query)
    # print(*result,sep="\n")
    print(len(result), "number of hits")
    return result

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
        bbox_result = query_bbox(config.db_table, bbox, type_filter)
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

max_extent = [9.7008,53.363,10.3435,53.7383] # xmin, ymin, xmax, ymax
type_filter = ["P"]

samples = sample_bboxes(config.db_table,max_extent,config.map_sizes_from_scale[25000],4,type_filter)

points = list(map(lambda s: s[1:3],samples[0][1]))
props = list(map(lambda s: dict(zip(["name","feature_code"],[s[0]]+list(s[3:]))),samples[0][1]))
print(props)
points_to_geojson("test.json",points,props)
bbox_to_geojson("bbox.json",samples[0][0])