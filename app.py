from flask import Flask, request, jsonify
import sqlite3
from flasgger import Swagger
import os
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from db import init_db
import inspect

load_dotenv()

app = Flask(__name__)

DATABASE = os.getenv("DATABASE")
SECRET_KEY = os.getenv('SECRET_KEY')

app.config['JWT_SECRET_KEY'] = SECRET_KEY
jwt = JWTManager(app)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/",
    "securityDefinitions": {
        "BearerAuth": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Enter your JWT token in the format **Bearer &lt;token&gt;**.",
        }
    },
    "security": [{"BearerAuth": []}],
}
swagger = Swagger(app, config=swagger_config)

init_db()

@app.route('/add', methods=['POST'])
@jwt_required()
def add_subscription():
    """
    Add a new subscription.
    ---
    tags:
      - Subscriptions
    security:
      - BearerAuth: []  # Require Authorization header
    parameters:
      - name: body
        in: body
        required: true
        description: Subscription details
        schema:
          type: object
          properties:
            customer_id:
              type: integer
              description: ID of the customer
            start_date:
              type: string
              format: date
              description: Start date of the subscription
            end_date:
              type: string
              format: date
              description: End date of the subscription
            rental_location:
              type: string
              description: Rental location of the subscription
            price_per_month:
              type: number
              description: Monthly subscription price
            agreed_km:
              type: integer
              description: Agreed kilometers for the subscription
            actual_km:
              type: integer
              description: Actual kilometers driven
            vehicle_id:
              type: integer
              description: ID of the vehicle
            down_payment:
              type: number
              description: Down payment for the subscription
    responses:
      201:
        description: Subscription successfully added.
      400:
        description: Missing required fields.
      401:
        description: Unauthorized. Missing or invalid token.
    """
    data = request.get_json()
    required_fields = ["start_date", "end_date", "rental_location", "price_per_month", "agreed_km", "actual_km", "vehicle_id", "down_payment"]

    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    conn = sqlite3.connect(DATABASE)
    cursor = conn.execute("""
        INSERT INTO subscriptions (customer_id, start_date, end_date, rental_location, price_per_month, agreed_km, actual_km, vehicle_id, down_payment)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (data.get("customer_id"), data["start_date"], data["end_date"], data["rental_location"],
          data["price_per_month"], data["agreed_km"], data["actual_km"], data["vehicle_id"], data["down_payment"]))
    conn.commit()
    subscription_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": subscription_id, "message": "Subscription added successfully"}), 201

@app.route('/list', methods=['GET'])
@jwt_required()
def get_subscriptions():
    """
    Retrieve subscription details with optional filters.
    ---
    tags:
      - Subscriptions
    security:
      - BearerAuth: []
    parameters:
      - name: customer_id
        in: query
        type: integer
        required: false
        description: Filter by customer ID.
      - name: vehicle_id
        in: query
        type: integer
        required: false
        description: Filter by vehicle ID.
      - name: start_date
        in: query
        type: string
        format: date
        required: false
        description: Filter by subscriptions starting on or after this date.
      - name: end_date
        in: query
        type: string
        format: date
        required: false
        description: Filter by subscriptions ending on or before this date.
      - name: rental_location
        in: query
        type: string
        required: false
        description: Filter by subscription location.
    responses:
      200:
        description: List of subscriptions.
      401:
        description: Unauthorized. Missing or invalid token.
    """
    filters = []
    query = "SELECT * FROM subscriptions WHERE 1=1"

    # Filter by customer ID
    customer_id = request.args.get('customer_id')
    if customer_id:
        query += " AND customer_id = ?"
        filters.append(customer_id)

    # Filter by vehicle ID
    vehicle_id = request.args.get('vehicle_id')
    if vehicle_id:
        query += " AND vehicle_id = ?"
        filters.append(vehicle_id)

    # Filter by start date
    start_date = request.args.get('start_date')
    if start_date:
        query += " AND start_date >= ?"
        filters.append(start_date)

    # Filter by end date
    end_date = request.args.get('end_date')
    if end_date:
        query += " AND end_date <= ?"
        filters.append(end_date)

    # Filter by rental location
    rental_location = request.args.get('rental_location')
    if rental_location:
        query += " AND rental_location = ?"
        filters.append(rental_location)

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.execute(query, filters)
    rows = cursor.fetchall()
    conn.close()

    subscriptions = [dict(row) for row in rows]

    if not subscriptions:
        return jsonify([]), 200

    return jsonify(subscriptions), 200


@app.route('/update/<int:subscription_id>', methods=['PUT'])
@jwt_required()
def update_subscription(subscription_id):
    """
    Update a subscription by ID.
    ---
    tags:
      - Subscriptions
    security:
      - BearerAuth: []  # Require Authorization header
    parameters:
      - name: subscription_id
        in: path
        type: integer
        required: true
        description: ID of the subscription to update.
      - name: body
        in: body
        required: true
        description: Updated subscription details.
        schema:
          type: object
          properties:
            start_date:
              type: string
              format: date
            end_date:
              type: string
              format: date
            rental_location:
              type: string
            price_per_month:
              type: number
            agreed_km:
              type: integer
            actual_km:
              type: integer
            vehicle_id:
              type: integer
            down_payment:
              type: number
    responses:
      200:
        description: Subscription successfully updated.
      404:
        description: Subscription not found.
    """
    data = request.get_json()
    updates = []
    params = []

    for key in ["start_date", "end_date", "rental_location", "price_per_month", "agreed_km", "actual_km", "vehicle_id", "down_payment"]:
        if key in data:
            updates.append(f"{key} = ?")
            params.append(data[key])

    if not updates:
        return jsonify({"error": "No fields to update"}), 400

    query = f"UPDATE subscriptions SET {', '.join(updates)} WHERE subscription_id = ?"
    params.append(subscription_id)

    conn = sqlite3.connect(DATABASE)
    cursor = conn.execute(query, params)
    conn.commit()
    row_count = cursor.rowcount
    conn.close()

    if row_count == 0:
        return jsonify({"error": "Subscription not found"}), 404

    return jsonify({"message": "Subscription updated successfully"}), 200

@app.route('/remove/<int:subscription_id>', methods=['DELETE'])
@jwt_required()
def delete_subscription(subscription_id):
    """
    Delete a subscription by ID.
    ---
    tags:
      - Subscriptions
    security:
      - BearerAuth: []  # Require Authorization header
    parameters:
      - name: subscription_id
        in: path
        type: integer
        required: true
        description: ID of the subscription to delete.
    responses:
      200:
        description: Subscription successfully deleted.
      404:
        description: Subscription not found.
    """
    conn = sqlite3.connect(DATABASE)
    cursor = conn.execute("DELETE FROM subscriptions WHERE subscription_id = ?", (subscription_id,))
    conn.commit()
    row_count = cursor.rowcount
    conn.close()

    if row_count == 0:
        return jsonify({"error": "Subscription not found"}), 404

    return jsonify({"message": "Subscription deleted successfully"}), 200


@app.route('/', methods=['GET'])
def endpoints():
    """
    List all available endpoints in the API, including their descriptions, methods, and JWT token requirements.
    --- 
    tags:
      - Utility
    responses:
      200:
        description: A list of all available routes with their descriptions, methods, and JWT token requirements.
    """
    excluded_endpoints = {'static', 'flasgger.static', 'flasgger.oauth_redirect', 'flasgger.<lambda>', 'flasgger.apispec'}
    excluded_methods = {'HEAD', 'OPTIONS'}
    routes = []

    for rule in app.url_map.iter_rules():
        if rule.endpoint not in excluded_endpoints:
            func = app.view_functions.get(rule.endpoint)
            if not func:
                continue

            # Get the docstring
            full_docstring = inspect.getdoc(func)
            docstring = full_docstring.split('---')[0].replace("\n", " ").strip() if full_docstring else None

            # Check if the @jwt_required() decorator is applied
            jwt_required = "@jwt_required" in inspect.getsource(func).split('\n')[1]

            # Exclude methods
            methods = list(rule.methods - excluded_methods)

            routes.append({
                'endpoint': rule.rule,
                'methods': methods,
                'description': docstring,
                'jwt_required': jwt_required
            })
    return jsonify({'endpoints': routes}), 200


if __name__ == "__main__":
    app.run(debug=True)
