# Subscription Service API

A Flask-based REST API that allows managing vehicle subscriptions. The API provides functionality to create, retrieve, update, and delete subscriptions. It uses JWT-based authentication to secure the endpoints and offers a Swagger UI for documentation.

## Features

- Add a new subscription.
- Retrieve a list of subscriptions with optional filters.
- Update a subscription by its ID.
- Delete a subscription by its ID.
- List all available API endpoints with method details.

## Technologies Used

- **Flask**: Web framework for Python.
- **SQLite3**: Lightweight relational database for storing subscription data.
- **Flasgger**: Swagger integration for automatic API documentation.
- **Flask-JWT-Extended**: JWT-based authentication for securing API routes.
- **Python-dotenv**: To manage environment variables like database credentials and JWT secret keys.

## Installation

### Prerequisites

- Python 3.6+
- pip

### Steps

1. Clone the repository:
    ```bash
    git clone https://github.com/Fred062f/subscription-service.git
    cd subscription-service
    ```

2. Install required packages:
    ```bash
    pip install -r requirements.txt
    ```

3. Create a `.env` file to store environment variables. Sample `.env`:

    ```
    DATABASE=your_database_file.db
    SECRET_KEY=your_jwt_secret_key
    ```

4. Initialize the database:
    ```bash
    python db.py
    ```

5. Run the Flask app:
    ```bash
    python app.py
    ```

The application will run at `http://127.0.0.1:5000/`.

## Endpoints

### 1. Add a new subscription
- **URL**: `/subscriptions`
- **Method**: `POST`
- **Authentication**: JWT required
- **Body Parameters**:
  - `customer_id`: Integer
  - `start_date`: String (Date)
  - `end_date`: String (Date)
  - `rental_location`: String
  - `price_per_month`: Float
  - `agreed_km`: Integer
  - `actual_km`: Integer
  - `vehicle_id`: Integer
  - `down_payment`: Float

- **Response**:
  - `201`: Subscription successfully added.
  - `400`: Missing required fields.
  - `401`: Unauthorized. Invalid or missing JWT.

### 2. Get subscriptions
- **URL**: `/subscriptions`
- **Method**: `GET`
- **Authentication**: JWT required
- **Query Parameters** (optional):
  - `customer_id`: Filter by customer ID.
  - `vehicle_id`: Filter by vehicle ID.
  - `start_date`: Filter by subscription start date.
  - `end_date`: Filter by subscription end date.
  - `rental_location`: Filter by rental location.

- **Response**:
  - `200`: List of subscriptions.

### 3. Update a subscription
- **URL**: `/subscriptions/<subscription_id>`
- **Method**: `PUT`
- **Authentication**: JWT required
- **Body Parameters**:
  - `start_date`: String (Date)
  - `end_date`: String (Date)
  - `rental_location`: String
  - `price_per_month`: Float
  - `agreed_km`: Integer
  - `actual_km`: Integer
  - `vehicle_id`: Integer
  - `down_payment`: Float

- **Response**:
  - `200`: Subscription successfully updated.
  - `404`: Subscription not found.

### 4. Delete a subscription
- **URL**: `/subscriptions/<subscription_id>`
- **Method**: `DELETE`
- **Authentication**: JWT required

- **Response**:
  - `200`: Subscription successfully deleted.
  - `404`: Subscription not found.

### 5. List all API endpoints
- **URL**: `/endpoints`
- **Method**: `GET`
- **Response**: List of all available routes with their descriptions, methods, and JWT token requirements.

## Swagger UI

You can access the Swagger UI for interactive API documentation at:

```
http://127.0.0.1:5000/apidocs/
```

## Environment Variables

- `DATABASE`: Path to the SQLite database file.
- `SECRET_KEY`: JWT secret key used for token generation.
