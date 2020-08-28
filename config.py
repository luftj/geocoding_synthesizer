db_creds = {
    "host": "192.168.13.7",
    "port" : 5432,
    "dbname" : "geocode",
    "user": "postgres",
    "password": "enteente",
}
db_table = "gn_de"

# geonames srid is wgs84 -> EPSG:4326
srid  = 4326

# reference map size for German official TK series in degrees [lon,lat]
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

max_extent = [9.7008,53.363,10.3435,53.7383] # xmin, ymin, xmax, ymax
type_filter = ["P"] # possible values subset of ["A","H","L","P","R","S","T","U","V"]


miss_probability = 0.3
word_split_probability = 1

strip_first_probability = 0.2
strip_last_probability = 0.2
umlaut_conversion_probability = 0.6
ocr_character_error_probability = 0.1
ocr_single_char_errors = {
    "f" : "t",
    "m" : "rn",
    "t" : "f",
    "R" : "B"
}