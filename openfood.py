import requests
import random
import mysql.connector
from mysql.connector import errorcode

def connect_db(**setting):
    return mysql.connector.connect(**setting)


def create_table(cursor,**table):
    for name,values in table.items():
        try:
            cursor.execute(values)

        except mysql.connector.Error as err:

            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print('cette table existe déjà')

        else:
            print('La table {} a été créée'.format(name))



def retrieve_products(*category):
    list2=list()
    for elmt in category:
        print("La catégorie {} est en cours de traitement".format(elmt[1][3:]))
        nbpages=1
        while nbpages>0 :
            
            link='https://fr-en.openfoodfacts.org/category/{}/{}.json'.format(elmt[1],nbpages)
            r=requests.get(link)
            request=r.json()
            nbpages+=1
            prod=request['products']
            if len(prod)>0:
                for elt in prod:
                    if 'nutrition_grades'in elt.keys() and ('product_name' or 'product_name_fr') in elt.keys():
                        name=elt['product_name']
                        url=elt['url']
                        nutri=elt['nutrition_grades']
                        if nutri=='a':
                            reclass=1
                        elif nutri=='b':
                            reclass=2
                        elif nutri=='c':
                            reclass=3
                        elif nutri=='d':
                            reclass=4
                        else:
                            reclass=5
                        
                        code=int(elt['code'])
                        category_id=elmt[0]
                        list1=[code,name,url,nutri,reclass,category_id,0]
                        yield list1
                        
                    
            else:
                nbpages=0
                print("La catégorie {} est terminée".format(elmt[1][3:]))
                
                

    
	
def get_colname(cursor,table):
    
    cursor.execute("SELECT * FROM {}".format(table))
    liste=cursor.column_names

    return liste

def insert_data(cursor,table,*datas):

    column=get_colname(cursor,table)
    cursor.fetchall()
    for data in datas:
        j=tuple(data)
        cursor.execute("INSERT INTO {} "
           "({})"
           "VALUES {}".format(table,','.join(column),j))
    
def choose_category(*category):
    
    for cat in category:
        print("Tapez {} pour la catégorie {}".format(cat[0],cat[1][3:]))

    choice=int(input("Rentrez  le numéro de la catégorie que vous souhaitez"))
    

    return choice

def choose_product(cursor,choice):
    cursor.execute("SELECT code_barre,name FROM `products`"
                   "WHERE category_id = {} AND id_substitute= 0 LIMIT 25".format(choice))
    results= cursor.fetchall()

    for res in results:
        print(res[0],'  ',res[1])

    chosen_product=int(input("Rentrez  le code barre de votre choix"))

    cursor.execute("SELECT * FROM `products`"
                   "WHERE code_barre = {}".format(chosen_product))

    product=cursor.fetchone()
    

    return product
    

def substitute_product(cursor,product):

    code=product[0]
    reclass=product[4]
    
    cursor.execute("SELECT code_barre FROM `products`"
                   "WHERE code_barre <> {} AND nutri_reclass<={}"
                   " ORDER BY code_barre LIMIT 1".format(code,reclass))
    
    result=cursor.fetchone()
    print(result)
    cursor.execute("UPDATE `products`"
	       "SET id_substitute = {} WHERE code_barre = {}"
	       .format(result[0],code))

def get_substituted_product(cursor,*category):
    choice=choose_category(*category)

    cursor.execute("SELECT code_barre,name FROM `products`WHERE category_id = {} AND id_substitute<> 0".format(choice))
    results=cursor.fetchall()
    if len(results)>0:
        print("Voici la liste des produits déjà substitués")
        for res in results:
            
            print(res)

        chosen_product=int(input("Rentrez  le code barre de votre choix"))

        cursor.execute("SELECT a.name, b.name,b.url FROM products as a "
                   "INNER JOIN products b ON a.id_substitute=b.code_barre WHERE a.code_barre={}"
                       .format(chosen_product))
        temp=cursor.fetchall()
        url=temp[0][2]
        subtitute=temp[0][1]
        prod=temp[0][0]
        print("Pour {} ==> {}. URL : {}".format(prod,subtitute,url))

    else:
        print("Vous n'avez pas de produits substitués")

        
##category=[(0, 'en:poultries'), (1, 'en:biscuits-and-cakes'), (2,
##'en:plant-based-foods-and-beverages'), (3, 'en:fruits'), (4,
##'en:syrups'), (5, 'en:spices'), (6, 'en:fresh-foods'), (7, 'en:bars'),
##(8, 'en:confectioneries'), (9, 'en:chips-and-fries'), (10,
##'en:canned-legumes'), (11, 'en:meats'), (12, 'en:coffees'), (13,
##'en:legumes'), (14, 'en:non-sugared-beverages'), (15, 'en:fresh-meals'),
##(16, 'en:juices-and-nectars'), (17, 'en:dried-products'), (18,
##'en:vegetable-oils'), (19, 'en:dairy-desserts'), (20, 'en:meals')]

category=[(5, 'en:spices')]

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



cnx = connect_db(**config)
cursor=cnx.cursor()

if cnx.is_connected:
    print('base connectée')
else:
    print('base pas connectée')

create_table(cursor,**tb)

products=list()
products_list=retrieve_products(*category)
products.extend(products_list)
   
for keys,items in tb.items():
    if keys=='category':
        try:
            insert_data(cursor,keys,*category)
            print("les données de la table {} ont été insérées".format(keys))
            cnx.commit()
        except mysql.connector.errors.IntegrityError:
            
            print("les données ont déjà été insérées")

        else:
            
            print("les données de la table {} ont été insérées".format(keys))
            cnx.commit()
    else:
        
        try:
            insert_data(cursor,keys,*products)
            
        except mysql.connector.errors.IntegrityError:
            
            print("les données ont déjà été insérées")
        else:
            print("les données de la table {} ont été insérées".format(keys))
            cnx.commit()
        

run=1
while run>0:

    action= str(input("Pour trouver de nouveaux produits à substituer tapez n. \n"
            "Pour retrouver tous vos enregistrements tapez e. \n"
                      "Sinon tapez sur n'importe quel touche."))

    if action == 'n':
        
        choice=choose_category(*category)
        product=choose_product(cursor,choice)
        substitute_product(cursor,product)
        run=int(input("Si vous voulez continuer tapez 1, sinon tapez 0"))
            
                        

    elif action == 'e':
        
        get_substituted_product(cursor,*category)
        run=int(input("Si vous voulez continuer tapez 1, sinon tapez 0"))

    else:
        run=0


print("merci d'être venu")
    
                
                

    

	






