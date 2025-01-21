
# DreamHost Python Deployment Instructions

## 1. Overview
This guide provides detailed steps to deploy a Python project on DreamHost, ensuring compatibility with features and requirements from the README, including database setup, advanced dependency management, and troubleshooting.

---

## 2. Prerequisites

### Local Development
- A Python project with:
  - `requirements.txt` or `pyproject.toml` for dependencies.
  - An application entry point (e.g., `main.py` or `app.py`).
  - A `schema.sql` file for database schema.

### DreamHost Setup
- DreamHost hosting plan with Passenger enabled for your subdomain.
- SSH access for deploying and managing the server.
- Access to the DreamHost database panel for managing PostgreSQL.

### Required Tools
- Python 3.11+ installed locally and on the server.
- Git for repository management.
- SFTP client for file transfers (if needed).

---

## 3. Pre-Deployment Setup

### Step 1: Enable SSH Access
1. Log in to the DreamHost control panel.
2. Go to **Manage Users** → **Add/Edit User**.
3. Enable **Shell (SSH)** access for your user account.

### Step 2: Connect to the Server
1. Open your terminal and connect via SSH:
   ```bash
   ssh username@yourdomain.com
   ```
2. Verify the Python version:
   ```bash
   python3 --version
   ```
3. (Optional) Install a custom Python version if required:
   ```bash
   curl -O https://www.python.org/ftp/python/3.x.x/Python-3.x.x.tar.xz
   tar -xvf Python-3.x.x.tar.xz
   cd Python-3.x.x
   ./configure
   make
   make install
   ```

### Step 3: Prepare Your Subdomain
1. In DreamHost’s panel, navigate to **Manage Domains**.
2. Add or edit your subdomain and enable **Passenger** for running Python applications.

---

## 4. Uploading Your Project

### Step 1: Clone Your Repository
1. SSH into your server and navigate to the subdomain directory:
   ```bash
   cd /home/username/yourdomain.com
   ```
2. Clone your project repository:
   ```bash
   git clone https://github.com/yourusername/yourproject.git .
   ```

### Step 2: Set Up a Virtual Environment
1. Create and activate the virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Upgrade `pip` and install dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

## 5. Configuring PostgreSQL

### Step 1: Create a Database
1. Log into the DreamHost panel and navigate to **MySQL Databases**.
2. Create a new database (PostgreSQL is managed under the same section).
3. Note down the credentials (hostname, username, password).

### Step 2: Initialize the Schema
1. Connect to the database using `psql`:
   ```bash
   psql -h hostname -U username -d database_name
   ```
2. Import the schema:
   ```bash
   psql -h hostname -U username -d database_name -f schema.sql
   ```

---

## 6. Configuring the Application

### Step 1: Create a `passenger_wsgi.py` File
1. Add this file to your project root:
   ```python
   import sys
   sys.path.insert(0, "/home/username/yourdomain.com")

   from main import app as application  # Update to match your app’s structure
   ```

### Step 2: Set Environment Variables
1. Create a `.env` file in your project root:
   ```properties
   DATABASE_URL=postgresql://username:password@hostname:5432/database_name
   SECRET_KEY=your_secret_key
   DEBUG=False
   ```
2. Use `python-dotenv` to load these variables in your app:
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

### Step 3: Adjust Permissions
1. Ensure files are readable by Passenger:
   ```bash
   chmod -R 755 /home/username/yourdomain.com
   ```

---

## 7. Testing and Troubleshooting

### Step 1: Restart Passenger
1. Restart Passenger to apply changes:
   ```bash
   touch tmp/restart.txt
   ```

### Step 2: Monitor Logs
1. Check Passenger logs for issues:
   ```bash
   tail -f logs/error.log
   ```

### Step 3: Debugging
1. If the app doesn’t load, verify:
   - Paths in `passenger_wsgi.py`.
   - Database credentials in `.env`.
   - Python dependencies are correctly installed.

---

## 8. Handling Advanced Requirements

### Using `pip-compile`
1. Install `pip-tools`:
   ```bash
   pip install pip-tools
   ```
2. Compile dependencies:
   ```bash
   pip-compile
   ```
3. Install the compiled requirements:
   ```bash
   pip install -r requirements.txt
   ```

### Using `Poetry`
1. Install Poetry:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```
2. Install dependencies:
   ```bash
   poetry install
   ```

---

## 9. Final Steps

### Automating Deployments
1. Automate updates with Git:
   ```bash
   git pull origin main
   touch tmp/restart.txt
   ```

### Static File Handling
1. Configure a static directory for your files and update your app to serve them.

---

These instructions should help you deploy your Python project on DreamHost successfully, ensuring alignment with all requirements from the README. If further clarification is needed, consult DreamHost's support or documentation.
