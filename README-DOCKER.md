# MedLab Pro - Docker Deployment Guide

This guide explains how to deploy MedLab Pro using Docker for development and production environments.

## Prerequisites

- Docker Engine 20.10+ 
- Docker Compose 2.0+
- Minimum 4GB RAM for production deployment
- SSL certificates for HTTPS (production only)

## Quick Start

### Development Environment
```bash
# Clone the repository
git clone <repository-url>
cd medlab-pro

# Copy environment file
cp .env.example .env

# Edit .env with your configuration
nano .env

# Build and run with Docker Compose
docker-compose up --build

# Run in background
docker-compose up -d --build
```

The application will be available at `http://localhost`

### Production Environment (Recommended)
```bash
# Set required environment variables
export DB_PASSWORD="your-secure-db-password"
export SESSION_SECRET="your-secure-session-secret"
export OPENAI_API_KEY="your-openai-api-key"

# Deploy with production configuration
docker-compose -f docker-compose.prod.yml up -d --build

# Check deployment status
docker-compose -f docker-compose.prod.yml ps
```

### Production Environment
```bash
# Use the production compose file
docker-compose -f docker-compose.prod.yml up --build -d

# Or with environment variables
DB_PASSWORD=secure_password SESSION_SECRET=secure_session_key OPENAI_API_KEY=your_key docker-compose -f docker-compose.prod.yml up -d
```

## Architecture

The Docker setup includes:

- **Web Application**: Flask application with gunicorn server
- **Database**: PostgreSQL 15 with automated initialization
- **Reverse Proxy**: Nginx with SSL support and security headers
- **Cache** (Production): Redis for session storage and caching

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes | - |
| `DB_PASSWORD` | Database password | Yes | - |
| `SESSION_SECRET` | Flask session secret | Yes | - |
| `OPENAI_API_KEY` | OpenAI API key for AI reports | Yes | - |
| `FLASK_ENV` | Flask environment | No | production |

### SSL Configuration

For HTTPS in production:

1. Place your SSL certificates in the `ssl/` directory:
   - `ssl/cert.pem` - SSL certificate
   - `ssl/key.pem` - Private key

2. Uncomment the HTTPS server block in `nginx.conf`

3. Update the server name to match your domain

## Data Persistence

- **Database**: PostgreSQL data is stored in the `postgres_data` volume
- **Logs**: Application logs are stored in `./logs/` directory
- **Redis** (Production): Redis data is stored in the `redis_data` volume

## Health Checks

The application includes health check endpoints:

- `/health` - Application health status
- Database connectivity is verified automatically

## Monitoring

### Logs
```bash
# View application logs
docker-compose logs -f web

# View database logs
docker-compose logs -f db

# View nginx logs
docker-compose logs -f nginx
```

### Resource Usage
```bash
# Check container resource usage
docker stats
```

## Scaling

### Horizontal Scaling
The production configuration supports multiple web application replicas:

```bash
# Scale web application to 3 instances
docker-compose -f docker-compose.prod.yml up --scale web=3 -d
```

### Performance Tuning

1. **Database**: Adjust PostgreSQL configuration in `postgresql.conf`
2. **Application**: Modify gunicorn workers/threads in `Dockerfile`
3. **Nginx**: Configure rate limiting and caching in `nginx.conf`

## Security Features

- Non-root user execution
- Security headers via Nginx
- Rate limiting on API endpoints
- HTTPS support with modern TLS configuration
- Container isolation with custom networks

## Backup

### Database Backup
```bash
# Create backup
docker-compose exec db pg_dump -U medlab medlabpro > backup.sql

# Restore backup
docker-compose exec -T db psql -U medlab medlabpro < backup.sql
```

### Complete System Backup
```bash
# Backup volumes
docker run --rm -v medlab-pro_postgres_data:/data -v $(pwd):/backup ubuntu tar czf /backup/postgres_backup.tar.gz /data
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check DATABASE_URL environment variable
   - Ensure PostgreSQL container is healthy
   - Verify network connectivity

2. **Application Won't Start**
   - Check logs: `docker-compose logs web`
   - Verify all required environment variables are set
   - Ensure database is initialized

3. **Performance Issues**
   - Monitor resource usage with `docker stats`
   - Check application logs for slow queries
   - Consider scaling web application instances

### Debug Mode
```bash
# Run in development mode with debug output
docker-compose -f docker-compose.yml -f docker-compose.debug.yml up
```

## Maintenance

### Updates
```bash
# Pull latest images
docker-compose pull

# Restart with new images
docker-compose up -d --force-recreate
```

### Cleanup
```bash
# Remove unused containers and images
docker system prune -a

# Remove unused volumes (WARNING: This will delete data)
docker volume prune
```

## Support

For production deployment support:
1. Check logs for error details
2. Verify environment configuration
3. Ensure all required services are healthy
4. Check network connectivity between containers