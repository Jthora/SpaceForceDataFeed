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
   git clone https://github.com/Jthora/SpaceForceDataFeed.git
   ```

### Step 2: Set Up a Virtual Environment
1. Create and activate the virtual environment:
   *navigate to opt/ folder*
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Upgrade `pip` and install dependencies:
   *navigate to the git repo directory*
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
      ```bash
      echo 'export PATH=$HOME/opt/postgresql/bin:$PATH' >> ~/.bash_profile
      source ~/.bash_profile
      ```
   2. Verify the PostgreSQL version:
      ```bash
      psql --version
      ```
   3. If `psql` is not found, ensure the PostgreSQL binaries are in your `PATH`:
      ```bash
      export PATH=$HOME/opt/postgresql/bin:$PATH
      ```

5. Initialize the Database
   1. Create a data directory for PostgreSQL:
      ```bash
      mkdir -p $HOME/opt/postgresql/data
      ```
   2. Initialize the database cluster:
      ```bash
      initdb -D $HOME/opt/postgresql/data
      ```

6. Start the PostgreSQL Server
   1. Ensure the PostgreSQL binaries are in your `PATH`:
      ```bash
      export PATH=$HOME/opt/postgresql/bin:$PATH
      ```
   2. Check if the server is already running:
      ```bash
      pg_ctl status -D $HOME/opt/postgresql/data || pg_ctl -D $HOME/opt/postgresql/data -l $HOME/opt/postgresql/logfile start
      ```
   3. Verify the server is running:
      ```bash
      pg_ctl status -D $HOME/opt/postgresql/data
      ```
   4. Ensure the server is accepting connections:
      ```bash
      psql -d postgres -c "SELECT 1;" || (export PATH=$HOME/opt/postgresql/bin:$PATH && pg_ctl -D $HOME/opt/postgresql/data -l $HOME/opt/postgresql/logfile start)
      ```
   5. If the server fails to start, examine the log output:
      ```bash
      cat $HOME/opt/postgresql/logfile
      ```

7. Create and Use a Database
   1. Create a new PostgreSQL user:
      ```bash
      createuser jono
      ```
   2. Set the password for the new user:
      ```bash
      psql -d postgres -c "ALTER USER jono WITH PASSWORD 'your_password01a';"
      ```
   3. Create a new database:
      ```bash
      createdb spaceforce_datafeed
      ```
   4. Grant all privileges on the database to the new user:
      ```bash
      psql -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE spaceforce_datafeed TO jono;"
      ```
   5. Connect to the database:
      ```bash
      psql -d spaceforce_datafeed
      ```

      use \q to exit out of the database
      ```bash
      \q
      ```
   6. To execute your schema (from within the spaceforcedatafeed directory):
      ```bash
      psql -d spaceforce_datafeed -f schema.sql
      ```


   2. To stop the server:
      ```bash
      pg_ctl -D $HOME/opt/postgresql/data stop
      ```
   3. To restart the server:
      ```bash
      pg_ctl -D $HOME/opt/postgresql/data restart
      ```
   4. To check the status of the server:
      ```bash
      pg_ctl status -D $HOME/opt/postgresql/data
      ```
   5. To view the server logs:
      ```bash
      cat $HOME/opt/postgresql/logfile
      ```

---

### 6. Setup the .env file

```bash
echo "DATABASE_URL=postgresql://jono:your_password01a@localhost:5432/spaceforce_datafeed" > .env
echo "PGUSER=jono" >> .env
echo "PGPASSWORD=your_password01a" >> .env
echo "PGHOST=localhost" >> .env
echo "PGPORT=5432" >> .env
echo "PGDATABASE=spaceforce_datafeed" >> .env
```
