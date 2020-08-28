# Geocoding Test-/Trainingdata Synthesizer

create bounding boxes with place names for use in training or evaluationg geocoding/geoparsing models.

---

## Installation

Requires
* a running postGIS database
* Python3

```$ python3 -m pip install -r requirements.txt ```

Download geonames data from the [official repository](http://download.geonames.org/export/dump/).

set your database connection settings in `config.py`

Run ```$ python3 setup_db.py [--table TABLE] geonamesfile``` with the path to the downloaded file and the name the new table should have in your database.

## Usage

Set the desired maximal extent of where you want to generate data, the desired feature type filter according to the [geonames specs](http://www.geonames.org/export/codes.html) and the error probabilites for data degradation in `config.py`. Then run `$ python3 main.py`

## To Do
* smarter OCR errors, esp. with multi-character errors and different substitution/deletion/insertion probabilities
* feature class filter