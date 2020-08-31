import json
import numpy as np
import progressbar
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
import matplotlib.pyplot as plt

import config
from geocode import create_map_vector,coord_to_index

def get_bbox_centre(json_data):
    x = 0
    y = 0
    pointlist = json_data["features"][0]["geometry"]["coordinates"][0]
    for idx,point in enumerate(pointlist):
        if idx >= 4:
            break
        x += point[0]
        y += point[1]
    
    x /= 4
    y /= 4
    return (x,y)

if __name__ == "__main__":
    cell_size_degrees_train = 1
    cell_size_degrees_test = 2
    X = []
    Y = []
    num_empty = 0
    
    print("Training on %d samples..." % config.n_samples)
    progress = progressbar.ProgressBar()
    for i in progress(range(config.n_samples)):
        with open("data/points_%d.json"%i) as file:
            json_data = json.load(file)

            mapvector = create_map_vector(json_data, cell_size_degrees_train)
            if np.sum(mapvector) == 0:
                num_empty += 1
                continue
            X.append(mapvector)

        with open("data/bbox_%d.json"%i) as file:
            json_data = json.load(file)

            centre = get_bbox_centre(json_data)
            Y.append(coord_to_index(centre, cell_size_degrees_test))

    print(Y)
    print("empty samples", num_empty)

    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.1)
    clf = RandomForestClassifier(n_estimators=100)
    clf = clf.fit(X_train, Y_train)

    prediction_test = clf.predict(X_test)
    print("predictions", prediction_test)
    print("ground truth", Y_test)

    print("Accuracy", metrics.accuracy_score(Y_test, prediction_test))

    mapvect = [0] * ((180//cell_size_degrees_test) * (360//cell_size_degrees_test))
    for y in prediction_test:
        mapvect[y] += 1
    mapvect = np.reshape(mapvect, (180//cell_size_degrees_test, 360//cell_size_degrees_test))
    mapvect2 = [0] * ((180//cell_size_degrees_test) * (360//cell_size_degrees_test))
    for y in Y_test:
        mapvect2[y] += 1
    mapvect2 = np.reshape(mapvect2, (180//cell_size_degrees_test, 360//cell_size_degrees_test))
    
    fig, (ax1, ax2) = plt.subplots(1,2)
    ax1.set_title("prediction")
    ax1.imshow(mapvect)
    ax2.set_title("ground truth")
    ax2.imshow(mapvect2)
    plt.show()