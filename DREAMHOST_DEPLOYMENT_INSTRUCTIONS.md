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

    **Advanced:**

    ```bash
    ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
    ssh-copy-id username@yourdomain.com
    ```

    *Comment: Using SSH keys enhances security and avoids the need to enter a password each time you connect. Be careful to keep your private key secure.*

    **Newbie:**

    If you're not familiar with SSH keys, you can simply enable SSH access and use your password to connect.

    **Note:** SSH (Secure Shell) is a protocol for securely connecting to a remote server. Enabling SSH access allows you to manage your server from your local machine.

### Step 2: Connect to the Server
1. Open your terminal and connect via SSH:
   ```bash
   ssh username@yourdomain.com
   ```

    **Advanced:**

    ```bash
    ssh -i /path/to/your/private/key username@yourdomain.com
    ```

    *Comment: Specifying the private key file directly can be useful if you have multiple keys or need to use a specific one.*

    **Newbie:**

    If you're not using SSH keys, just use the first command and enter your password when prompted.

    **Note:** Connecting via SSH allows you to execute commands on your remote server as if you were sitting right in front of it.

2. Verify the Python version:
   ```bash
   python3 --version
   ```

    **Advanced:**

    ```bash
    python3 -m pip list
    ```

    *Comment: Listing installed packages helps ensure all required dependencies are available.*

    **Newbie:**

    Just run the first command to check if Python is installed and to see its version.

    **Note:** It's important to ensure that the correct version of Python is installed on your server to avoid compatibility issues.

   1. Install a custom Python version (likely required):
   ```bash
   mkdir ~/tmp
   cd ~/tmp
   curl -O https://www.python.org/ftp/python/3.13.1/Python-3.13.1.tar.xz
   tar -xvf Python-3.13.1.tar.xz
   cd Python-3.13.1
   ./configure --prefix=$HOME/opt/python-3.13.1
   make
   make install
   ```

   2. Add the new Python installation to your `PATH`:
   ```bash
   echo 'export PATH=$HOME/opt/python-3.13.1/bin:$PATH' >> ~/.bash_profile
   source ~/.bash_profile
   ```
   3. Verify the Python version:
      ```bash
      python3 --version
      ```
      This should output `Python 3.13.1`.

    **Advanced:**

    ```bash
    ./configure --enable-optimizations
    ```

    *Comment: Enabling optimizations can improve the performance of the Python interpreter. Be cautious as this increases the build time.*

    **Newbie:**

    If you're not comfortable compiling Python from source, you can skip this step and use the version provided by DreamHost.

    **Note:** Compiling Python from source allows you to customize the installation, but it's usually not necessary unless you need specific features.

### Step 3: Prepare Your Subdomain
1. In DreamHost’s panel, navigate to **Manage Domains**.
2. Add or edit your subdomain and enable **Passenger** for running Python applications.

    **Advanced:**

    ```bash
    mkdir -p /home/username/yourdomain.com/tmp
    ```

    *Comment: Creating a `tmp` directory ensures Passenger can restart your application properly.*

    **Newbie:**

    Just follow the steps in the DreamHost panel to enable Passenger for your subdomain.

    **Note:** Passenger is a web application server that allows you to run Python applications on your DreamHost subdomain.

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

    **Advanced:**

    ```bash
    git clone --depth=1 https://github.com/yourusername/yourproject.git .
    ```

    *Comment: Cloning with `--depth=1` reduces the size of the clone and speeds up the process. Be careful as this only includes the latest commit.*

    **Newbie:**

    Use the first command to clone your repository. Make sure you replace the URL with your actual repository URL.

    **Note:** Cloning your repository copies all your project files to the server, allowing you to run your application from there.

### Step 2: Set Up a Virtual Environment
1. Create and activate the virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

    **Advanced:**

    ```bash
    python3 -m venv --prompt YourProjectEnv venv
    source venv/bin/activate
    ```

    *Comment: Using `--prompt` sets a custom prompt name for the virtual environment, making it easier to identify.*

    **Newbie:**

    Just use the first command to create and activate the virtual environment.

    **Note:** A virtual environment isolates your project's dependencies, ensuring they don't conflict with other projects or system-wide packages.

