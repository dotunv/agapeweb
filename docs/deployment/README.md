# Deployment Process

This document provides detailed instructions for deploying the Agape subscription management system to different environments, including staging and production.

## Table of Contents

1. [Deployment Environments](#deployment-environments)
2. [Prerequisites](#prerequisites)
3. [Deployment Steps](#deployment-steps)
4. [Continuous Integration/Continuous Deployment (CI/CD)](#continuous-integrationcontinuous-deployment-cicd)
5. [Rollback Procedures](#rollback-procedures)
6. [Monitoring and Maintenance](#monitoring-and-maintenance)

## Deployment Environments

The Agape system can be deployed to the following environments:

### Development

- Used for local development and testing
- Typically uses SQLite as the database
- Debug mode enabled
- No production-level security measures

### Staging

- Mirrors the production environment
- Used for testing before deploying to production
- Uses PostgreSQL as the database
- Debug mode disabled
- Full security measures implemented
- Accessible only to internal team members

### Production

- Live environment accessible to users
- Uses PostgreSQL as the database
- Debug mode disabled
- Full security measures implemented
- Performance optimizations enabled
- Regular backups configured

## Prerequisites

Before deploying the Agape system, ensure you have the following:

### Server Requirements

- Linux server (Ubuntu 20.04 LTS or later recommended)
- Python 3.8+
- PostgreSQL 12+
- Nginx
- Gunicorn
- Supervisor
- Let's Encrypt for SSL certificates

### Domain and DNS

- Registered domain name
- DNS records configured to point to your server
- SSL certificate for secure HTTPS connections

### Access and Permissions

- SSH access to the server
- Sudo privileges for installing packages
- Database user with appropriate permissions

## Deployment Steps

### 1. Server Setup

#### Install Required Packages

```bash
# Update package lists
sudo apt update

# Install required packages
sudo apt install python3-pip python3-venv nginx postgresql postgresql-contrib supervisor

# Install Let's Encrypt certbot
sudo apt install certbot python3-certbot-nginx
```

#### Create a Database

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create a database and user
CREATE DATABASE agape;
CREATE USER agape_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE agape TO agape_user;
ALTER USER agape_user CREATEDB;  # Needed for running tests
\q
```

### 2. Application Setup

#### Clone the Repository

```bash
# Create directory for the application
sudo mkdir -p /var/www/agape
sudo chown $USER:$USER /var/www/agape

# Clone the repository
git clone <repository-url> /var/www/agape
cd /var/www/agape
```

#### Set Up Virtual Environment

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn
```

#### Configure Environment Variables

Create a `.env` file in the project root:

```bash
# For staging
echo "DJANGO_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(50))')" > .env
echo "DJANGO_DEBUG=False" >> .env
echo "DATABASE_URL=postgres://agape_user:secure_password@localhost:5432/agape" >> .env
echo "ALLOWED_HOSTS=staging.example.com" >> .env
echo "CORS_ALLOWED_ORIGINS=https://staging.example.com" >> .env

# For production
echo "DJANGO_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(50))')" > .env
echo "DJANGO_DEBUG=False" >> .env
echo "DATABASE_URL=postgres://agape_user:secure_password@localhost:5432/agape" >> .env
echo "ALLOWED_HOSTS=example.com,www.example.com" >> .env
echo "CORS_ALLOWED_ORIGINS=https://example.com,https://www.example.com" >> .env
```

#### Apply Migrations and Collect Static Files

```bash
# Apply migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --no-input
```

#### Create a Superuser

```bash
python manage.py createsuperuser
```

### 3. Web Server Configuration

#### Configure Gunicorn

Create a Gunicorn service file:

```bash
sudo nano /etc/systemd/system/gunicorn_agape.service
```

Add the following content:

```ini
[Unit]
Description=gunicorn daemon for Agape
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/agape
ExecStart=/var/www/agape/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/var/www/agape/agape.sock agape.wsgi:application
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Start and enable the Gunicorn service:

```bash
sudo systemctl start gunicorn_agape
sudo systemctl enable gunicorn_agape
```

#### Configure Nginx

Create an Nginx configuration file:

```bash
sudo nano /etc/nginx/sites-available/agape
```

Add the following content:

```nginx
server {
    listen 80;
    server_name example.com www.example.com;  # Replace with your domain

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /var/www/agape;
    }
    
    location /media/ {
        root /var/www/agape;
    }
    
    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/agape/agape.sock;
    }
}
```

Enable the site and restart Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/agape /etc/nginx/sites-enabled/
sudo nginx -t  # Test the configuration
sudo systemctl restart nginx
```

#### Set Up SSL with Let's Encrypt

```bash
sudo certbot --nginx -d example.com -d www.example.com
```

### 4. Supervisor Configuration (Optional)

Supervisor can be used to ensure that Gunicorn is always running:

```bash
sudo nano /etc/supervisor/conf.d/agape.conf
```

Add the following content:

```ini
[program:agape]
command=/var/www/agape/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/var/www/agape/agape.sock agape.wsgi:application
directory=/var/www/agape
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/agape/gunicorn.err.log
stdout_logfile=/var/log/agape/gunicorn.out.log
```

Create the log directory and update Supervisor:

```bash
sudo mkdir -p /var/log/agape
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl status agape
```

## Continuous Integration/Continuous Deployment (CI/CD)

### GitHub Actions

We use GitHub Actions for CI/CD. The workflow is defined in `.github/workflows/ci.yml` and includes:

1. Running tests on multiple Python versions
2. Linting with flake8
3. Checking for security vulnerabilities
4. Generating coverage reports
5. Deploying to staging or production based on the branch

### Deployment Workflow

1. **Development to Staging**:
   - Merge feature branches into `develop`
   - GitHub Actions automatically deploys to staging
   - Test the changes in the staging environment

2. **Staging to Production**:
   - Create a pull request from `develop` to `main`
   - Review and approve the pull request
   - Merge the pull request
   - GitHub Actions automatically deploys to production

### Manual Deployment

If you need to deploy manually:

```bash
# SSH into the server
ssh user@example.com

# Navigate to the project directory
cd /var/www/agape

# Pull the latest changes
git pull

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --no-input

# Restart Gunicorn
sudo systemctl restart gunicorn_agape
```

## Rollback Procedures

If a deployment causes issues, you can roll back to a previous version:

### Using Git

```bash
# SSH into the server
ssh user@example.com

# Navigate to the project directory
cd /var/www/agape

# Check the commit history
git log --oneline

# Revert to a specific commit
git checkout <commit-hash>

# Apply migrations if necessary
source venv/bin/activate
python manage.py migrate

# Restart Gunicorn
sudo systemctl restart gunicorn_agape
```

### Database Rollback

If database migrations cause issues:

```bash
# Revert to a specific migration
python manage.py migrate app_name migration_name

# For example, to revert to migration 0003 in the users app:
python manage.py migrate users 0003
```

## Monitoring and Maintenance

### Monitoring

- Use Django Debug Toolbar in development
- Set up Sentry for error tracking
- Configure logging to track errors and warnings
- Use Prometheus and Grafana for performance monitoring

### Backups

Set up regular database backups:

```bash
# Create a backup script
sudo nano /usr/local/bin/backup_agape_db.sh
```

Add the following content:

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/agape"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/agape_$TIMESTAMP.sql"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Create backup
pg_dump -U agape_user -h localhost agape > $BACKUP_FILE

# Compress backup
gzip $BACKUP_FILE

# Remove backups older than 30 days
find $BACKUP_DIR -type f -name "*.sql.gz" -mtime +30 -delete
```

Make the script executable and set up a cron job:

```bash
sudo chmod +x /usr/local/bin/backup_agape_db.sh
sudo crontab -e
```

Add the following line to run the backup daily at 2 AM:

```
0 2 * * * /usr/local/bin/backup_agape_db.sh
```

### Maintenance Tasks

Regular maintenance tasks include:

- Updating dependencies
- Applying security patches
- Monitoring disk space
- Checking log files for errors
- Testing backup restoration
- Reviewing performance metrics

For more information on specific maintenance tasks, see the [Troubleshooting Guide](../troubleshooting/README.md).