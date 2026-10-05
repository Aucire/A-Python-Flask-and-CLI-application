import requests

API = "http://127.0.0.1:5000"


def call(method, path, **kwargs):
    try:
        resp = requests.request(method, API + path, timeout=15, **kwargs)
        data = resp.json()
    except requests.exceptions.ConnectionError:
        print("Couldnt access the server...!")
        return None
    
    if not resp.ok:
        print(f"! Error of status {resp.status_code} occurred....!")
        return None
    
    return data


def show(item):
    p = item["product"]
    print(f"""
        [{item['id']}] 
        {p['product_name']} 
        ({p.get('brands')})
        Price: ${item['price']:.2f} | 
        stock: {item['stock']}
    """)
    if p.get("ingredients_text"):
        print(f"Ingredients: {p['ingredients_text']}")


def view_all():
    items = call("GET", "/inventory")
    if items is not None:
        for i in items:
            show(i)


def view_one():
    item_id = input("Enter item ID (must be an int) >> ")
    if not item_id.isdigit():
        print("ID must be whole number")
        return
    item = call("GET", f"/inventory/{item_id}")
    if item:
        show(item)
        print(f"Barcode: {item['product'].get('barcode', '')}")


def add_item():
    print("1) Add by barcode \n2) Add manually")
    mode = input(">> ").strip()
    price = input("Price >> ").strip()
    stock = input("Stock >> ").strip()
    
    body = {"price": price, "stock": stock}
    if mode == "1":
        body["barcode"] = input("Enter item's Barcode >> ").strip()
    elif mode == "2":
        body["product_name"] = input("Product name: ").strip()
        body["brands"] = input("Brand: ").strip()
    else:
        print("! Invalid choice.")
        return
    item = call("POST", "/inventory", json=body)
    if item:
        print("Added:")
        show(item)


def update_item():
    item_id = input("Enter Item ID >> ")
    if not item_id.isdigit():
        print("ID must be whole number...!")
        return
    body = {}
    price = input("New price >> ").strip()
    stock = input("New stock >> ").strip()
    if price:
        body["price"] = price
    if stock:
        body["stock"] = stock
    if not body:
        print("Nothing to update.")
        return
    item = call("PATCH", f"/inventory/{item_id}", json=body)
    if item:
        print("Updated:")
        show(item)


def delete_item():
    item_id = input("Enter Item ID >> ")
    if not item_id.isdigit():
        print("ID must be whole number")
        return

    result = call("DELETE", f"/inventory/{item_id}")
    if result:
        print(result["message"])


def find_on_api():

    print("1) Search by barcode\n2) Search by name")
    mode = input(" >> ").strip()

    if mode == "1":
        product = call("GET", f"/lookup/barcode/{input('Barcode: ').strip()}")
        results = [product] if product else []
    elif mode == "2":
        results = call("GET", "/lookup/search", params={"name": input("Name: ").strip()}) or []
    else:
        print("! Invalid choice.")
        return
    
    if not results:
        print("No results.")

    for r in results:
        print(f"- {r['product_name']} ({r['brands']}) barcode: {r['barcode']}")
    