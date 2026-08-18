"""
inventory-service
Tracks stock levels for items and handles reservation requests
from order-service. In-memory store for simplicity — the point
of this project is the platform around it, not the app logic.
"""
from flask import Flask, jsonify, request
import os
import threading

app = Flask(__name__)
lock = threading.Lock()

# Seed inventory: item_id -> quantity available
INVENTORY = {
    "sku-001": 50,
    "sku-002": 30,
    "sku-003": 0,   # intentionally out of stock, useful for testing failure paths
    "sku-004": 100,
}


@app.route("/health", methods=["GET"])
def health():
    return jsonify(status="ok", service="inventory-service"), 200


@app.route("/inventory/<item_id>", methods=["GET"])
def get_stock(item_id):
    with lock:
        qty = INVENTORY.get(item_id)
    if qty is None:
        return jsonify(error="item not found", item_id=item_id), 404
    return jsonify(item_id=item_id, quantity=qty), 200


@app.route("/inventory/<item_id>/reserve", methods=["POST"])
def reserve_stock(item_id):
    body = request.get_json(silent=True) or {}
    qty_requested = body.get("quantity", 1)

    if not isinstance(qty_requested, int) or qty_requested <= 0:
        return jsonify(error="quantity must be a positive integer"), 400

    with lock:
        available = INVENTORY.get(item_id)
        if available is None:
            return jsonify(error="item not found", item_id=item_id), 404
        if available < qty_requested:
            return jsonify(
                error="insufficient stock",
                item_id=item_id,
                available=available,
                requested=qty_requested,
            ), 409
        INVENTORY[item_id] -= qty_requested
        remaining = INVENTORY[item_id]

    return jsonify(
        item_id=item_id,
        reserved=qty_requested,
        remaining=remaining,
    ), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
