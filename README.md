# Document Management System

A lightweight, Django-based document management system with project organization, role-based permissions, versioning, and audit logging.

---

## 🚀 Setup Instructions

### 1. Clone the Repo

```bash
git clone git@github.com:rorymulcahey/Document-Management-System.git
cd Document-Management-System
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv document_mgmt_venv
source document_mgmt_venv/bin/activate  # or Scripts\activate on Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables

Create a `.env` file in the root with the following:

```ini
DJANGO_SECRET_KEY=your-secure-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

> These are loaded using [`python-decouple`](https://pypi.org/project/python-decouple/)

### 5. Migrate & Seed Data

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py populate_dummy_data
```

---

## ⚙️ Developer Notes

- Uses `django-guardian` for per-object access control
- SharePoint CSV imports via `documents/importers/sharepoint_import.py`

---

## 📝 License

MIT License

---

## 💡 Future Enhancements

- Celery-based background processing
- Azure Blob Storage integration
- PDF preview and annotation
- Microsoft Graph live editing
- Full SharePoint import/export pipeline

---

## 🔗 Project URL

[github.com/rorymulcahey/Document-Management-System](https://github.com/rorymulcahey/Document-Management-System)
