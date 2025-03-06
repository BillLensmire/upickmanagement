# Upick Deployment Guide

This guide provides instructions for deploying the Upick application on a Linux server like Linode.

## Prerequisites

- A Linux server (Ubuntu 22.04 LTS recommended)
- A domain name pointing to your server
- Basic knowledge of Linux command line
- SSH access to your server

## Server Setup

### 1. Update System Packages

```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Install Required Packages

```bash
sudo apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx libpango-1.0-0 libpangoft2-1.0-0
```

## Application Deployment

### 1. Create Application Directory

```bash
sudo mkdir -p /var/www/upickmanagement
sudo chown -R www-data:www-data /var/www/upickmanagement
```

### 2. Clone the Repository (or Transfer Files)

Option 1: Clone from Git (if using version control):
```bash
git clone https://github.com/BillLensmire/upickmanagement.git /var/www/upickmanagement
```

sudo chown -R www-data:www-data /var/www/upickmanagement

### 3. Set Up Virtual Environment

```bash
cd /var/www/upickmanagement
python3 -m venv .venv
source .venv/bin/activate
pip install -r upick/requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file:
```bash
sudo nano /var/www/upickmanagement/.env
```

to make django key : 
```bash
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Add the following content for sqlite3
```
DJANGO_SETTINGS_MODULE=upick.settings_production
DJANGO_SECRET_KEY=your-very-secure-secret-key
DB_NAME=upick.sqlite3
DEBUG=False
```

Load environment variables in systemd service:
```bash
sudo nano /etc/systemd/system/upick.service
```

Copy the content from the `upick.service` file in your project.

### 6. Configure Production Settings

The project includes a `upick.settings_production.py` file that inherits from the base settings and applies production-specific configurations. You need to modify this file based on your database choice:


Update the domain names in `ALLOWED_HOSTS` to match your actual domain.

### 7. Set Up Django Application

```bash
cd /var/www/upickmanagement
source .venv/bin/activate

# Apply migrations
python3 manage.py makemigrations
python3 manage.py migrate --settings=upick.settings_production

# Collect static files
python3 manage.py collectstatic --settings=upick.settings_production --no-input

# Create superuser
python3 manage.py createsuperuser --settings=upick.settings_production
```

sudo chown -R www-data:www-data /var/www/upickmanagement

### 8. Set Up Gunicorn

Create required directories:
```bash
sudo mkdir -p /var/log/gunicorn
sudo chown -R www-data:www-data /var/log/gunicorn
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable upick
sudo systemctl start upick
```

Check status:
```bash
sudo systemctl status upick
```

### 9. Set Up Nginx

Copy the Nginx configuration:
```bash
sudo cp /var/www/upickmanagement/upick_nginx.conf /etc/nginx/sites-available/upick
```

Edit the configuration to update your domain name:
```bash
sudo nano /etc/nginx/sites-available/upick
```
```

Create a symbolic link:
```bash
sudo ln -s /etc/nginx/sites-available/upick /etc/nginx/sites-enabled/
```

Test Nginx configuration:
```bash
sudo nginx -t
```

Restart Nginx:
```bash
sudo systemctl restart nginx
```

sudo ufw allow 'Nginx Full'
sudo ufw delete allow 'Nginx HTTP'


### 10. Set Up SSL with Let's Encrypt

```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

Follow the prompts to complete the SSL setup.

### 11. Final Checks

- Visit your domain in a web browser to ensure the application is running
- Try logging in to the admin interface at `https://your-domain.com/admin/`
- Check the logs if there are any issues:
  ```bash
  sudo journalctl -u upick
  sudo cat /var/log/gunicorn/upick-error.log
  sudo cat /var/log/nginx/upick-error.log
  ```

## Maintenance

### Updating the Application

```bash
cd /var/www/upickmanagement
git pull  # If using git

source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate --settings=upick.settings_production
python manage.py collectstatic --settings=upick.settings_production --no-input

sudo systemctl restart upick
```

### Renewing SSL Certificates

SSL certificates from Let's Encrypt are valid for 90 days and are automatically renewed by a cron job. You can manually renew them with:

```bash
sudo certbot renew
```

## Troubleshooting

### 1. Application Not Loading

Check Gunicorn status:
```bash
sudo systemctl status upick
```

Check Gunicorn logs:
```bash
sudo cat /var/log/gunicorn/upick-error.log
```

### 2. Database Connection Issues

Check database connection settings in the `.env` file.

### 3. Static Files Not Loading

Ensure static files were collected:
```bash
source .venv/bin/activate
python manage.py collectstatic --settings=upick.settings_production --no-input
```

Check Nginx configuration for the static files location.
```

### 4. Permission Issues

Ensure proper ownership of files:
```bash
sudo chown -R www-data:www-data /var/www/upickmanagement
```
