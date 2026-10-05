===========================================================================================
# INVENTORY MANAGEMENT SYSTEM (Flask + OpenFoodFacts)
===========================================================================================

## 1. ABOUT THE PROJECT
--------------------------------------------------------------------------
This is a small inventory management system I built for my lab. It has a
Flask REST API that manages an inventory of food products, a command line
tool (CLI) to use the API from the terminal, and a simple web page to use
it from the browser.

The system also connects to the OpenFoodFacts API so that I can look up
real product details (name, brand, ingredients) using a barcode or a
product name, and add those products to my inventory.

There is no real database. The inventory is stored in a Python list
(array) inside app.py, which simulates storage. This means all changes are
lost when the server is restarted.


## 2. WHAT IT CAN DO
--------------------------------------------------------------------------
- View all items in the inventory
- View one item by its ID
- Add a new item (manually, or by barcode so details come from the API)
- Update the price and/or stock of an item
- Delete an item
- Find a product on OpenFoodFacts by barcode or by name
- Handle errors for invalid input and API failures


## 3. PROJECT STRUCTURE
--------------------------------------------------------------------------
```python
inventory-lab/
|-- app.py              The Flask API (all the routes + the mock database)
|-- api.py              Functions that fetch data from OpenFoodFacts
|-- cli.py              The CLI menu (only the menu loop)
|-- helper_fns.py       Helper functions used by the CLI
|-- requirements.txt    Python packages needed (flask, requests)
|-- templates/
|   |-- index.html      The web page
|-- static/
    |-- main.js         JavaScript for the web page
```
``
Note: Flask only serves JavaScript files from the "static" folder, and it
only finds HTML files inside the "templates" folder, so main.js and
index.html must be placed exactly there.
``

## 4. SETUP AND INSTALLATION
--------------------------------------------------------------------------
### Step 1: Clone or download the project and open the project folder.
```bash
    git clone <my-repo-link>
    cd inventory-lab
```
### Step 2: Create and activate a virtual environment.
```bash
    python3 -m venv venv

    Linux / Mac:   source venv/bin/activate
    Windows:       venv\Scripts\activate
```
### Step 3: Install the required packages.
```bash
    pip install -r requirements.txt

    (or: python3 -m pip install flask requests)
```
### Step 4: Start the server.
```bash
    python3 app.py

    The server runs at http://127.0.0.1:5000
```
### Step 5: Use the app in one of two ways.
```
    a) Web page: open http://127.0.0.1:5000 in the browser.
    b) CLI: open a SECOND terminal (with the venv activated) and run
```
```bash
           python3 cli.py
```
IMPORTANT: The server (app.py) must be running before using the CLI,
otherwise the CLI will say it cannot reach the server.


## 5. THE MOCK DATABASE
--------------------------------------------------------------------------
The inventory is a list of dictionaries stored in app.py. Each item has
its own ID, a price, a stock count, and a "product" section that looks
like what OpenFoodFacts returns.
```bash
Example item:

{
    "id": 1,
    "status": 1,
    "price": 3.99,
    "stock": 24,
    "product": {
        "barcode": "0000000000001",
        "product_name": "Organic Almond Milk",
        "brands": "Silk",
        "ingredients_text": "Filtered water, almonds, cane sugar, sea salt"
    }
}
```

Fields:
- id                 Unique number for the item (created automatically)
- status             1 means the item is valid, like the API's status field
- price              Price of the item (a number, can have decimals)
- stock              How many are in stock (a whole number)
- product            Product details, copied from OpenFoodFacts or typed in
    - barcode            Product barcode
    - product_name       Name of the product
    - brands             Brand of the product
    - ingredients_text   Ingredients of the product

The list starts with 3 sample items (Organic Almond Milk, Nutella and
Whole Wheat Bread).


## 6. ROUTE PLANNING
--------------------------------------------------------------------------
For every route I planned the inputs, the output, what it changes in the
data, and when it is triggered in the CLI.