2. Upgrade `pip` and install dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

    **Advanced:**

    ```bash
    pip install -r requirements.txt --no-cache-dir
    ```

    *Comment: Using `--no-cache-dir` ensures that pip does not use the cache, which can be useful for avoiding issues with outdated cached packages.*

    **Newbie:**

    Use the first command to upgrade `pip` and install your project's dependencies.

    **Note:** Upgrading `pip` ensures you have the latest version, and installing dependencies from `requirements.txt` sets up your project environment.

---

## 5. Configuring PostgreSQL

### Step 1: Create a Database
1. Log into the DreamHost panel and navigate to **MySQL Databases**.
2. Create a new database (PostgreSQL is managed under the same section).
3. Note down the credentials (hostname, username, password).

    **Advanced:**

    ```bash
    psql -h hostname -U username -c "CREATE DATABASE database_name;"
    ```

    *Comment: Creating the database via command line can be faster and allows for scripting. Be cautious with command syntax to avoid errors.*

    **Newbie:**

    Follow the steps in the DreamHost panel to create your database and note down the credentials.

    **Note:** A database is essential for storing and managing your application's data. PostgreSQL is a powerful, open-source database system.

### Step 2: Initialize the Schema
1. Connect to the database using `psql`:
   ```bash
   psql -h hostname -U username -d database_name
   ```
2. Import the schema:
   ```bash
   psql -h hostname -U username -d database_name -f schema.sql
   ```

    **Advanced:**

    ```bash
    psql -h hostname -U username -d database_name -f schema.sql --echo-all
    ```

    *Comment: Using `--echo-all` provides detailed output of the SQL commands being executed, which can help with debugging.*

    **Newbie:**

    Use the first command to connect to your database and the second command to import your schema.

    **Note:** Importing the schema sets up the database structure required by your application.

---

## 6. Configuring the Application

### Step 1: Create a `passenger_wsgi.py` File
1. Add this file to your project root:
   ```python
   import sys
   sys.path.insert(0, "/home/username/yourdomain.com")

   from main import app as application  # Update to match your app’s structure
   ```

    **Advanced:**

    ```python
    import os
    sys.path.insert(0, os.path.dirname(__file__))

    from main import app as application  # Update to match your app’s structure
    ```

    *Comment: Using `os.path.dirname(__file__)` makes the path insertion more dynamic and adaptable to different environments.*

    **Newbie:**

    Use the first code snippet and make sure to update the import statement to match your application's structure.

    **Note:** The `passenger_wsgi.py` file tells Passenger how to start your application.

### Step 2: Set Environment Variables
1. Create a `.env` file in your project root:
   ```properties
   DATABASE_URL=postgresql://username:password@hostname:5432/database_name
   SECRET_KEY=your_secret_key
   DEBUG=False
   ```

    **Advanced:**

    ```properties
    DATABASE_URL=postgresql://username:password@hostname:5432/database_name?sslmode=require
    SECRET_KEY=your_secret_key
    DEBUG=False
    ```

    *Comment: Adding `sslmode=require` ensures that the connection to the database is encrypted. Be cautious as this requires SSL to be configured properly.*

    **Newbie:**

    Use the first code snippet and replace the placeholders with your actual database credentials and secret key.

    **Note:** Environment variables store configuration settings that your application needs to run.

2. Use `python-dotenv` to load these variables in your app:
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

    **Advanced:**

    ```python
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv())
    ```

    *Comment: Using `find_dotenv()` ensures that the `.env` file is located correctly, even if the script is run from a different directory.*

    **Newbie:**

    Use the first code snippet to load environment variables in your application.

    **Note:** The `python-dotenv` library helps load environment variables from a `.env` file into your application's environment.

### Step 3: Adjust Permissions
1. Ensure files are readable by Passenger:
   ```bash
   chmod -R 755 /home/username/yourdomain.com
   ```

    **Advanced:**

    ```bash
    chmod -R 750 /home/username/yourdomain.com
    ```

    *Comment: Using `750` provides more restrictive permissions, enhancing security by limiting access to the owner and group.*

    **Newbie:**

    Use the first command to set the correct permissions for your project files.

    **Note:** Setting the correct permissions ensures that Passenger can read and execute your application files.

---

## 7. Testing and Troubleshooting

### Step 1: Restart Passenger
1. Restart Passenger to apply changes:
   ```bash
   touch tmp/restart.txt
   ```

    **Advanced:**

    ```bash
    touch tmp/restart.txt && tail -f logs/error.log
    ```

    *Comment: Combining the restart command with log monitoring helps immediately identify any issues that arise.*

    **Newbie:**

    Use the first command to restart Passenger and apply your changes.

    **Note:** Restarting Passenger reloads your application, applying any changes you've made.

