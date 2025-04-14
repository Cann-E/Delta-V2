# Delta_Project


# Verisys Core

**Verisys** is a secure, role-based user management and document processing platform built with Django. It integrates Office365 authentication, supports custom user roles, and handles PDF generation with digital signatures for approval workflows. Designed for enterprise-grade user access control and document automation.

---

## 🚀 Features

### 🔐 Authentication & Access Control

- Office365 SSO login (via Microsoft OAuth)
- Role-Based Access Control (RBAC)
- Default role: `basicuser`
- Admin-controlled user CRUD
- User deactivation/reactivation

### 🧑‍💼 User Management

- Manage user attributes: name, email, role, status
- Admin-only access to user creation and role updates
- Deactivated users cannot access system resources

### 📄 Document Workflow (PDF)

- Users upload signatures (image files)
- PDFs generated at each step of approval
- Backend PDF generation with LaTeX and Makefile
- Auto-fill first name, last name (from session), and current date (from system)

---

## 🗂️ Folder Structure Overview

```
verisys-core/
├── delta/                    # Main Django app
│   ├── migrations/
│   ├── PDF/                  # LaTeX and document logic
│   ├── views.py              # Web views & endpoints
│   ├── models.py             # User, Role, and PDF models
│   ├── settings.py           # Project settings
│   ├── urls.py               # URL routing
│   └── ...
├── custom_auth/             # Office365 authentication logic
├── static/                  # Static files (CSS, JS, etc.)
├── templates/               # HTML templates
├── media/                   # Uploaded signatures
├── .env                     # Environment config
├── docker-compose.yaml      # Docker setup
├── Dockerfile               # App container config
├── backup.sql               # DB backup
├── manage.py                # Django CLI entry
├── requirements.txt         # Python dependencies
└── README.md
```

---

## 🧪 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/verisys-core.git
cd verisys-core
```

### 2. Setup Environment Variables

Create a `.env` file with:

```
SECRET_KEY=your_django_secret
DEBUG=True
DATABASE_URL=postgres://username:password@localhost:5432/verisys
OFFICE365_CLIENT_ID=your_client_id
OFFICE365_CLIENT_SECRET=your_client_secret
REDIRECT_URI=http://localhost:8000/auth/redirect
```

### 3. Run with Docker

```bash
docker-compose up --build
```

### 4. Access the Web App

```bash
http://localhost:8000
```

---

## 📸 Key Screens

- User Dashboard
- Role & Permissions Manager
- Signature Upload UI
- PDF Approval Workflow
- Admin User Table

---

## 🧑‍💻 Tech Stack

- Python 3.x / Django
- PostgreSQL
- Office365 OAuth
- Docker / Docker Compose
- LaTeX + Makefile
- HTML/CSS templates

---

## 🙏 Acknowledgements

- [Django](https://www.djangoproject.com/)
- [Microsoft Identity Platform](https://learn.microsoft.com/en-us/azure/active-directory/develop/)
- [LaTeX Project](https://www.latex-project.org/)

---

## 📬 Contact

For setup help or questions, please reach out to the development team or open an issue in the repository.

---

© Team Cann-E — 2025

