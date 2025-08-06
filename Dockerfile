# Multi-stage build for MedLab Pro
FROM python:3.11-slim as builder

# Set environment variables for build
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY pyproject.toml ./
RUN pip install --upgrade pip \
    && pip install flask flask-sqlalchemy flask-login flask-dance \
       werkzeug sqlalchemy psycopg2-binary gunicorn openai \
       pandas openpyxl email-validator pyjwt python-dotenv

# Production stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV PYTHONPATH=/app
ENV PORT=5000

# Install runtime dependencies and security updates
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    dumb-init \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && pip install --upgrade pip

# Create app user with specific UID/GID for security
RUN groupadd -r -g 1001 medlab && \
    useradd -r -u 1001 -g medlab -d /app -s /bin/bash medlab

# Set work directory and create necessary directories
WORKDIR /app
RUN mkdir -p /app/logs /app/uploads /app/static /app/templates \
    && chown -R medlab:medlab /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code with proper ownership
COPY --chown=medlab:medlab . .

# Set proper permissions
RUN chmod +x main.py && \
    find /app -type f -name "*.py" -exec chmod 644 {} \; && \
    find /app -type d -exec chmod 755 {} \;

# Switch to non-root user
USER medlab

# Expose port
EXPOSE 5000

# Health check with better configuration
HEALTHCHECK --interval=15s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Use dumb-init to handle signals properly
ENTRYPOINT ["dumb-init", "--"]

# Optimized gunicorn configuration for production
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "4", \
     "--threads", "4", \
     "--worker-class", "gthread", \
     "--worker-connections", "1000", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "100", \
     "--timeout", "30", \
     "--keep-alive", "2", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info", \
     "--capture-output", \
     "--enable-stdio-inheritance", \
     "main:app"]