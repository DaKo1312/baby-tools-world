# Running Django with WSGI Server

This document outlines the necessary steps to add a WSGI server to the project that can be used to serve the app for production.

## Preparing the project

In order to have a WSGI library added to your project follow the steps below:

- add the dependency to the `requirements.txt`
   ```bash
   # in requirements.txt
   # ...other package names
   gunicorn==<YOUR_VERSION>
   # or waitress as alternative
   waitress==<YOUR_VERSION>
   ```
- install the dependencies with `pip install -r requirements.txt`

## Running with Gunicorn

Gunicorn is a Python WSGI HTTP server that can be used to serve the application in a production-like environment.

1. **Run the Application**:
    Use the following command to start the application with Gunicorn:
    ```bash
    gunicorn --bind 0.0.0.0:8000 btw_app.wsgi:application
    ```

2. **Configuration Options**:
    You can customize Gunicorn with additional options, such as:
    - `--workers`: Number of worker processes (e.g., `--workers 3`).
    - `--timeout`: Request timeout in seconds (e.g., `--timeout 30`).

3. **Verify the Application**:
    Visit `http://localhost:8000` to ensure the application is running with Gunicorn.

By using Gunicorn, you can serve the application efficiently in a production-like setup.

#### Waitress

Waitress is a production-quality WSGI server for Python applications, designed to be simple and robust.

1. **Install Waitress**:
    If not already installed, first install Waitress using pip:
    ```bash
    pip install waitress
    ```

2. **Run the Application**:
    Use the following command to start the application with `waitress`:
    ```bash
    waitress-serve --port=8000 btw_app.wsgi:application
    ```

3. **Configuration Options**:
    You can customize Waitress with additional options, such as:
    - `--host`: Specify the host to bind to (e.g., `--host=0.0.0.0`).
    - `--threads`: Set the number of threads to use (e.g., `--threads=4`).

4. **Verify the Application**:
    Visit `http://localhost:8000` to ensure the application is running with Waitress.

Waitress provides a lightweight and reliable option for serving your Django application in production.