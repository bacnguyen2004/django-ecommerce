# Bookstore Django REST API

Bookstore is a Django e-commerce project for selling books and general store products. The project includes a customer storefront, a custom admin panel, JWT-protected REST APIs, order management, COD/VNPAY checkout flow, wishlist, and Swagger API documentation.

## Live Demo

- Local app: `http://127.0.0.1:8000/`
- Swagger docs: `http://127.0.0.1:8000/api/docs/`
- Production demo: add your deployed URL here after deployment.

## Screenshots

| Storefront preview | Home banner |
| --- | --- |
| ![Storefront preview](store/static/store/images/bookstore-hero.png) | ![Home banner](store/static/store/images/home1.jpg) |

## Tech Stack

- Python 3.11
- Django 5.2
- Django REST Framework
- Simple JWT
- drf-spectacular / Swagger UI
- PostgreSQL for local, Docker, and production databases
- Cloudinary storage for media
- WhiteNoise for static files
- Gunicorn for production runtime

## Main Features

- Register, login, JWT refresh, and profile API.
- Product and category APIs with search and price filters.
- Create order API with stock validation and stock deduction.
- My orders and order detail APIs for authenticated customers.
- Cancel pending order API with stock restoration.
- Admin-only APIs for listing and viewing all completed orders.
- Storefront pages for home, products, cart, checkout, wishlist, profile, and order history.
- Admin panel for dashboard, categories, products, customers, and orders.

## API Documentation

Swagger UI is available at:

```txt
GET /api/docs/
```

OpenAPI schema is available at:

```txt
GET /api/schema/
```

Protected endpoints require this header:

```http
Authorization: Bearer <access_token>
```

## API Endpoints

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| GET | `/api/products/` | Public | List products with pagination |
| GET | `/api/products/?search=django&min_price=100000&max_price=300000` | Public | Search/filter products |
| GET | `/api/products/<id>/` | Public | Product detail |
| GET | `/api/categories/` | Public | List categories |
| POST | `/api/auth/register/` | Public | Register customer account |
| POST | `/api/auth/login/` | Public | Get JWT access and refresh tokens |
| POST | `/api/auth/refresh/` | Public | Refresh access token |
| GET | `/api/auth/profile/` | JWT | Current user profile |
| POST | `/api/orders/` | JWT | Create order |
| GET | `/api/my-orders/` | JWT | Current user's orders |
| GET | `/api/my-orders/<id>/` | JWT | Current user's order detail |
| POST | `/api/my-orders/<id>/cancel/` | JWT | Cancel current user's pending order |
| GET | `/api/orders/` | Admin JWT | List all completed orders |
| GET | `/api/orders/<id>/` | Admin JWT | View any completed order |

## Permissions

- Public users can view products and categories.
- Authenticated users can view their profile, create orders, view their own orders, and cancel only their own pending orders.
- Users cannot view another customer's order detail through `/api/my-orders/<id>/`.
- Admin users can view every completed order through `/api/orders/`.

Admin access is granted when a user is `is_staff`, `is_superuser`, or has a related `Customer.role = "admin"`.

## Postman Collection

The Postman collection is included at:

```txt
postman/bookstore-api.postman_collection.json
```

Import it into Postman, set `base_url` to your local or deployed URL, then run `Auth / Login`. The login request saves `access_token` and `refresh_token` into collection variables.

## Local Setup

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
docker compose up -d db
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open:

```txt
http://127.0.0.1:8000/
```

## Environment Variables

Copy `.env.example` to `.env` and update values as needed:

```env
SECRET_KEY=django-insecure-change-me
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=
POSTGRES_DB=bookstore
POSTGRES_USER=bookstore
POSTGRES_PASSWORD=bookstore
DATABASE_URL=postgres://bookstore:bookstore@localhost:5433/bookstore
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
VNPAY_TMN_CODE=
VNPAY_HASH_SECRET_KEY=
VNPAY_PAYMENT_URL=
VNPAY_RETURN_URL=http://127.0.0.1:8000/vnpay/return/
```

`DATABASE_URL` is required. For local development with the PostgreSQL container, use:

```env
DATABASE_URL=postgres://bookstore:bookstore@localhost:5433/bookstore
```

When Django runs inside Docker Compose, the service uses:

```env
DATABASE_URL=postgres://bookstore:bookstore@db:5432/bookstore
```

## Run Tests

```powershell
python manage.py check
python manage.py test
```

## Docker With PostgreSQL

Copy the Docker env file:

```powershell
copy .env.docker.example .env.docker
```

Build and start Django with PostgreSQL:

```powershell
docker compose up --build
```

The `web` service waits for PostgreSQL, runs migrations, then starts Gunicorn on port `8000`.
The `db` service exposes PostgreSQL on local port `5433`, so `python manage.py runserver` can use the same database through `localhost`.

Open:

```txt
http://127.0.0.1:8000/
http://127.0.0.1:8000/api/docs/
```

Create a superuser:

```powershell
docker compose exec web python manage.py createsuperuser
```

Stop containers:

```powershell
docker compose down
```

Reset PostgreSQL data:

```powershell
docker compose down -v
```

## Render Deployment

The repository includes `render.yaml` for a Python web service and Render PostgreSQL database.

Render runs:

```txt
Build Command: bash build.sh
Pre-Deploy Command: python manage.py migrate --noinput
Start Command: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

Set these secret values in Render:

```txt
SECRET_KEY
CLOUDINARY_CLOUD_NAME
CLOUDINARY_API_KEY
CLOUDINARY_API_SECRET
VNPAY_TMN_CODE
VNPAY_HASH_SECRET_KEY
VNPAY_PAYMENT_URL
VNPAY_RETURN_URL
```

`DATABASE_URL` is provided automatically by the Render PostgreSQL database in `render.yaml`.

## Project Structure

```txt
config/                         # Django settings, urls, asgi, wsgi
store/                          # Main bookstore app
store/api/                      # DRF serializers, views, urls
store/models/                   # Domain models split by module
store/services/api/             # API business logic
store/services/storefront/      # Storefront business logic
store/services/admin_panel/     # Admin panel business logic
store/templates/store/          # Storefront and admin templates
store/static/store/             # Static assets
postman/                        # Postman API collection
```

The Django app package is `store`. The app label remains `app` in `store/apps.py` to keep existing database table names and migrations compatible.

## Deployment Notes

- Do not commit `.env`, `db.sqlite3`, `media/`, or `staticfiles/`.
- Use `DEBUG=False` in production.
- Configure `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` for your domain.
- Run `python manage.py collectstatic --noinput` before production deployment.
