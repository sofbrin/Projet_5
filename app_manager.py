#! /usr/bin/env python
# coding: utf8

import os
import sys

import django
import requests as requests
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator

from constants import App_Title, App_Intro, App_Home_Menu, App_Categories_Menu, App_Products_Menu, \
    App_Selected_Product_Menu, App_Nutri_Score, App_Suggested_Product_Menu, App_Save_Substitute_Menu, \
    App_DB_Menu, App_DB_Cat_Menu, end_of_App

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "purbeurre.settings")
django.setup()

from substitutes_db.models import ProductDb, CategoryDb, HistoricDb


def find_or_substitute():
    """ First Application menu :
    --> looking for a product in the OpenFoodFacts database
    --> looking for a substitute product already saved in the user's personal database """

    while True:
        input_user = input(App_Home_Menu)

        if input_user == '1':
            display_categories()
        elif input_user == '2':
            substitutes()
        elif input_user == '3':
            print(end_of_App)
            sys.exit()


###############################################################
""" SCRIPT FIRST PART : QUERYING THE OPENFOODFACTS DATABASE """
###############################################################


def display_categories():
    """ Using the OpenFoodFacts Api to access the categories, displaying them and selecting one of them """

    r_categories = requests.get('https://fr.openfoodfacts.org/categories.json')
    response = r_categories.json()
    categories = response['tags']

    page = 1

    while True:
        for idx, category in enumerate(categories[page*10-10:page*10]):
            print(idx+1, category['name'])

        input_user = input(App_Categories_Menu)

        if input_user == 's':
            page += 1
        elif input_user == 'p' and page-1 != 0:
            page -= 1
        elif input_user == '0':
            return
        else:
            try:
                selection = int(input_user)
                if 10 >= selection >= 1:
                    display_products(categories[page*10-10+(selection-1)])
            except ValueError:
                continue


def display_products(category):
    """ Using the OpenFoodFacts Api to access the substitutes_db, displaying them and selecting one of them """

    page = 1

    while True:
        r_products = requests.get(category['url'] + '/{}.json'.format(page))
        response = r_products.json()
        products = response['products']

        for idx, product in enumerate(products):
            if 'product_name' in product and product['product_name'] != '':
                print(idx+1, product['product_name'])
            #else:
                #print(idx+1, 'ce produit ne contient pas assez d\'informations pour être affiché')

        input_user = input(App_Products_Menu)

        if input_user == 's':
            page += 1
        elif input_user == 'p' and page-1 != 0:
            page -= 1
        elif input_user == '0':
            return
        else:
            try:
                selection = int(input_user)
                if 20 >= selection >= 1:# and 'product_name' in products and products[selection-1]['product_name'] != '':
                    choose_product(products[selection-1], category)
                #else:
                    #print('\nLe produit ' + input_user + ' ne contient pas assez d\'informations pour être affiché. '
                          #'Veuillez faire une autre sélection\n')
            except ValueError:
                continue


def choose_product(product, category):
    """ Displaying selected product' specific information from OpenFoodFacts product page """

    while True:
        input_user = input(App_Selected_Product_Menu)

        if input_user == '1':
            display_product_characteristics(product)

        elif input_user == '2':
            display_product_nutriscore(product)

        elif input_user == '3':
            display_product_link_off(product)

        elif input_user == '4':
            suggest_substitute(product, category)

        elif input_user == '0':
            return
        else:
            continue


def suggest_substitute(product, category):
    """ Using the OpenFoodFacts Api to access to 3 substitutes_db potentially better and displaying them """

    page = 1
    better_products = []
    if 'nutrition_grades' not in product or product['nutrition_grades'] == '':
        print('\nImpossible de faire une recherche de substitut sur ce produit car son indice '
              'nutritionnel n\'est pas renseigné.\n')
        return

    else:
        while len(better_products) < 3:
            r_substitutes = requests.get(category['url'] + '/{}.json'.format(page))
            response = r_substitutes.json()
            substitutes = response['products']

            for substitute in substitutes:
                if 'nutrition_grades' in substitute and 'nutrition_grades' in product and \
                        product['nutrition_grades'] != '':
                    if substitute['nutrition_grades'] < product['nutrition_grades'] or\
                        (substitute['nutrition_grades'] == product['nutrition_grades']
                            and product['nutrition_grades'] == 'a'):
                        better_products.append(substitute)

                    if len(better_products) == 3:
                        break

            page += 1

    while True:
        print('\nVoici nos 3 suggestions de substitut :\n')

        for idx, substitute in enumerate(better_products):
            print(idx+1, substitute['product_name'])

        input_user = input(App_Suggested_Product_Menu)

        if input_user == '1':
            display_substitute(better_products[0], product, category)

        elif input_user == '2':
            display_substitute(better_products[1], product, category)

        elif input_user == '3':
            display_substitute(better_products[2], product, category)

        elif input_user == '0':
            return
        else:
            continue


