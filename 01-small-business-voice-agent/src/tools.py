import json
from pathlib import Path

DATA_PATH=(
    Path(__file__).resolve().parent.parent / "data" / "products.json"
)

def check_product_stock(product_id:str) -> dict:
    with DATA_PATH.open(encoding="utf-8") as file:
        products=json.load(file)

    for product in products:
        if product["id"].lower()== product_id.strip().lower():
            return {
                "found":True,
                "id":product["id"],
                "name":product["name"],
                "in_stock":product["in_stock"],
                "price_inr":product["price_inr"],
            }


    return {
        "found":False,
        "product_id":product_id,
        "message":"Product not found.",
    }
