# UPick Management

Version 0.1.0
This is a work in progress project.  Small progress will be made during 2025 because I will be outside working on my Upick garden.

I expect to be able to finish this during the winter of 2025 - 2026.


UPick Management is a Django-based web application for managing and optimizing pick operations 
It provides tools for:

- Plant Planning
- Bed Planning
- Work Calendar w/ Pdf printout
- Produce Availability
- Garden Logs
- Reminders


## 📋 Table of Contents

- [Features](#features)
- [Screenshots](#screenshots)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## 📸 Screenshots

*Coming soon*

## 🔧 Requirements

- Python 3.8+
- Django 4.2+
- SQLite3 
- Nginx
- Gunicorn
- Certbot

## 🚀 Installation

1. Clone the repository
   ```bash
   git clone https://github.com/BillLensmire/upickmanagement.git
   cd upickmanagement
   ```

2. Create and activate a virtual environment (optional but recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Configure settings
   ```bash
   cp upick/upick/settings_example.py upick/upick/settings_local.py
   # Edit settings_local.py with your configuration
   ```

5. Run migrations
   ```bash
   python manage.py migrate
   ```

6. Create a superuser (admin)
   ```bash
   python manage.py createsuperuser
   ```

7. Start the development server
   ```bash
   python manage.py runserver
   ```

8. Access the application at http://127.0.0.1:8000

## 📖 Usage

### Admin Interface

Access the admin interface at `/admin`


## 🚢 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.