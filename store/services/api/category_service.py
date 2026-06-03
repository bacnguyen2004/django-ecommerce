from store.models.category import Category

def get_categories():

    return Category.objects.filter(
        status=True
    )