### Step 2: Monitor Logs
1. Check Passenger logs for issues:
   ```bash
   tail -f logs/error.log
   ```

    **Advanced:**

    ```bash
    tail -f logs/error.log | grep -i "error"
    ```

    *Comment: Using `grep` filters the log output to show only lines containing "error", making it easier to spot issues.*

    **Newbie:**

    Use the first command to monitor the logs for any issues.

    **Note:** Monitoring logs helps you identify and troubleshoot any problems with your application.

### Step 3: Debugging
1. If the app doesn’t load, verify:
   - Paths in `passenger_wsgi.py`.
   - Database credentials in `.env`.
   - Python dependencies are correctly installed.

    **Advanced:**

    ```bash
    lsof -i :8000
    ```

    *Comment: Using `lsof` helps identify if another process is using the port, which can cause conflicts.*

    **Newbie:**

    Check the listed items to ensure everything is set up correctly.

    **Note:** Debugging involves checking various parts of your setup to find and fix issues preventing your application from running.

---

## 8. Handling Advanced Requirements

### Using `pip-compile`
1. Install `pip-tools`:
   ```bash
   pip install pip-tools
   ```

    **Advanced:**

    ```bash
    pip install pip-tools --user
    ```

    *Comment: Installing with `--user` avoids requiring administrative privileges.*

    **Newbie:**

    Use the first command to install `pip-tools`.

    **Note:** `pip-tools` helps manage your project's dependencies more effectively.

2. Compile dependencies:
   ```bash
   pip-compile
   ```

    **Advanced:**

    ```bash
    pip-compile --generate-hashes
    ```

    *Comment: Using `--generate-hashes` adds security by including hashes for each package.*

    **Newbie:**

    Use the first command to compile your dependencies.

    **Note:** Compiling dependencies generates a `requirements.txt` file with all the packages your project needs.

3. Install the compiled requirements:
   ```bash
   pip install -r requirements.txt
   ```

    **Advanced:**

    ```bash
    pip install -r requirements.txt --no-deps
    ```

    *Comment: Using `--no-deps` ensures only the specified packages are installed, avoiding potential conflicts.*

    **Newbie:**

    Use the first command to install the compiled requirements.

    **Note:** Installing the compiled requirements sets up your project environment with all necessary packages.

### Using `Poetry`
1. Install Poetry:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

    **Advanced:**

    ```bash
    curl -sSL https://install.python-poetry.org | python3 - --preview
    ```

    *Comment: Installing with `--preview` allows you to use the latest features available in the preview version.*

    **Newbie:**

    Use the first command to install Poetry.

    **Note:** Poetry is a dependency management tool that simplifies managing your project's dependencies.

2. Install dependencies:
   ```bash
   poetry install
   ```

    **Advanced:**

    ```bash
    poetry install --no-dev
    ```

    *Comment: Using `--no-dev` installs only the production dependencies, which can be useful for deployment.*

    **Newbie:**

    Use the first command to install your project's dependencies with Poetry.

    **Note:** Installing dependencies with Poetry sets up your project environment with all necessary packages.

---

## 9. Final Steps

### Automating Deployments
1. Automate updates with Git:
   ```bash
   git pull origin main
   touch tmp/restart.txt
   ```

    **Advanced:**

    ```bash
    git pull origin main && touch tmp/restart.txt && tail -f logs/error.log
    ```

    *Comment: Combining the commands ensures that the application is restarted and logs are monitored immediately.*

    **Newbie:**

    Use the first command to pull the latest changes from your repository and restart Passenger.

    **Note:** Automating deployments with Git ensures your server always has the latest version of your application.

### Static File Handling
1. Configure a static directory for your files and update your app to serve them.

    **Advanced:**

    ```bash
    ln -s /home/username/yourdomain.com/static /home/username/yourdomain.com/public
    ```

    *Comment: Creating a symbolic link allows Passenger to serve static files directly, improving performance.*

    **Newbie:**

    Follow the instructions in your application's documentation to configure static file handling.

    **Note:** Serving static files (like images, CSS, and JavaScript) directly improves your application's performance.

---

These instructions should help you deploy your Python project on DreamHost successfully, ensuring alignment with all requirements from the README. If further clarification is needed, consult DreamHost's support or documentation.
