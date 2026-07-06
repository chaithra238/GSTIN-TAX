# GSTIN-TAX

GSTIN-TAX is a full-stack GST search project with a React/Vite frontend and a Django backend API.

## Features

- React frontend for searching GST details.
- Django REST backend for GST lookup endpoints.
- CORS configured for local frontend development.
- Environment-based backend settings for safer deployment.

## Tech Stack

- Frontend: React, TypeScript, Vite, Axios
- Backend: Django, Django REST Framework, django-cors-headers
- Database: SQLite for local development

## Project Structure

```text
GSTIN-TAX/
├── tax/                 # React/Vite frontend
├── tax-backend/         # Django backend
├── .gitignore
├── LICENSE
└── README.md
```

## Backend Setup

```bash
cd tax-backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Create `tax-backend/.env` for local development:

```env
DEBUG=True
SECRET_KEY=replace_with_your_secret_key
ALLOWED_HOSTS=127.0.0.1,localhost
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

## Frontend Setup

```bash
cd tax
npm install
npm run dev
```

## Deployment Notes

For production, set environment variables in the hosting platform instead of committing secrets:

```env
DEBUG=False
SECRET_KEY=your_production_secret_key
ALLOWED_HOSTS=your-backend-domain.com
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
```

## License

This project is licensed under the MIT License.
