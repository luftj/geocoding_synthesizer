import os
import requests
import json
import numpy as np
import matplotlib.pyplot as plt

import config

def geocode_geonames(query):
    countrycode = ""
    if  config.countrycode != "none":
        countrycode += "&country=" + config.countrycode
    url = "http://api.geonames.org/searchJSON?username=jlcsl&inclBbox=true&name=" + query + countrycode

    cache_index = query.lower()[0]
    cache_filepath = (os.path.dirname(__file__)+"/cache/geonames_%s.json" % (cache_index))
    
    if os.path.isfile(cache_filepath):
        with open(cache_filepath) as cache_file:
            cache_data = json.load(cache_file)
    else:
        cache_data = {}

    if url in cache_data:
        return cache_data[url]

    try:
        r = requests.get(url,headers={'Content-Type': 'application/json'})
        if not r.status_code == 200:
            print("could not get from geonames API")
            print("Error code", r.status_code)
            exit()
    except Exception as e:
        print(e)
        return []

    output = []

    accepted_classes = ["P"]
    # P: city,village,... 
    # A: country, state, region (administrative) 
    # S: spot/building/farm/station
    # L: parks,area,...,
    # H: stream,lake

    if not "geonames" in r.json():
        # error in geocoding. e.g. hourly limit exceeded
        print(r.json())
        exit()
    
    for result in r.json()["geonames"]:
        if "fcl" in result and result["fcl"]in accepted_classes:
            if "bbox" in result:
                bbox_size = abs(float(result["bbox"]["east"]) - float(result["bbox"]["west"])) * abs(float(result["bbox"]["north"]) - float(result["bbox"]["south"]))
            else: bbox_size = 0
            # entry = "; ".join([result["lat"], result["lng"], str(bbox_size), result["name"], result["adminName1"]])
            # output.append(entry)
            output.append([result["lat"], result["lng"], str(bbox_size), result["name"], result["adminName1"]])

    with open(cache_filepath, "w") as cache_file:
        cache_data[url] = output
        json.dump(cache_data,cache_file)

    return output

def coord_to_index(coordinates, polygon_size):
    """
    Convert coordinates into an array index. Use that to modify mapvec polygon value.
    :param coordinates: (latitude, longitude) to compute
    :param polygon_size: integer size of the polygon? i.e. the resolution of the world
    :return: index pointing into mapvec array
    """
    latitude = float(coordinates[0]) - 90 if float(coordinates[0]) != -90 else -179.99  # The two edge cases must
    longitude = float(coordinates[1]) + 180 if float(coordinates[1]) != 180 else 359.99  # get handled differently!
    if longitude < 0:
        longitude = -longitude
    if latitude < 0:
        latitude = -latitude
    x = int(360 / polygon_size) * int(latitude / polygon_size)
    y = int(longitude / polygon_size)
    return x + y if 0 <= x + y <= int(360 / polygon_size) * int(180 / polygon_size) else ValueError(u"polygon_size should be int")

def create_map_vector(json_data, cell_size_degrees):
    mapvector = [0] * ((180//cell_size_degrees) * (360//cell_size_degrees)) # 360° lon X 180° lat
    for feature in json_data["features"]:
        hypos = geocode_geonames(feature["properties"]["text"])
        # print(feature["properties"]["text"],hypos))
        for hypo in hypos:
            coords = list(map(float,hypo[0:2]))
            index = coord_to_index(coords,cell_size_degrees)
            mapvector[index] += 1
            # print(coords,index,hypo[3])
    return mapvector

if __name__ == "__main__":
    with open("data/points_0.json") as file:
        json_data = json.load(file)

        cell_size_degrees = 1
        mapvector = create_map_vector(json_data, cell_size_degrees)
        

    print("mapvector max",max(mapvector))
    print("max index",  mapvector.index(max(mapvector)))

    mapvect = np.array(mapvector)
    mapvect = np.reshape(mapvector,(180//cell_size_degrees,360//cell_size_degrees))
    max_idx = np.argmax(mapvect)
    y,x = np.unravel_index(max_idx,mapvect.shape)
    print(y,x)
    print(mapvect[y,x])

    norm_mapvect = mapvect / np.max(mapvect)

    # get true map position from bbox
    # with open("data/bbox_0.json") as file:
    y = 9.866884 + (10.033554 - 9.866884) / 2
    x = 53.409067 + (53.509067 - 53.409067) / 2
    print("bbox centre pos",[x,y],coord_to_index([x,y],1))


    plt.imshow(mapvect)
    plt.show()