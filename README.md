# Scrapy Books Scraper

Spider educativo que extrae información de libros desde [books.toscrape.com](https://books.toscrape.com), un sitio diseñado específicamente para practicar web scraping.

---

## Objetivo

Demostrar el uso de **Scrapy** para:
- Crawling automático con paginación
- Extracción estructurada con CSS selectors
- Limpieza de datos
- Exportación a CSV y JSON
- Parámetros dinámicos en el spider

---

## Tecnologías

| Herramienta    | Uso                    |
|----------------|------------------------|
| Python 3.10+   | Lenguaje principal     |
| Scrapy 2.13+   | Framework de scraping  |
| CSS Selectors  | Extracción HTML        |
| CSV / JSON     | Exportación de datos   |

---

## Instalación

```bash
# 1. Crear y activar entorno virtual
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / Mac
source venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt
```

---

## Estructura del proyecto

```
scrapy_books_project/
│
├── bookscraper/
│   ├── spiders/
│   │   └── books_spider.py   ← Spider principal
│   │
│   ├── items.py              ← Definición de campos
│   ├── pipelines.py          ← Filtros y validaciones
│   └── settings.py           ← Configuración del proyecto
│
├── resultados/
│   ├── books.csv             ← Resultado en CSV
│   └── books.json            ← Resultado en JSON
│
├── requirements.txt
├── README.md
└── scrapy.cfg
```

---

## Ejecución

### Catálogo general (todas las categorías)

```bash
scrapy crawl books -o resultados/books.csv
scrapy crawl books -o resultados/books.json
```

### Filtrar por categoría

```bash
scrapy crawl books -a category=travel -o resultados/travel.csv
scrapy crawl books -a category=mystery -o resultados/mystery.json
scrapy crawl books -a category=fiction -o resultados/fiction.csv
```

### Limitar número de páginas

```bash
scrapy crawl books -a pages=3 -o resultados/books.csv
scrapy crawl books -a category=romance -a pages=2 -o resultados/romance.json
```

---

## Parámetros disponibles

| Parámetro  | Descripción                                         | Ejemplo            |
|------------|-----------------------------------------------------|--------------------|
| `category` | Categoría a scrapear (ver lista abajo)             | `-a category=travel` |
| `pages`    | Límite de páginas a recorrer                        | `-a pages=5`       |

### Categorías disponibles

`travel`, `mystery`, `historical-fiction`, `sequential-art`, `classics`, `philosophy`, `romance`, `womens-fiction`, `fiction`, `childrens`, `music`, `science`, `sports-and-games`

---

## Datos extraídos

Por cada libro se obtiene:

| Campo          | Tipo    | Descripción                        |
|----------------|---------|------------------------------------|
| `title`        | str     | Título del libro                   |
| `price`        | float   | Precio en libras (sin símbolo £)   |
| `rating`       | int     | Calificación del 1 al 5            |
| `availability` | str     | "In stock" / "Out of stock"        |
| `category`     | str     | Categoría del libro                |
| `product_url`  | str     | URL de la página del libro         |

---

## Adaptaciones propias

1. **Filtro por categoría** — parámetro `-a category=` que apunta directamente a la URL de esa sección.
2. **Límite de páginas** — parámetro `-a pages=` que detiene la paginación al alcanzar el número indicado.
3. **Limpieza de precio** — elimina el símbolo `£` y convierte a `float` (ej: `£51.77` → `51.77`).
4. **Limpieza de rating** — convierte el texto CSS en número (ej: `star-rating Three` → `3`).
5. **Limpieza de disponibilidad** — extrae solo `"In stock"` o `"Out of stock"` del texto completo.
6. **Deduplicación doble** — el spider rastrea URLs visitadas con un `set`, y la pipeline `DuplicateFilterPipeline` actúa como segunda capa de defensa.
7. **Validación de precio** — la pipeline `PriceValidationPipeline` descarta ítems con precio `0` o negativo.

---

## Dificultades encontradas

| Problema                        | Solución aplicada                              |
|---------------------------------|------------------------------------------------|
| URLs relativas en los links     | `response.urljoin(link)` para hacer absolutas |
| Símbolo `£` en precio          | Filtrado carácter a carácter antes de `float()` |
| Rating almacenado como clase CSS | Mapa `RATING_MAP` palabra → número            |
| Texto con espacios en disponibilidad | `.strip()` + búsqueda de substring        |
| Posibles duplicados al paginar  | `set()` de URLs visitadas + pipeline          |

---

## Conceptos clave de Scrapy

- **Spider** — clase que define qué URLs visitar y cómo procesar las respuestas.
- **`async def start()`** — método que genera las peticiones iniciales.
- **`parse_listing()`** — parsea listados de libros y genera nuevas peticiones.
- **`parse_book()`** — parsea la página de detalle de cada libro.
- **`response.css()`** — extrae datos usando selectores CSS.
- **`yield`** — devuelve ítems o nuevas `Request` sin detener la ejecución.
- **Pipeline** — clase que procesa cada ítem después de ser extraído.
