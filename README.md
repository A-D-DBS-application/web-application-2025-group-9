[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/DxqGQVx4)

## Prerequisites

Before beginning, make sure you have installed the following:

- **Python 3.8+** ([Download](https://www.python.org/downloads/))
- **PostgreSQL 12+** ([Download](https://www.postgresql.org/download/))
- **Git** ([Download](https://git-scm.com/downloads))
- Een **Bizzy API key** (voor bedrijfsgegevens)
- Een **Supabase account** (of lokale PostgreSQL database)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/web-application-2025-group-9.git
cd web-application-2025-group-9
```

### 2. Create a virtual environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup

#### Option A: Import Database Backup (recommended for testing)

**Windows (PowerShell):**
```powershell
& 'C:\Program Files\PostgreSQL\18\bin\psql.exe' -U postgres -d your_database -f database/database-backup.sql
```

**macOS/Linux:**
```bash
psql -U postgres -d your_database -f database/database-backup.sql
```

*Change `your_database` with the name of your database.*

#### Optie B: Run Migrations for Fresh Database

```bash
flask db upgrade
```

### 5. Environment Variables

Make an `.env` bestand in the root directory:

```env
SECRET_KEY=your_secret_key_here
DATABASE_URL=postgresql+psycopg2://username:password@host:port/database
BIZZY_API_KEY=your_bizzy_api_key_here
FLASK_ENV=development
```

**For Supabase:**
```env
DATABASE_URL=postgresql+psycopg2://postgres.[PROJECT_ID]:[PASSWORD]@aws-[REGION].pooler.supabase.com:6543/postgres?sslmode=require
```

### 6. Run the application

**Development server:**
```bash
python run.py
```

**Or via Flask CLI:**
```bash
flask run
```

## Database Schema

The project uses PostgreSQL with the following tables:
- **users** - user profiles with optional roles
- **companies** - Company info and general metrics
- **debtor_batches** - Groups of debtors
- **cases** - Individual files linked to companies and users

See `database/ERD_Group9.png` and `database/DDL_Group9.sql` for the complete Entity Relationship Diagram and DDL.

## Tech Stack

- **Backend:** Flask 3.1.2
- **Database:** PostgreSQL + SQLAlchemy 2.0.44
- **Migrations:** Alembic (Flask-Migrate)
- **API Integration:** Bizzy API for up-to-date company info
- **PDF Generation:** xhtml2pdf
- **Frontend:** Bootstrap 5 + vanilla JavaScript

## Deployment

The application is configured for Render.com:
- `Procfile` - Gunicorn configuratie
- `render.yaml` - Render deployment configuratie

Link to Render: https://web-application-2025-group-9.onrender.com/
## Feedback Sessies

You can find our feedback sessions with our external partner here:
- [Feedback Sessie 1 - WhatsApp Audio Recording](https://drive.google.com/file/d/1--3B42kcW603DZGRa1rAkQcun9GAE7mX/view?usp=sharing) - Recording van irl meeting
- [Feedback Sessie 2 - Google Meet](https://drive.google.com/file/d/1n-67_Gqf03S4-FZ_4C8yfMLHc437P-iR/view?pli=1) - Bespreking via Google Meet

You can find our UI Prototype screenshots in the file with the same name: `UI prototype screenshots` and our Figma website here:
https://www.figma.com/make/oSz1PQA7rTZVGaD2A0opX8/Bailiff-Management-Website?p=f&t=NF5kowFDnnZYOwzc-0

You can find our presentation slides with the demo at slide 9 in `presentation`