--------------------------------------------------------------------------
#### ROUTE 1: GET /inventory
--------------------------------------------------------------------------
```bash
Purpose:   Fetch all the items
Input:     None
Output:    A list of all items (200)
Changes:   Nothing, it only reads the data
CLI:       Option 1 "View all the inventories"
```
--------------------------------------------------------------------------
#### ROUTE 2: GET /inventory/<id>
--------------------------------------------------------------------------
```bash
Purpose:   Fetch a single item
Input:     The item ID in the URL
Output:    The item (200), or an error if it does not exist (404)
Changes:   Nothing, it only reads the data
CLI:       Option 2 "View one inventory"
```
--------------------------------------------------------------------------
#### ROUTE 3: POST /inventory
--------------------------------------------------------------------------
```bash
Purpose:   Add a new item
Input:     JSON body with
             - "barcode" (details are fetched from OpenFoodFacts)
               OR "product_name" (and optionally "brands",
               "ingredients_text") to add it manually
             - "price" and "stock" (both optional, default to 0)
Output:    The new item (201)
           400 for bad input (not JSON, bad price or stock, negative
               numbers, or no barcode and no product name)
           404 if the barcode is not found on OpenFoodFacts
           502 if the OpenFoodFacts API fails
Changes:   Adds a new item to the end of the inventory list with a new
           ID (the highest ID + 1)
CLI:       Option 3 "Add an inventory"
```
--------------------------------------------------------------------------
#### ROUTE 4: PATCH /inventory/<id>
--------------------------------------------------------------------------
```bash
Purpose:   Update the price and/or stock of an item
Input:     The item ID in the URL, and a JSON body with "price" and/or
           "stock"
Output:    The updated item (200)
           404 if the item does not exist
           400 for bad input (not JSON, nothing to update, invalid or
               negative numbers)
Changes:   Edits the price and/or stock of that item. Nothing is changed
           if any of the input is invalid.
CLI:       Option 4 "Update price/stock"
```
--------------------------------------------------------------------------
#### ROUTE 5: DELETE /inventory/<id>
--------------------------------------------------------------------------
```bash
Purpose:   Remove an item
Input:     The item ID in the URL
Output:    A confirmation message (200), or 404 if it does not exist
Changes:   Removes the item from the inventory list
CLI:       Option 5 "Delete item"
```
--------------------------------------------------------------------------
#### ROUTE 6: GET /lookup/barcode/<barcode>
--------------------------------------------------------------------------
```bash
Purpose:   Find a product on OpenFoodFacts using its barcode
Input:     The barcode (digits only) in the URL
Output:    The product details (200)
           404 if the product is not found
           400 if the barcode has anything other than digits
           502 if the OpenFoodFacts API fails
Changes:   Nothing, it does not touch the inventory
CLI:       Option 6 "Find item on OpenFoodFacts" then "Search by
           barcode"
```
--------------------------------------------------------------------------
#### ROUTE 7: GET /lookup/search?name=<name>
--------------------------------------------------------------------------
```bash
Purpose:   Find products on OpenFoodFacts using a product name
Input:     The product name as the "name" query parameter
Output:    A list of matching products (200), limited to 2 results
           400 if the name is empty
           502 if the OpenFoodFacts API fails
Changes:   Nothing, it does not touch the inventory
CLI:       Option 6 "Find item on OpenFoodFacts" then "Search by name"
```


## 7. HOW THE OPENFOODFACTS API IS USED
------------------------------------
All the code for the external API is in api.py.

- ```fetch_by_barcode(barcode)```
  Checks the barcode has only digits, then calls the OpenFoodFacts
  product endpoint. It returns the product details, or None if the
  product was not found.

- ``search_by_name(name, limit=2)``
  Checks the name is not empty, then calls the OpenFoodFacts search
  endpoint and returns a list of matching products.

- ``_get(url, params)``
  A helper that makes the request. It has a timeout and turns any
  request problem (no internet, timeout, bad response) into a
  ConnectionError so that app.py can return a clean error message.

- ``_slim(product)``
  A helper that keeps only the fields I need from the large API
  response (barcode, product name, brands, ingredients, nutriscore,
  quantity and categories). The leading underscore shows these two
  helpers are for internal use inside api.py.

When an item is added by barcode, the details from OpenFoodFacts are
saved into the item's "product" section, which enhances the stored
inventory data.


## 8. HOW TO USE THE CLI
---------------------
Run `` python3 cli.py`` and choose from the menu:

    1. View all the inventories
    2. View one inventory
    3. Add an inventory
    4. Update price/stock
    5. Delete item
    6. Find item on OpenFoodFacts
    7. Quit




## 9. HOW TO USE THE WEB PAGE
--------------------------
Open http://127.0.0.1:5000 in the browser. On the page I can:
- See all the items in a table
- Add an item using a barcode or a product name, with price and stock
- Change a price or stock directly in the table (it saves when I click
  away from the box)
- Delete an item with the Delete button
- Search OpenFoodFacts by name, then click "Use barcode" to copy a
  barcode into the add form
- See error messages at the top of the page


## 10. ERROR HANDLING
------------------
- Invalid price or stock (letters, negative numbers, decimals in stock)
  returns a 400 error with a clear message
- An item ID that does not exist returns a 404 error
- A request without a JSON body returns a 400 error
- A barcode that is not only digits returns a 400 error
- A barcode not found on OpenFoodFacts returns a 404 error
- If OpenFoodFacts is down, slow or there is no internet, the API
  returns a 502 error
- The CLI checks that IDs are whole numbers, prints the server's error
  message, and tells me if the server is not running, instead of
  crashing
- The web page shows the error message at the top, and a message if the
  server cannot be reached


## 11. TESTING WITH CURL (OPTIONAL)
--------------------------------
Get all items:
    curl http://127.0.0.1:5000/inventory

Get one item:
    curl http://127.0.0.1:5000/inventory/1

Add an item manually:
    curl -X POST http://127.0.0.1:5000/inventory \
         -H "Content-Type: application/json" \
         -d '{"product_name": "Orange Juice", "price": 2.5, "stock": 10}'

Add an item by barcode:
    curl -X POST http://127.0.0.1:5000/inventory \
         -H "Content-Type: application/json" \
         -d '{"barcode": "3017620422003", "price": 4.5, "stock": 20}'

Update an item:
    curl -X PATCH http://127.0.0.1:5000/inventory/1 \
         -H "Content-Type: application/json" \
         -d '{"price": 4.25, "stock": 30}'

Delete an item:
    curl -X DELETE http://127.0.0.1:5000/inventory/1

Look up a barcode:
    curl http://127.0.0.1:5000/lookup/barcode/3017620422003

Search by name:
    curl "http://127.0.0.1:5000/lookup/search?name=nutella"



## 12. TOOLS USED
--------------
```bash
- Python 3
- Flask (API and routing)
- Requests (calls to OpenFoodFacts and from the CLI to the API)
- OpenFoodFacts API (product data)
- HTML and JavaScript (web page)
- Git and GitHub (version control)
```

## 15. AUTHOR
----------
James Osire

Software Engineering student, The Moringa school