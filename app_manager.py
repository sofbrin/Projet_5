#! /usr/bin/env python
# coding: utf8

import sys
import requests as requests


from constants import App_Title, App_Intro, App_Home_Menu, App_Categories_Menu, App_Products_Menu, \
    App_Selected_Product_Menu, App_Nutri_Score, App_Suggested_Product_Menu, App_Save_Substitute_Menu, end_of_App


def find_or_substitute():
    """ First Application menu :
    --> looking for a product in the OpenFoodFacts database
    --> looking for a substitute product already saved in the user's personal database """

    while True:
        input_user = input(App_Home_Menu)

        if input_user == '1':
            display_categories()
        elif input_user == '2':
            substituted_products()
        elif input_user == '3':
            print(end_of_App)
            sys.exit()


def display_categories():
    """ Using the OpenFoodFacts Api to access the categories, displaying them and selecting one of them """

    r_categories = requests.get('https://fr.openfoodfacts.org/categories.json')
    response = r_categories.json()
    categories = response['tags']

    page = 1

    while True:
        for idx, category in enumerate(categories[page*10-10:page*10]):
            print(idx, category['name'])

        input_user = input(App_Categories_Menu)

        if input_user == 's':
            page += 1
        elif input_user == 'p':
            page -= 1
        else:
            try:
                selection = int(input_user)
                if 9 >= selection >= 0:
                    display_products(categories[page*10-10+selection])
            except ValueError:
                continue


def display_products(category):
    """ Using the OpenFoodFacts Api to access the products, displaying them and selecting one of them """

    page = 1

    while True:
        r_products = requests.get(category['url'] + '/{}.json'.format(page))
        response = r_products.json()
        products = response['products']

        for idx, product in enumerate(products):
            print(idx, product['product_name'])

        input_user = input(App_Products_Menu)

        if input_user == 's':
            page += 1
        elif input_user == 'p':
            page -= 1
        else:
            try:
                selection = int(input_user)
                if 19 >= selection >= 0:
                    choose_product(products[selection], category)
            except ValueError:
                continue


def choose_product(product, category):
    """ Displaying selected product' specific information from OpenFoodFacts product page """

    while True:
        input_user = input(App_Selected_Product_Menu)

        if input_user == '1':
            display_product_caracteristics(product)

        elif input_user == '2':
            display_product_nutriscore(product)

        elif input_user == '3':
            display_product_link_off(product)

        elif input_user == '4':
            suggest_substitute(product, category)

        else:
            try:
                if input_user == '5':
                    find_or_substitute()
            except ValueError:
                continue


def suggest_substitute(product, category):
    """ Using the OpenFoodFacts Api to access to 3 products potentially better and displaying them """

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
                if 'nutrition_grades' in substitute and 'nutrition_grades' in product and product['nutrition_grades'] != '':
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
            print(idx, substitute['product_name'])

        input_user = input(App_Suggested_Product_Menu)

        if input_user == '0':
            save_substitute(better_products[0], product, category)

        elif input_user == '1':
            save_substitute(better_products[1], product, category)

        elif input_user == '2':
            save_substitute(better_products[2], product, category)

        else:
            return


def save_substitute(substitute, product, category):
    """ Displaying substitute' specific information
    and allowing to save a substitute in personal database or to go from one substitute to the others """

    display_product_caracteristics(substitute)
    display_product_nutriscore(substitute)
    display_product_link_off(substitute)

    while True:
        input_user = input(App_Save_Substitute_Menu)
        if input_user == '1':
            pass

        else:
            return


def display_product_caracteristics(product):
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


def substituted_products():
    pass


if __name__ == '__main__':
    print(App_Title)
    print(App_Intro)

    find_or_substitute()