def display_substitute(substitute, product, category):
    """ Displaying substitute' specific information
    and allowing to save a substitute in personal database or to go from one substitute to the others """

    display_product_characteristics(substitute)
    display_product_nutriscore(substitute)
    display_product_link_off(substitute)

    while True:
        input_user = input(App_Save_Substitute_Menu)
        if input_user == '1':
            save_substitute(substitute, product, category)
        elif input_user == '2':
            return
        elif input_user == '0':
            find_or_substitute()
        else:
            continue


def display_product_characteristics(product):
    """ Specific information to be displayed, selected from OpenFoodFacts product page """

    print('\nCARACTERISTIQUES DU PRODUIT ' + product['product_name'])
    if 'brands' not in product or product['brands'] == '':
        print('\nMarque                                   : non renseigné')
    else:
        print('\nMarque                                   : '+product['brands'])

    if 'categories' not in product or product['categories'] == '':
        print('Catégorie                                : non renseigné')
    else:
        print('Catégories                               : '+product['categories'])

    if 'origins' not in product or product['origins'] == '':
        print('Origine                                  : non renseigné')
    else:
        print('Origine des ingrédients                  : '+product['origins'])

    if 'manufacturing_places' not in product or product['manufacturing_places'] == '':
        print('Lieu de fabrication ou de transformation : non renseigné')
    else:
        print('Lieu de fabrication ou de transformation : '+product['manufacturing_places'])

    if 'countries' not in product or product['countries'] == '':
        print('Pays de vente                            : non renseigné')
    else:
        print('Pays de vente                            : '+product['countries'])

    if 'stores' not in product or product['stores'] == '':
        print('Magasins de vente                        : non renseigné')
    else:
        print('Magasins où acheter le produit           : '+product['stores'])


def display_product_nutriscore(product):
    """ Nutriscore range selected from OpenFoodFacts product page """

    print(App_Nutri_Score)
    if 'nutrition_grades' not in product or product['nutrition_grades'] == '':
        print('Classement Nutri-Score du produit ' + product['product_name'] + ': non renseigné')
    else:
        print('Classification NUTRI-SCORE  ' + product['product_name'] + ' = ' + product['nutrition_grades'].upper())


def display_product_link_off(product):
    """ Link to OpenFoodFacts product page """

    print('\nLIEN vers la fiche du produit ' + product['product_name'] + ' sur OpenFoofFacts : ' + product['url'])


#####################################################
""" SCRIPT SECOND PART : USER'S PERSONAL DATABASE """
#####################################################


def save_substitute(substitute, product, category):
    """ Saving the substitute(s) and the original product in the user's personal database """

    try:
        category_db = CategoryDb.objects.get(name=category['name'])
    except ObjectDoesNotExist:
        category_db = CategoryDb(name=category['name'])
        category_db.save()

    checking_tags_names_for_db(substitute)
    substitute_db = ProductDb(name=substitute['product_name'], category=category_db, brand=substitute['brands'],
                              origin=substitute['origins'], manufacturing_places=substitute['manufacturing_places'],
                              countries=substitute['countries'], store=substitute['stores'],
                              nutriscore=substitute['nutrition_grades'])
    substitute_db.save()

    checking_tags_names_for_db(product)
    try:
        product_db = ProductDb.objects.get(name=product['product_name'])
    except ObjectDoesNotExist:
        product_db = ProductDb(name=product['product_name'], category=category_db, brand=product['brands'],
                               origin=product['origins'], manufacturing_places=product['manufacturing_places'],
                               countries=product['countries'], store=product['stores'],
                               nutriscore=product['nutrition_grades'])
        product_db.save()

    historic_db = HistoricDb(product_original=product_db, product_replaceable=substitute_db)
    historic_db.save()

    print('Le produit ', product_db, 'et son substitut ', substitute_db, ' ont bien été enregistrés '
                                                                             'dans votre base de données '
                                                                             'personnelle.')


