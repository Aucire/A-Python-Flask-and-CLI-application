from flask import Flask, jsonify, request, render_template
from api import fetch_by_barcode, search_by_name

app = Flask(__name__)

inventory = [
    {
        "id": 1, 
        "status": 1, 
        "price": 3.99, 
        "stock": 24,
        "product": {
            "barcode": "0000000000001", "product_name": "Organic Almond Milk",
            "brands": "Silk",
            "ingredients_text": "Filtered water, almonds, cane sugar, sea salt"}},

    {
        "id": 2, 
        "status": 1, 
        "price": 2.49, 
        "stock": 40,
        "product": {
            "barcode": "3017620422003", "product_name": "Nutella",
            "brands": "Ferrero",
            "ingredients_text": "Sugar, palm oil, hazelnuts, skimmed milk powder, cocoa"}},

    {
        "id": 3, 
        "status": 1, 
        "price": 1.79, 
        "stock": 12,
        "product": {
            "barcode": "0000000000003", "product_name": "Whole Wheat Bread",
            "brands": "Baker's Best",
            "ingredients_text": "Whole wheat flour, water, yeast, salt"}},
]

def find_item(item_id):
    for item in inventory:
        if item["id"] == item_id:
            return item

    return None


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/inventory", methods=["GET"])
def get_inventory():
    return jsonify(inventory), 200


@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = find_item(item_id)

    if not item:
        return jsonify({"error":"Item not found"}), 404
    
    return jsonify(item), 200


@app.route("/inventory", methods=["POST"])
def add_item():

    data = request.get_json()
    
    if not data:
        return jsonify({"error":"Request body must be JSON"}), 400

    price = float(data.get("price", 0))
    stock = int(data.get("stock", 0))

    barcode = data.get("barcode")
    product_name = data.get("product_name")

    if not isinstance(price, float):
        return jsonify({"error":"This must be an Float"}), 400
    if not isinstance(stock, int):
        return jsonify({"error":"This must be an interger"}), 400

    product = None

    if barcode:
        try:
            product = fetch_by_barcode(data["barcode"])
        except ValueError as error:
            return jsonify({"error":str(error)}),400
        
        if product is None:
            return jsonify({"error":"Barcode not found on OpenFoodFacts"}), 404
    elif product_name:
        product = {
            "barcode": data.get("barcode", ""),
            "product_name": data["product_name"],
            "brands": data.get("brands", ""),
            "ingredients_text": data.get("ingredients_text", "")}
    else:
        return jsonify({"error":"Provide a 'barcode' or a 'product_name'"}), 400

    next_id = max(item["id"] for item in inventory) + 1
    item = {
        "id": next_id, 
        "status": 1, 
        "price": price, 
        "stock": stock,
        "product": product
    }

    inventory.append(item)
    return jsonify(item), 201


@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    item = find_item(item_id)
    if not item:
        return jsonify({"error":"Item not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error":"Request body must be JSON"}), 400

    if "price" not in data and "stock" not in data:
        return jsonify({"error":"Price/Stock cant be empty"}), 400

    
    new_price = float(data.get("price",0))
    new_stock = int(data.get("stock",0))


    item["price"] = new_price
    item["stock"] = new_stock
    return jsonify(item), 200


@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = find_item(item_id)
    if not item:
        return jsonify({"error":"Item not found"}), 404

    inventory.remove(item)
    return jsonify({"message": f"Item {item_id} deleted"}), 200


@app.route("/lookup/barcode/<barcode>", methods=["GET"])
def lookup_barcode(barcode):

    try:
        product = fetch_by_barcode(barcode)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    if not product:
        return jsonify({"error":"Product not found...!"}), 404

    return jsonify(product), 200


@app.route("/lookup/search", methods=["GET"])
def lookup_search():
    name = request.args.get("name", "")

    if not name.strip():
        return jsonify({"error":"Product not found...!"}), 404
    
    return jsonify(search_by_name(name)), 200



if __name__ == "__main__":
    app.run(debug=True)   