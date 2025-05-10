# 🛠️ Django Project Setup

Follow the steps below to set up and run your Django project.

---

## 1. Run Migrations

Apply initial migrations to set up your database schema:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser


Create the missing static directory to resolve it:
mkdir static

Run the following command to collect all static files into the STATIC_ROOT directory:
python manage.py collectstatic