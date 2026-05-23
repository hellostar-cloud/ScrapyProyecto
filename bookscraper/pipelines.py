"""
Pipelines del proyecto.

DuplicateFilterPipeline
  — Descarta ítems con URLs duplicadas como segunda línea de defensa
    (el spider ya filtra con self.visited_urls, pero esta pipeline
     protege en caso de que se usen múltiples instancias o crawls).

PriceValidationPipeline
  — Descarta libros con precio 0 o negativo (datos corruptos).
"""
from scrapy.exceptions import DropItem


class DuplicateFilterPipeline:
    """Elimina libros duplicados basándose en product_url."""

    def __init__(self):
        self.seen_urls: set = set()

    def process_item(self, item, spider):
        url = item.get("product_url", "")
        if url in self.seen_urls:
            raise DropItem(f"Libro duplicado descartado: {url}")
        self.seen_urls.add(url)
        return item


class PriceValidationPipeline:
    """Descarta libros con precio inválido (0.0 o negativo)."""

    def process_item(self, item, spider):
        if item.get("price", 0) <= 0:
            raise DropItem(
                f"Precio inválido para: {item.get('title', 'desconocido')!r}"
            )
        return item
