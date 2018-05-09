#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import random
import mysql.connector
from mysql.connector import errorcode



def connect_db(**setting):

    """Connect to mysql database
        """
    return mysql.connector.connect(**setting)


def create_table(cursor,**table):

    """Create a table in mysql database

    with a dictionnary in parameters.
    The key refers to the table name,
    and the value to the SQL query.
    
    """
    for name,values in table.items():           
        try:
            cursor.execute(values)      #Execute a SQL query

        except mysql.connector.Error as err: #If the table has been created

            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print('cette table existe déjà')

        else:
            print('La table {} a été créée'.format(name))



def retrieve_products(*category):

    """Retrieve data in Openfood Facts API thanks to a category list
    in parameter. (Check https://world.openfoodfacts.org/categories.json)

    Return a list with :
    -barcode
    -product name
    -product url
    -nutrition grade
    -nutrition reclassification
    -category id
    """

    list2 = list()
    for elmt in category:
        print("La catégorie {} est en cours de traitement"
              .format(elmt[1][3:]))
        nbpages=1
        while nbpages > 0 :
            
            link='https://fr-en.openfoodfacts.org/category/{}/{}.json'.format(elmt[1],nbpages) 
            r=requests.get(link)                                                                #request send to openfoodfact api
            request=r.json()                                                                    #extract in json
            nbpages+=1
            prod=request['products']
            if len(prod) > 0:
                
                for elt in prod:
                    
                    if 'nutrition_grades'in elt.keys() and('product_name' or
                        'product_name_fr') in elt.keys():
                        
                        name = elt['product_name']
                        url = elt['url']
                        nutri = elt['nutrition_grades']                         
                        if nutri == 'a':                                                        #Reclass nutrition grade value
                            reclass = 1                                                         #to compare them later
                        elif nutri == 'b':
                            reclass = 2
                        elif nutri == 'c':
                            reclass = 3
                        elif nutri == 'd':
                            reclass = 4
                        else:
                            reclass = 5
                        
                        code = int(elt['code'])
                        category_id = elmt[0]
                        list1 = [code,name,url,nutri,reclass,category_id,0]
                        yield list1
                        
                    
            else:
                nbpages = 0
                print("La catégorie {} est terminée".format(elmt[1][3:]))
                
                

    
	
def get_colname(cursor,table):
    
    """Return a list of all the columns
        for a given table
        """
    
    cursor.execute("SELECT * FROM {}".format(table))        #SQL query to retrieve all the columns
    liste = cursor.column_names

    return liste

def insert_data(cursor,table,*datas):

    """Insert data in a given table
    """

    column = get_colname(cursor,table)
    cursor.fetchall()
    try:                                                    #Check if the data not in the table 
        for data in datas:
            j = tuple(data)                                 #The data must be tuples
            cursor.execute("INSERT INTO {} "
               "({})"
               "VALUES {}".format(table,','.join(column),j))

    except mysql.connector.errors.IntegrityError:
        pass

    else:
        pass
    
def choose_category(cursor,*category):

    """Returns the cutommer's choice"""

    cursor.execute("SELECT * FROM `category`")
    result=cursor.fetchall()

    for res in result:
        print("Tapez {} pour la catégorie {}".format(res[0],res[1][3:].decode("utf-8")))

    choice = input("Rentrez  le numéro de la catégorie que vous souhaitez")

    verify = 1
    while verify == 1:
        try:                                            #Choice must be an integer and between 0 and 20
            choice = int(choice)
            assert choice >= 0 and choice <= 20

        except ValueError:
            
            print("Il faut saisir un chiffre")

            choice = input("Rentrez  le numéro de la catégorie"
                           " que vous souhaitez")

        except AssertionError:

            print("Les numéros de catégorie doivent être compris"
                  " entre 0 et 20")

            choice = input("Rentrez  le numéro de la catégorie "
                           "que vous souhaitez")
            
        else:
            verify = 0

    return choice


def choose_product(cursor,choice):

    """Returns the cutommer's choice"""
    
    cursor.execute("SELECT code_barre,name FROM `products`"                                     #SQL query to get all 
                   "WHERE category_id = {} AND id_substitute= 0 LIMIT 25"                       #not substituted
                   .format(choice))

    results = cursor.fetchall()

    for res in results:
        print(res[0],'  ',res[1].decode("utf-8"))

    chosen_product = input("Rentrez  le code barre de votre choix:")

    verify = 1
    
    while verify == 1:
        try:                                                                                #Choice must be an integer
            chosen_product = int(chosen_product)

        except ValueError:
            
            print("Il faut saisir un chiffre")

            chosen_product=input("Rentrez  le code barre adéquat: ")

        else:
            verify = 0

    cursor.execute("SELECT * FROM `products`"
                   "WHERE code_barre = {}".format(chosen_product))

    product = cursor.fetchone()
    

    return product
    

def substitute_product(cursor,product):

    """Substitute a given product
        by comparing nutrition grade"""

    code = product[0]
    reclass = product[4]
    
    cursor.execute("SELECT code_barre,name FROM `products`"                             #SQL query to compare nutrition grade
                   "WHERE code_barre <> {} AND nutri_reclass<={}"
                   " ORDER BY code_barre LIMIT 1".format(code,reclass))
    

    result = cursor.fetchone()
    print("Nous vous proposons le résultat suivant: {}"
          .format(result[1].decode("utf-8")))

    record = int(input("Souhaitez-vous enregistrer ce produit? \n"
          "Tapez 1 pour oui, 0 pour non"))
    
    if record == 1:                     
        cursor.execute("UPDATE `products`"                                          #SQL query to update the table 
                   "SET id_substitute = {} WHERE code_barre = {}"
                   .format(result[0],code))
        print("Votre demande a bien été prise en compte")
    else:
        pass



def get_substituted_product(cursor,*category):

    """Returns all the substituted products"""
    
    choice = choose_category(cursor,*category)

    cursor.execute("SELECT code_barre,name FROM `products`"
                   "WHERE category_id = {} AND id_substitute<> 0"
                   .format(choice))

    results = cursor.fetchall()
    
    if len(results) > 0:
        print("Voici la liste des produits déjà substitués")
        for res in results:
            
            print(res[0],res[1].decode("utf-8"))

        chosen_product = input("Rentrez  le code barre de votre choix:")

        verify = 1
        
        while verify == 1:
            try:                                                                                #Choice must be an integer
                chosen_product = int(chosen_product)

            except ValueError:
                
                print("Il faut saisir un chiffre")

                chosen_product=input("Rentrez  le code barre adéquat:")

            else:
                verify = 0




        cursor.execute("SELECT a.name, b.name,b.url FROM products as a INNER JOIN products b ON a.id_substitute=b.code_barre WHERE a.code_barre={}"
                       .format(chosen_product))
        temp = cursor.fetchall()
        url = temp[0][2]
        subtitute = temp[0][1]
        prod = temp[0][0]
        print("Pour {} ==> {}.\n"
              " URL : {}"
              .format(prod.decode("utf-8"),
                      subtitute.decode("utf-8"),url.decode("utf-8")))

    else:
        print("Vous n'avez pas de produits substitués")
