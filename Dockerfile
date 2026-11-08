FROM python:3.12-slim AS backend

# Destination to copy all assets to during the build process.
ARG _WORKDIR=/app
# Set working directory to WORKDIR Argument
WORKDIR ${_WORKDIR}

# Default port for the app to start with
ENV APP_PORT=8000

# Copy all non-ignored files to image
COPY . ${_WORKDIR}

# Install package dependencies for app
RUN pip install -r requirements.txt \
    && chmod +x /app/entrypoint.sh

# Switch WORKDIR to src/ in order to execute entrypoint commands from there
WORKDIR /app/src

EXPOSE $APP_PORT
ENTRYPOINT [ "/bin/sh", "-c", "/app/entrypoint.sh" ]