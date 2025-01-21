# Space Force Events Dashboard

## Table of Contents

- [Space Force Events Dashboard](#space-force-events-dashboard)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Prerequisites](#prerequisites)
  - [Setup Instructions](#setup-instructions)
  - [Running the Application](#running-the-application)
  - [Database Setup](#database-setup)
  - [Environment Variables](#environment-variables)

## Overview

The Space Force Events Dashboard is a comprehensive tool for monitoring and analyzing Space Force-related events and news. It provides real-time updates, interactive visualizations, and detailed analytics.

## Prerequisites

Before setting up the project, ensure you have the following installed:

- Python 3.11 or higher
- PostgreSQL
- `psycopg2` library for PostgreSQL
- `pip` (Python package installer)

## Setup Instructions

1. **Clone the repository:**

    ```sh
    git clone https://github.com/yourusername/SpaceForceDataFeed.git
    cd SpaceForceDataFeed
    ```

2. **Create a virtual environment:**

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install the required dependencies:**

    ```sh
    pip install -r requirements.txt
    ```

## Running the Application

1. **Set up the environment variables:**

    Create a [.env](http://_vscodecontentref_/1) file in the root directory of the project with the following content:

    ```properties
    DATABASE_URL=postgresql://jono:your_password@localhost:5432/spaceforce_datafeed
    PGUSER=jono
    PGPASSWORD=your_password
    PGHOST=localhost
    PGPORT=5432
    PGDATABASE=spaceforce_datafeed
    ```

2. **Run the application:**

    ```sh
    streamlit run main.py
    ```

## Database Setup

1. **Create the PostgreSQL database:**

    ```sh
    createdb spaceforce_datafeed
    ```

2. **Create the required tables:**

    Connect to the database using `psql` and run the SQL commands in the [schema.sql](http://_vscodecontentref_/2) file:

    ```sh
    psql $DATABASE_URL -f schema.sql
    ```

    Alternatively, you can run the commands directly in the `psql` shell:

    ```sql
    CREATE TABLE categories (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL UNIQUE
    );

    CREATE TABLE news (
        id SERIAL PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        description TEXT,
        publication_date TIMESTAMP WITH TIME ZONE NOT NULL,
        source VARCHAR(255),
        link VARCHAR(255),
        category_id INTEGER REFERENCES categories(id),
        content_hash VARCHAR(255) UNIQUE,
        image_url VARCHAR(255),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    ```

## Environment Variables

Ensure the following environment variables are set in your [.env](http://_vscodecontentref_/3) file:

```properties
DATABASE_URL=postgresql://jono:your_password@localhost:5432/spaceforce_datafeed
PGUSER=jono
PGPASSWORD=your_password
PGHOST=localhost
PGPORT=5432
PGDATABASE=spaceforce_datafeed