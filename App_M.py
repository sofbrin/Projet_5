#! /usr/bin/env python
# coding: utf8

import sys
import requests as requests

from constants import App_Title, App_Intro, App_Home_Menu, App_Category_Menu, App_Product_Menu, end_of_App


def choice_product(category):
    pass


def choice_substitute():
    pass


def choice_category():
    r_category = requests.get('https://fr.openfoodfacts.org/categories.json')
    response = r_category.json()
    categories = response['tags']

    page = 1
    while True:
        for idx, category in enumerate(categories[page*10-10:page*10]):
            print(idx, category['name'])

        input_user = input(App_Category_Menu)
        if input_user == 's':
            page += 1
        elif input_user == 'p':
            page -= 1
        else:
            try:
                selection = int(input_user)
                if 9 >= selection >= 0:
                    choice_product(categories[page*10-10+selection])
            except ValueError:
                continue


def choice1():
    while True:
        user_input = input(App_Home_Menu)
        if user_input == '1':
            choice_category()
        elif user_input == '2':
            choice_substitute()
        else:
            print(end_of_App)
            sys.exit()


if __name__ == '__main__':
    print(App_Title)
    print(App_Intro)

    choice1()
