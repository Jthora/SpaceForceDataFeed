# Space Force Events Dashboard

## Table of Contents

- [Space Force Events Dashboard](#space-force-events-dashboard)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Prerequisites](#prerequisites)
  - [Setup Instructions](#setup-instructions)
    - [Linux/MacOS](#linuxmacos)
    - [Windows](#windows)
  - [Running the Application](#running-the-application)
  - [Database Setup](#database-setup)
  - [Environment Variables](#environment-variables)
  - [Using pip-compile](#using-pip-compile)
  - [Using Poetry](#using-poetry)
  - [Features](#features)
  - [Contributing](#contributing)
  - [License](#license)

## Overview

The Space Force Events Dashboard is a comprehensive tool for monitoring and analyzing Space Force-related events and news. It provides real-time updates, interactive visualizations, and detailed analytics.

## Prerequisites

Before setting up the project, ensure you have the following installed:

- Python 3.11 or higher
- PostgreSQL
- `psycopg2` library for PostgreSQL
- `pip` (Python package installer)

## Setup Instructions

### Linux/MacOS

1. **Clone the repository:**

    ```sh
    git clone https://github.com/yourusername/SpaceForceDataFeed.git
    cd SpaceForceDataFeed
    ```

    *Note: Ensure you have `git` installed. If not, install it using your package manager (e.g., `sudo apt-get install git` for Linux or `brew install git` for MacOS).*

    **Advanced:**

    ```sh
    git clone --depth=1 https://github.com/yourusername/SpaceForceDataFeed.git
    cd SpaceForceDataFeed
    ```

    *Comment: Cloning with `--depth=1` reduces the size of the clone and speeds up the process.*

2. **Create a virtual environment:**

    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

    *Note: If `python3` is not found, you may need to install it or use `python` instead.*

    **Advanced:**

    ```sh
    python3 -m venv --prompt SpaceForceEnv venv
    source venv/bin/activate
    ```

    *Comment: Using `--prompt` sets a custom prompt name for the virtual environment, making it easier to identify.*

3. **Install the required dependencies:**

    ```sh
    pip install -r requirements.txt
    ```

    *Note: Ensure `pip` is up-to-date by running `pip install --upgrade pip`.*

    **Advanced:**

    ```sh
    pip install -r requirements.txt --no-cache-dir
    ```

    *Comment: Using `--no-cache-dir` ensures that pip does not use the cache, which can be useful for avoiding issues with outdated cached packages.*

### Windows

1. **Clone the repository:**

    ```sh
    git clone https://github.com/yourusername/SpaceForceDataFeed.git
    cd SpaceForceDataFeed
    ```

    *Note: Ensure you have `git` installed. If not, download and install it from [git-scm.com](https://git-scm.com/).*

    **Advanced:**

    ```sh
    git clone --depth=1 https://github.com/yourusername/SpaceForceDataFeed.git
    cd SpaceForceDataFeed
    ```

    *Comment: Cloning with `--depth=1` reduces the size of the clone and speeds up the process.*

2. **Create a virtual environment:**

    ```sh
    python -m venv venv
    venv\Scripts\activate
    ```

    *Note: If `python` is not found, ensure Python is added to your PATH during installation.*

    **Advanced:**

    ```sh
    python -m venv --prompt SpaceForceEnv venv
    venv\Scripts\activate
    ```

    *Comment: Using `--prompt` sets a custom prompt name for the virtual environment, making it easier to identify.*

3. **Install the required dependencies:**

    ```sh
    pip install -r requirements.txt
    ```

    *Note: Ensure `pip` is up-to-date by running `python -m pip install --upgrade pip`.*

    **Advanced:**

    ```sh
    pip install -r requirements.txt --no-cache-dir
    ```

    *Comment: Using `--no-cache-dir` ensures that pip does not use the cache, which can be useful for avoiding issues with outdated cached packages.*

## Running the Application

1. **Set up the environment variables:**

    Create a `.env` file in the root directory of the project with the following content:

    ```properties
    DATABASE_URL=postgresql://jono:your_password@localhost:5432/spaceforce_datafeed
    PGUSER=jono
    PGPASSWORD=your_password
    PGHOST=localhost
    PGPORT=5432
    PGDATABASE=spaceforce_datafeed
    ```

    *Note: Replace `your_password` with your actual PostgreSQL password.*

    **Advanced:**

    ```sh
    echo "DATABASE_URL=postgresql://jono:your_password@localhost:5432/spaceforce_datafeed" >> .env
    echo "PGUSER=jono" >> .env
    echo "PGPASSWORD=your_password" >> .env
    echo "PGHOST=localhost" >> .env
    echo "PGPORT=5432" >> .env
    echo "PGDATABASE=spaceforce_datafeed" >> .env
    ```

    *Comment: Using `echo` commands can automate the creation of the `.env` file.*

2. **Run the application:**

    ```sh
    streamlit run main.py
    ```

    *Note: Ensure `streamlit` is installed. If not, install it using `pip install streamlit`.*

    **Advanced:**

    ```sh
    streamlit run main.py --server.port 8501
    ```

    *Comment: Specifying `--server.port` allows you to run the application on a different port if the default port is in use.*

## Database Setup

1. **Install PostgreSQL:**

    - **Linux:** Use your package manager, e.g., `sudo apt-get install postgresql`
    - **MacOS:** Use Homebrew, e.g., `brew install postgresql`
    - **Windows:** Download and install from the [official website](https://www.postgresql.org/download/windows/)

    *Note: Follow the installation instructions specific to your operating system.*

    **Advanced:**

    - **Linux:** `sudo apt-get install postgresql postgresql-contrib`
    - **MacOS:** `brew install postgresql@14`
    - **Windows:** Use the EnterpriseDB installer for additional tools

    *Comment: Installing `postgresql-contrib` or a specific version can provide additional tools and features.*

2. **Start PostgreSQL service:**

    - **Linux/MacOS:** `sudo service postgresql start`
    - **Windows:** Start the PostgreSQL service from the Services application

    *Note: Ensure the PostgreSQL service is running before proceeding.*

    **Advanced:**

    - **Linux/MacOS:** `sudo systemctl enable postgresql && sudo systemctl start postgresql`
    - **Windows:** Use `pg_ctl` to start the service from the command line

    *Comment: Enabling the service ensures it starts automatically on boot.*

3. **Create the database and tables:**

    Connect to your PostgreSQL database and run the commands in `schema.sql` to create the necessary tables.

    ```sh
    psql -U jono -d spaceforce_datafeed -f schema.sql
    ```

    *Note: Replace `jono` with your PostgreSQL username if different.*

    **Advanced:**

    ```sh
    psql -U jono -d spaceforce_datafeed -f schema.sql --echo-all
    ```

    *Comment: Using `--echo-all` provides detailed output of the SQL commands being executed.*

## Environment Variables

Ensure the following environment variables are set in your `.env` file:

```properties
DATABASE_URL=postgresql://jono:your_password@localhost:5432/spaceforce_datafeed
PGUSER=jono
PGPASSWORD=your_password
PGHOST=localhost
PGPORT=5432
PGDATABASE=spaceforce_datafeed
```

*Note: Replace `your_password` with your actual PostgreSQL password.*

**Advanced:**

```properties
DATABASE_URL=postgresql://jono:your_password@localhost:5432/spaceforce_datafeed?sslmode=require
PGUSER=jono
PGPASSWORD=your_password
PGHOST=localhost
PGPORT=5432
PGDATABASE=spaceforce_datafeed
```

*Comment: Adding `sslmode=require` ensures that the connection to the database is encrypted.*

## Using pip-compile

1. **Install pip-tools:**

    ```sh
    pip install pip-tools
    ```

    *Note: `pip-tools` helps manage dependencies more effectively.*

    **Advanced:**

    ```sh
    pip install pip-tools --user
    ```

    *Comment: Installing with `--user` avoids requiring administrative privileges.*

2. **Compile the dependencies:**

    ```sh
    pip-compile
    ```

    *Note: This generates a `requirements.txt` file from `pyproject.toml`.*

    **Advanced:**

    ```sh
    pip-compile --generate-hashes
    ```

    *Comment: Using `--generate-hashes` adds security by including hashes for each package.*

3. **Install the compiled dependencies:**

    ```sh
    pip install -r requirements.txt
    ```

    *Note: Ensure `requirements.txt` is up-to-date by running `pip-compile` whenever dependencies change.*

    **Advanced:**

    ```sh
    pip install -r requirements.txt --no-deps
    ```

    *Comment: Using `--no-deps` ensures only the specified packages are installed, avoiding potential conflicts.*

## Using Poetry

1. **Install Poetry:**

    ```sh
    curl -sSL https://install.python-poetry.org | python3 -
    ```

    *Note: Follow the instructions provided by Poetry for your operating system.*

    **Advanced:**

    ```sh
    curl -sSL https://install.python-poetry.org | python3 - --preview
    ```

    *Comment: Installing with `--preview` allows you to use the latest features available in the preview version.*

2. **Install dependencies:**

    ```sh
    poetry install
    ```

    *Note: This installs all dependencies listed in `pyproject.toml`.*

    **Advanced:**

    ```sh
    poetry install --no-dev
    ```

    *Comment: Using `--no-dev` installs only the production dependencies, which can be useful for deployment.*

3. **Activate the virtual environment:**

    ```sh
    poetry shell
    ```

    *Note: This activates the virtual environment managed by Poetry.*

    **Advanced:**

    ```sh
    poetry shell --no-interaction
    ```

    *Comment: Using `--no-interaction` avoids prompts, making the command suitable for automated scripts.*

## Features

- Real-time updates
- Interactive visualizations
- Detailed analytics

## Contributing

Contributions are welcome! Please read the [contributing guidelines](CONTRIBUTING.md) first.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.