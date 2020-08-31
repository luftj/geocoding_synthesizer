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
    
    for _ in range(number_samples):
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

    if len(list_points) > 0:
        outstring = outstring[:-1] # remove trailing comma
    outstring += ' ] }'

    with open(filename, "w", encoding="utf-8") as file:
        file.write(outstring)

def degrade_toponym(word):
    if random.uniform(0,1) <= config.strip_first_probability:
        word = word[1:]
    if random.uniform(0,1) <= config.strip_last_probability:
        word = word[:-1]
    if random.uniform(0,1) <= config.umlaut_conversion_probability:
        word = word.replace("ä","a")
        word = word.replace("ö","o")
        word = word.replace("ü","u")
        word = word.replace("ß","f")
    newword = ""
    for c in word:
        if random.uniform(0,1) <= config.ocr_character_error_probability:
            newword += config.ocr_single_char_errors.get(c,c)
        else:
            newword += c
    word = newword

    return word

def degrade_samples(samples):
    degraded_samples = []
    for sample in samples:
        places = sample[1]
        newplaces = []
        for place in places:
            name = place[0]
            if random.uniform(0,1) <= config.miss_probability:
                continue
            if (" " in name) or ("-" in name):
                if random.uniform(0,1) <= config.word_split_probability:
                    tosplit = name.replace("-"," ")
                    # split word(s)
                    split_places = [ [degrade_toponym(w), *place[1:], name] for w in tosplit.split(" ")]
                    newplaces += split_places
                    continue

            newplace = (degrade_toponym(name),*place[1:],name)
            newplaces.append(newplace)
            
        newsample = (sample[0],newplaces)
        print(newsample)
        degraded_samples.append(newsample)

    return degraded_samples

if __name__ == "__main__":
    samples = sample_bboxes(config.db_table, config.max_extent, config.map_sizes_from_scale[25000], config.n_samples, config.type_filter)
    samples = degrade_samples(samples)

    for i, sample in enumerate(samples):
        path = "data"
        points = list(map(lambda s: s[1:3], sample[1]))
        props = list(map(lambda s: dict(zip(["text","feature_code","name"],[s[0]]+list(s[3:]))), sample[1]))
        points_to_geojson("%s/points_%d.json" %(path,i), points, props)
        bbox_to_geojson("%s/bbox_%d.json" %(path,i), sample[0])