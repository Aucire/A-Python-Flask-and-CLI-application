import requests

BASE = "https://world.openfoodfacts.org"
HEADERS = {"User-Agent": "InventoryLab/1.0 (student project)"}


def _get(url, params=None):
    try:
        resp = requests.get(url, params=params, headers=HEADERS)
        resp.raise_for_status()
        return resp.json()
    
    except requests.exceptions.RequestException:
        raise ConnectionError("Could not get a valid response from OpenFoodFacts...!")


def _slim(product):
    
    data = {
        "barcode": product.get("code") or product.get("_id", ""),
        "product_name": product.get("product_name", "Unknown"),
        "brands": product.get("brands", ""),
        "ingredients_text": product.get("ingredients_text", ""),
        "nutriscore": product.get("nutriscore_grade", ""),
        "quantity": product.get("quantity", ""),
        "categories": product.get("categories", ""),
    }

    return data

def fetch_by_barcode(barcode):

    if not str(barcode).isdigit():
        raise ValueError("Barcode must contain digits only")
    
    data = _get(f"{BASE}/api/v0/product/{barcode}.json")
    if data.get("status") != 1:
        return None
    
    product = data["product"]
    product.setdefault("code", str(barcode))
    return _slim(product)


def search_by_name(name, limit=2):
    if not name or not name.strip():
        raise ValueError("Search term cannot be empty")
    
    data = _get(
        f"{BASE}/cgi/search.pl",
        params={"search_terms": name, "search_simple": 1, "action": "process","json": 1, "page_size": limit},
    )
    products = [_slim(p) for p in data.get("products", [])]
    return products