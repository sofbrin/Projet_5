import os
import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "purbeurre.settings")
django.setup()

from substitutes_db.models import SubstituteDb, CategoryDb

if __name__ == '__main__':
    category = CategoryDb.objects.get(id=1)
    products = SubstituteDb.objects.filter(category=category)


"""
    for product in substitutes_db:
        print(product.category.name, product.name)

    
    product = Product(name='fromage', description='bla', store='bla', substitute='bla',
                      category=category)
    product.save()




    category = Category(name='produits laitiers')
    category.save()

    product = Product(name='lait', description='bla', store='bla', substitute='bla',
                      category=category)
    product.save()

    # lister les produits de la bdd
    substitutes_db = Product.objects.all()
    for product in substitutes_db:
        print(product.name)

    # créer les prdoduits dans la bdd
    product = Product(name='lait')
    product.category ='produits laitiers'
    product.description ='bla bla bla'
    product.store ='bla bla bla'
    product.substitute =' bla bla bla'
    product.save()"""


