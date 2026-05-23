# ============================================================
# Configuración del proyecto Scrapy — Books Scraper
# ============================================================

BOT_NAME = "bookscraper"

SPIDER_MODULES = ["bookscraper.spiders"]
NEWSPIDER_MODULE = "bookscraper.spiders"

# ---- Comportamiento responsable ----
# Identifica el bot de forma honesta
USER_AGENT = "BooksScraperBot/1.0 (educational project)"

# Respeta robots.txt
ROBOTSTXT_OBEY = True

# Retraso entre peticiones (segundos) — evita saturar el servidor
DOWNLOAD_DELAY = 1.0

# Máximo de peticiones concurrentes
CONCURRENT_REQUESTS = 8
CONCURRENT_REQUESTS_PER_DOMAIN = 4

# ---- Pipelines activas ----
ITEM_PIPELINES = {
    "bookscraper.pipelines.DuplicateFilterPipeline": 100,
    "bookscraper.pipelines.PriceValidationPipeline": 200,
}

# ---- Exportación ----
# Codificación UTF-8 para CSV/JSON
FEED_EXPORT_ENCODING = "utf-8"

# Campos en el orden deseado para CSV
FEED_EXPORT_FIELDS = [
    "title",
    "price",
    "rating",
    "availability",
    "category",
    "product_url",
]

# ---- Logs ----
LOG_LEVEL = "INFO"

# ---- Caché (desactivada por defecto, útil para desarrollo) ----
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 3600
# HTTPCACHE_DIR = ".scrapy_cache"

# ---- Compatibilidad ----
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_BATCH_ITEM_COUNT = 0
