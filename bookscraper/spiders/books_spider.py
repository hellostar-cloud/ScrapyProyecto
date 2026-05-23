import scrapy
from bookscraper.items import BookItem

# Mapa de categorías disponibles en books.toscrape.com
CATEGORY_URLS = {
    "travel":             "https://books.toscrape.com/catalogue/category/books/travel_2/index.html",
    "mystery":            "https://books.toscrape.com/catalogue/category/books/mystery_3/index.html",
    "historical-fiction": "https://books.toscrape.com/catalogue/category/books/historical-fiction_4/index.html",
    "sequential-art":     "https://books.toscrape.com/catalogue/category/books/sequential-art_5/index.html",
    "classics":           "https://books.toscrape.com/catalogue/category/books/classics_6/index.html",
    "philosophy":         "https://books.toscrape.com/catalogue/category/books/philosophy_7/index.html",
    "romance":            "https://books.toscrape.com/catalogue/category/books/romance_8/index.html",
    "womens-fiction":     "https://books.toscrape.com/catalogue/category/books/womens-fiction_9/index.html",
    "fiction":            "https://books.toscrape.com/catalogue/category/books/fiction_10/index.html",
    "childrens":          "https://books.toscrape.com/catalogue/category/books/childrens_11/index.html",
    "music":              "https://books.toscrape.com/catalogue/category/books/music_14/index.html",
    "science":            "https://books.toscrape.com/catalogue/category/books/science_22/index.html",
    "sports-and-games":   "https://books.toscrape.com/catalogue/category/books/sports-and-games_17/index.html",
    "default":            "https://books.toscrape.com/catalogue/page-1.html",
}

# Mapa textual → número para el rating
RATING_MAP = {
    "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5,
}


class BooksSpider(scrapy.Spider):
    """
    Spider que extrae libros de books.toscrape.com.

    Argumentos opcionales (usar con -a):
        category  — nombre de categoría (ej: travel, mystery, fiction…).
                    Si no se indica, recorre el catálogo general.
        pages     — número máximo de páginas a recorrer (por defecto: todas).

    Ejemplos de ejecución:
        scrapy crawl books -o resultados/books.csv
        scrapy crawl books -a category=travel -o resultados/travel.json
        scrapy crawl books -a category=mystery -a pages=3 -o resultados/mystery.csv
    """

    name = "books"
    allowed_domains = ["books.toscrape.com"]

    # ------------------------------------------------------------------ #
    #  Inicialización                                                       #
    # ------------------------------------------------------------------ #

    def __init__(self, category=None, pages=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Parámetro: categoría
        self.category = category.lower().strip() if category else None

        # Parámetro: límite de páginas (None = sin límite)
        try:
            self.max_pages = int(pages) if pages else None
        except ValueError:
            self.logger.warning(
                f"El valor de 'pages' no es válido: {pages!r}. Se usarán todas las páginas."
            )
            self.max_pages = None

        # Contador de páginas por categoría visitada
        self.page_count = 0

        # Conjunto de URLs visitadas — evita duplicados
        self.visited_urls: set = set()

    async def start(self):
        """Genera la primera petición según categoría o catálogo general."""
        if self.category:
            url = CATEGORY_URLS.get(self.category)
            if url:
                self.logger.info(
                    f"Iniciando scraping — Categoría: {self.category!r} | Límite: {self.max_pages or 'sin límite'} página(s)"
                )
                yield scrapy.Request(url, callback=self.parse_listing)
            else:
                self.logger.error(
                    f"Categoría '{self.category}' no reconocida. "
                    f"Categorías disponibles: {', '.join(CATEGORY_URLS.keys())}"
                )
        else:
            self.logger.info(
                f"Iniciando scraping — Catálogo general | Límite: {self.max_pages or 'sin límite'} página(s)"
            )
            yield scrapy.Request(CATEGORY_URLS["default"], callback=self.parse_listing)

    # ------------------------------------------------------------------ #
    #  Parseo del listado                                                   #
    # ------------------------------------------------------------------ #

    def parse_listing(self, response):
        """Recorre la página de listado, entra a cada libro y maneja la paginación."""
        self.page_count += 1
        self.logger.info(f"Página {self.page_count}: {response.url}")

        # Determinar la categoría actual desde el breadcrumb
        breadcrumb = response.css("ul.breadcrumb li:last-child a::text").get()
        current_category = (breadcrumb or self.category or "General").strip()

        # Extraer links de libros en esta página
        book_links = response.css("article.product_pod h3 a::attr(href)").getall()

        for link in book_links:
            absolute_url = response.urljoin(link)

            # Evitar duplicados
            if absolute_url in self.visited_urls:
                continue
            self.visited_urls.add(absolute_url)

            yield scrapy.Request(
                absolute_url,
                callback=self.parse_book,
                cb_kwargs={"category": current_category},
            )

        # ---- Paginación ----
        if self.max_pages and self.page_count >= self.max_pages:
            self.logger.info(
                f"Límite de {self.max_pages} página(s) alcanzado. Deteniendo paginación."
            )
            return

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield scrapy.Request(
                response.urljoin(next_page),
                callback=self.parse_listing,
            )

    # ------------------------------------------------------------------ #
    #  Parseo del detalle de cada libro                                     #
    # ------------------------------------------------------------------ #

    def parse_book(self, response, category):
        """Extrae y limpia los datos de la página de detalle de un libro."""
        item = BookItem()

        # Título
        item["title"] = response.css("div.product_main h1::text").get("").strip()

        # Precio → limpiar símbolo £ y convertir a float
        raw_price = response.css("p.price_color::text").get("")
        item["price"] = self._clean_price(raw_price)

        # Rating → convertir palabra a número
        rating_class = response.css("p.star-rating::attr(class)").get("")
        item["rating"] = self._clean_rating(rating_class)

        # Disponibilidad → solo "In stock" o "Out of stock"
        raw_availability = response.css("p.availability::text").getall()
        item["availability"] = self._clean_availability(raw_availability)

        # Categoría (pasada desde parse_listing)
        item["category"] = category

        # URL del producto
        item["product_url"] = response.url

        yield item

    # ------------------------------------------------------------------ #
    #  Métodos de limpieza                                                  #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _clean_price(raw: str) -> float:
        """Elimina el símbolo £ (y cualquier carácter no numérico) y convierte a float."""
        cleaned = "".join(c for c in raw if c.isdigit() or c == ".")
        try:
            return float(cleaned)
        except ValueError:
            return 0.0

    @staticmethod
    def _clean_rating(class_attr: str) -> int:
        """Convierte 'star-rating Three' → 3."""
        for word, number in RATING_MAP.items():
            if word in class_attr:
                return number
        return 0

    @staticmethod
    def _clean_availability(texts: list) -> str:
        """Extrae solo 'In stock' o 'Out of stock' del texto."""
        joined = " ".join(t.strip() for t in texts if t.strip())
        if "In stock" in joined:
            return "In stock"
        if "Out of stock" in joined:
            return "Out of stock"
        return joined.strip() or "Unknown"
