# 🎂 DelightAPI - Cake Ordering Backend

DelightAPI is a robust and scalable RESTful backend service built with Django and Django REST Framework (DRF) for a modern cake ordering and delivery platform. It handles the full e-commerce lifecycle, from user registration and product Browse to order placement, delivery tracking, and administrative analytics.

-----

## 🚀 Key Features

This project includes a comprehensive set of features to power a full-stack application:

  * **Authentication & User Management**: Secure user registration, login (with token authentication), password management, and user profile updates.
  * **Store & Cake Catalog**: Manage a catalog of cakes linked to multiple stores. Stores can be filtered and sorted by distance from a user's location using the Haversine formula.
  * **Cart & Checkout**: A complete cart management system for adding, updating, and removing items before placing an order.
  * **Order Processing**: A full order lifecycle with status tracking, history, and alerts.
  * **Delivery Management**: APIs for managing delivery agents, assigning them to orders, and updating their live location.
  * **Address Management**: Users can save and manage multiple addresses for flexible delivery options.
  * **Admin Analytics**: Provides admin-only endpoints to track total sales and top-selling cakes.
  * **API Documentation**: Auto-generated interactive API documentation via Swagger and ReDoc.

-----

## 🔧 Setup Instructions

### 1\. Clone the repository

```bash
git clone https://github.com/Sathvika1209/delightapi.git
cd delightapi
```

### 2\. Create Virtual Environment

```bash
python -m venv venv
# On Windows
venv\Scripts\activate 
# On Linux/macOS
source venv/bin/activate 
```

### 3\. Install Dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` is not available, install manually:

```bash
pip install django djangorestframework drf-yasg djangorestframework-simplejwt daphne channels
```

### 4\. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5\. Create Superuser (Admin)

```bash
python manage.py createsuperuser
```

### 6\. Run the Server

```bash
# This uses Daphne for WebSocket support
daphne delightapi.asgi:application
```

### 7\. Access the API Admin

Navigate to `http://127.0.0.1:8000/admin/` to manage users, cakes, stores, and more.

## 📘 API Documentation

The backend provides full, interactive API documentation.

### 🔗 Swagger UI

  - **URL**: [http://127.0.0.1:8000/swagger/](http://127.0.0.1:8000/swagger/)
  - **Features**: Live testing of all endpoints, schema validation, and detailed descriptions.

### 📕 ReDoc

  - **URL**: [http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/)
  - **Features**: A clean, structured, and read-only view of the API documentation.

-----

## ✅ Core API Endpoints

A summary of the most important endpoints is provided below. All endpoints are accessible under the `/api/` prefix.

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| **POST** | `/api/auth/register/` | Register a new user with address & profile | ❌ No |
| **POST** | `/api/auth/login/` | Login and get an auth token | ❌ No |
| **POST** | `/api/auth/logout/` | Logout the user | ✅ Yes |
| **GET** | `/api/auth/profile/` | Get/update user profile (phone, gender) | ✅ Yes |
| **PUT** | `/api/auth/change-password/` | Change authenticated user's password | ✅ Yes |
| **DELETE** | `/api/auth/delete-account/` | Permanently delete the user's account | ✅ Yes |
| **GET, POST** | `/api/addresses/` | List all addresses or add a new one | ✅ Yes |
| **GET, PUT, DELETE** | `/api/addresses/{id}/` | Retrieve, update or delete an address | ✅ Yes |
| **GET** | `/api/stores/` | List all stores (can filter by `?lat=&lon=`) | ❌ No |
| **GET** | `/api/stores/{id}/cakes/` | List all cakes available at a specific store | ❌ No |
| **GET, POST** | `/api/cakes/` | List all cakes or add a new one (admin) | ❌ No / ✅ Yes |
| **GET, PUT, DELETE** | `/api/cakes/{id}/` | Retrieve, update or delete a specific cake | ❌ No / ✅ Yes |
| **GET, POST** | `/api/cart/` | List all cart items or add a new item | ✅ Yes |
| **PUT, DELETE** | `/api/cart/{id}/` | Update or remove a cart item | ✅ Yes |
| **POST** | `/api/orders/` | Place a new order from the cart | ✅ Yes |
| **GET** | `/api/orders/{id}/tracking/` | Get an order's status, ETA, and agent details | ✅ Yes |
| **GET** | `/api/orders/{id}/alerts/` | Get alerts for a specific order | ✅ Yes |
| **GET** | `/api/agents/available/` | Get a list of all available delivery agents | ✅ Yes |
| **POST** | `/api/agents/{agent_id}/location-update/` | Update a delivery agent's location | ✅ Admin |

-----

## 💡 Future Scope

  * **WebSocket Live Tracking**: Implement the front-end logic to consume real-time location updates for delivery agents.
  * **Payment Gateway**: Integrate a payment service like Razorpay or Stripe to handle transactions securely.
  * **Admin Dashboard**: Create a dedicated Streamlit/React/Vue frontend for admins with analytics, order management, and agent assignment features.

-----