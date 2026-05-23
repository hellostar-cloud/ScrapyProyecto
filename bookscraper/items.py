import scrapy


class BookItem(scrapy.Item):
    """Define los campos estructurados que extrae el spider."""

    title        = scrapy.Field()   # Título del libro
    price        = scrapy.Field()   # Precio en float (sin símbolo £)
    rating       = scrapy.Field()   # Calificación numérica 1-5
    availability = scrapy.Field()   # "In stock" / "Out of stock"
    category     = scrapy.Field()   # Categoría del libro
    product_url  = scrapy.Field()   # URL de la página del libro
