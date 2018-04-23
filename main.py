from settings import *
from functions import *

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