def checking_tags_names_for_db(item):
    """ Making sure that the lines in database are not NULL """

    if 'product_name' not in item:
        item['product_name'] = ''
    if 'brands' not in item:
        item['brands'] = ''
    if 'origins' not in item:
        item['origins'] = ''
    if 'manufacturing_places' not in item:
        item['manufacturing_places'] = ''
    if 'countries' not in item:
        item['countries'] = ''
    if 'stores' not in item:
        item['stores'] = ''
    if 'nutrition_grades' not in item:
        item['nutrition_grades'] = ''


def substitutes():
    """ Accessing to the personal's database : the products are organized by categories"""

    while True:

        input_user = input(App_DB_Menu)

        if input_user == '1':
            selecting_a_category()

        else:
            try:
                if input_user == '0':
                    return
            except ValueError:
                continue


def selecting_a_category():
    """ To access to a product saved in personal's database : step 1
    --> the user selects a category. """

    categories_db = CategoryDb.objects.all().order_by('id')
    p = Paginator(categories_db, 5)
    page_number = 1
    page = p.page(page_number)

    while True:
        for idx, category in enumerate(page.object_list):
            print(idx+1, category.name)

        input_user = input(App_DB_Cat_Menu)

        if input_user == '0':
            return

        elif input_user == 's' and page.has_next():
            page = p.page(page_number+1)
            page_number += 1

        elif input_user == 'p' and page.has_previous():
            page = p.page(page_number-1)
            page_number -= 1

        else:
            try:
                selection = int(input_user)
                if len(page.object_list) >= selection >= 1:
                    show_historic_substitution(page.object_list[selection-1])
            except ValueError:
                continue


def show_historic_substitution(category):
    """" Step 2
    --> the user prints on screen the historic (substituted products and their substitutes) from this category
    and choose a product."""

    print('Voici l\'historique de la catégorie :', category, '\n')

    products_db = HistoricDb.objects.filter(product_original__category=category).order_by('id')
    """for product in products_db:
        print(product.product_original, product.product_replaceable)"""
    p = Paginator(products_db, 1)
    page_number = 1
    page = p.page(page_number)
    page_ids = []

    while True:
        for product in page.object_list:
            print('Produit n°', product.product_original.id, ':', product.product_original,
                  '; Substitut n°', product.product_replaceable.id, ':', product.product_replaceable)
            page_ids.append(product.product_original.id)
            page_ids.append(product.product_replaceable.id)

            input_user = input(App_Products_Menu)

            if input_user == '0':
                return

            elif input_user == 's' and page.has_next():
                page = p.page(page_number + 1)
                page_number += 1

            elif input_user == 'p' and page.has_previous():
                page = p.page(page_number - 1)
                page_number -= 1

            else:
                try:
                    selection = int(input_user)
                    if selection in page_ids:
                        display_product_db(ProductDb.objects.get(id=selection))
                except ValueError:
                    continue


def display_product_db(product):
    """ Step 3
    -->the user print on screen the choosen product's characteristics."""

    print('\nVoici les caractéristiques du produit ', product.name, '\n')

    if product.category == '':
        print('Catégorie            : non renseigné')
    else:
        print('Catégorie            :', product.category)

    if product.brand == '':
        print('Marque               : non renseigné')
    else:
        print('Marque               :', product.brand)

    if product.origin == '':
        print('Origine              : non renseigné')
    else:
        print('Origine              :', product.origin)

    if product.manufacturing_places == '':
        print('Lieux de fabrication : non renseigné')
    else:
        print('Lieux de fabrication :', product.manufacturing_places)

    if product.countries == '':
        print('Pays                 : non renseigné')
    else:
        print('Pays                 :', product.countries)

    if product.store == '':
        print('Magasins             : non renseigné')
    else:
        print('Magasins             :', product.store)

    if product.nutriscore == '':
        print('Indice Nutriscore    : non renseigné')
    else:
        print('Indice Nutriscore    :', product.nutriscore.upper(), '\n')


if __name__ == '__main__':
    print(App_Title)
    print(App_Intro)

    find_or_substitute()
