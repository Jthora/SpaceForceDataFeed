# DreamHost Python Deployment Instructions

## 1. Overview
This guide provides detailed steps to deploy a Python project on DreamHost, ensuring compatibility with features and requirements from the README, including database setup, advanced dependency management, and troubleshooting.

---

## 2. Prerequisites

### Local Development
- A Python project with:
  - `pyproject.toml` and `uv.lock` for dependencies.
  - An application entry point (e.g., `main.py` or `app.py`).
  - A `schema.sql` file for database schema.
  - A `.env` file for environment variables.

### DreamHost Setup
- DreamHost hosting plan with Passenger enabled for your subdomain.
- SSH access for deploying and managing the server.
- Access to the DreamHost database panel for managing PostgreSQL.

### Required Tools
- Python 3.13.1 installed locally and on the server.
- Git for repository management.
- SFTP client for file transfers (if needed).

---

## 3. Pre-Deployment Setup

### Step 1: Enable SSH Access
1. Log in to the DreamHost control panel.
2. Go to **Manage Users** → **Add/Edit User**.
3. Enable **Shell (SSH)** access for your user account.

    **Advanced:**

    ```bash
    ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
    ssh-copy-id username@yourdomain.com
    ```

    **Newbie:**
    If you're not familiar with SSH keys, you can simply enable SSH access and then use your password to connect via the terminal.

### Step 2: Connect to the Server
1. Open your terminal and connect via SSH:
   ```bash
   ssh username@yourdomain.com
   ```

2. Verify the Python version:
   ```bash
   python3 --version
   ```

3. Install a custom Python version (likely required):
   ```bash
   mkdir ~/tmp
   cd ~/tmp
   curl -O https://www.python.org/ftp/python/3.13.1/Python-3.13.1.tar.xz
   tar -xvf Python-3.13.1.tar.xz
   cd Python-3.13.1
   ./configure --prefix=$HOME/opt/python-3.13.1 --with-ensurepip=install
   make
   make install
   ```

4. Add the new Python installation to your `PATH`:
   ```bash
   echo 'export PATH=$HOME/opt/python-3.13.1/bin:$PATH' >> ~/.bash_profile
   source ~/.bash_profile
   ```

5. Verify the Python version:
   ```bash
   python3 --version
   ```

6. Upgrade `pip`:
   ```bash
   pip3 install --upgrade pip
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
   pip install pip-tools
   pip-compile pyproject.toml
   pip install -r requirements.txt
   ```

---

## 5. Configuring PostgreSQL

### Step 1: Create a Database
1. Download PostgreSQL Source Code
   1. Log in to your DreamHost server via SSH.
   2. Create a temporary directory and navigate to it:
      ```bash
      mkdir ~/tmp
      cd ~/tmp
      ```
   3. Download the PostgreSQL 14.15 source code:
      ```bash
      wget https://ftp.postgresql.org/pub/source/v14.15/postgresql-14.15.tar.gz
      ```
   4. Extract the downloaded file:
      ```bash
      tar zxvf postgresql-14.15.tar.gz
      cd postgresql-14.15
      ```
2. Configure the Build
   1. Configure the build to install PostgreSQL in your home directory:
      ```bash
      ./configure --prefix=$HOME/opt/postgresql
      ```
3. Compile and Install
   1. Compile the source code:
      ```bash
      make
      ```
   2. Install PostgreSQL to the specified directory:
      ```bash
      make install
      ```
4. Add PostgreSQL to Your PATH
   1. Add the PostgreSQL binaries to your PATH:
   2. ```bash
      echo 'export PATH=$HOME/opt/postgresql/bin:$PATH' >> ~/.bash_profile
      source ~/.bash_profile
      ```
   3. Verify the PostgreSQL version:
   4. ```bash
      psql --version
      ```
5. Initialize the Database
   1. Create a data directory for PostgreSQL:
   2. ```bash
      mkdir -p $HOME/opt/postgresql/data
      ```
   3. Initialize the database cluster:
      ```bash
      initdb -D $HOME/opt/postgresql/data
      ```
6. Start the PostgreSQL Server
   1. Start the server:
      ```bash
      pg_ctl -D $HOME/opt/postgresql/data -l $HOME/opt/postgresql/logfile start
      ```
   2. Verify the server is running:
      ```bash
      pg_ctl status -D $HOME/opt/postgresql/data
      ```
7. Create and Use a Database
   1. Create a new database:
      ```bash
      createdb spaceforce_datafeed
      ```
   2. Connect to the database:
      ```bash
      psql -d spaceforce_datafeed
      ```
   3. To execute your schema:
      ```bash
      psql -d spaceforce_datafeed -f schema.sql
      ```
8. Stop the PostgreSQL Server
   1. To stop the server when you’re done:
      ```bash
      pg_ctl -D $HOME/opt/postgresql/data stop
      ```

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
   pip-compile pyproject.toml
   ```

3. Install the compiled requirements:
   ```bash
   pip install -r requirements.txt
   ```

### Using `Poetry`
1. Install Poetry:
   ```bash
   pip install poetry
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Activate the virtual environment:
   ```bash
   poetry shell
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
