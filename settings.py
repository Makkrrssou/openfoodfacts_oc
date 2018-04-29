

category=[(0, 'en:poultries'), (1, 'en:biscuits-and-cakes'), (2,
'en:meals' ), (3, 'en:fruits'), (4,
'en:syrups'),(6, 'en:fresh-foods'), (7, 'en:bars'),
(8, 'en:confectioneries'), (9, 'en:chips-and-fries'), (10,
'en:canned-legumes'), (11, 'en:meats'), (12, 'en:coffees'), (13,
'en:legumes'), (14, 'en:non-sugared-beverages'), (15, 'en:fresh-meals'),
(16, 'en:juices-and-nectars'), (17, 'en:dried-products'), (18,
'en:vegetable-oils'), (19, 'en:dairy-desserts'), (20,'en:plant-based-foods-and-beverages')]

##category=[(5, 'en:spices')]

config={
    'user':'root',
    'host': '127.0.0.1',
    'database' : 'openfoodfact'
    }

tb=dict()

tb['category'] = (
    " CREATE TABLE `category`("
    " `category_id` int NOT NULL PRIMARY KEY ,"
    " `name` text NOT NULL"
    " )"
    )
    
tb['products'] = (
    " CREATE TABLE `products`("
    " `code_barre` bigint NOT NULL PRIMARY KEY ,"
    " `name` text NOT NULL,"
    " `url`  text NOT NULL,"
    " `nutri_score` text NOT NULL,"
    " `nutri_reclass`int NOT NULL,"
    " `category_id` int NOT NULL,"
    " `id_substitute`bigint NOT NULL "
    " )"
    )
