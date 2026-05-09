# 📝 Notes App - Modern Web Application

A feature-rich, production-ready notes application built with Flask and Python. Create, manage, and organize your notes with a beautiful, modern interface and enterprise-grade security.

## ✨ Features

### Core Functionality
- 📌 **Create Notes**: Add unlimited notes with title and content
- ✏️ **Manage Notes**: Edit and delete your notes easily
- 🔍 **View Notes**: Browse all your notes in a modern grid layout
- 📱 **Responsive Design**: Works perfectly on desktop, tablet, and mobile

### User Authentication
- 👤 **User Registration**: Sign up with email validation
- 🔐 **Secure Login**: Protected access to your notes
- ✉️ **Email Verification**: Verify email address during signup
- 🔑 **Password Reset**: Recover your account with email verification
- 🛡️ **Remember Me**: Optional session persistence

### Security Features
- 🔒 **Password Strength Validation**: Enforces strong passwords
- 🛡️ **CSRF Protection**: Protected against cross-site attacks
- 🚫 **Rate Limiting**: Prevents brute-force attacks
- 🔐 **Session Security**: HttpOnly, Secure, and SameSite cookies
- 📊 **Security Headers**: Content Security Policy and more
- 📝 **Comprehensive Logging**: Tracks all important events

### User Experience
- 🎨 **Modern Dark Theme**: Beautiful gradient interface
- ⚡ **Loading Indicators**: Visual feedback during operations
- 🔔 **Toast Notifications**: Modern notification system
- 📊 **Password Strength Indicator**: Real-time feedback
- ⌨️ **Character Counters**: Track input length
- 🎯 **Smooth Animations**: Professional transitions
- ♿ **Accessibility**: ARIA labels and semantic HTML

### Developer Features
- 📚 **RESTful API**: JSON endpoints for integration
- 🗃️ **Database Support**: SQLite (dev) and PostgreSQL (prod)
- 📊 **Error Handling**: Comprehensive error pages
- 🔍 **Structured Logging**: Rotating file logs
- 🧪 **Production Ready**: Deployment guides included

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Gmail account (for email notifications)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/Notes-App.git
cd Notes-App
```

2. **Create virtual environment**
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Mac/Linux
source .venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Run the application**
```bash
python main.py
```

Visit `http://localhost:5000` in your browser.

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with:
```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
DATABASE_URL=sqlite:///notes.db
```

### Gmail Setup
1. Go to https://myaccount.google.com/apppasswords
2. Generate an app-specific password
3. Add credentials to `.env`

## 📂 Project Structure

```
Notes-App/
├── website/
│   ├── __init__.py          # Application factory
│   ├── auth.py              # Authentication routes
│   ├── views.py             # Note management
│   ├── models.py            # Database models
│   ├── sync_google_sheets.py
│   ├── templates/           # HTML templates
│   │   ├── base.html        # Base layout
│   │   ├── login.html       # Login page
│   │   ├── signup.html      # Registration page
│   │   ├── home.html        # Notes dashboard
│   │   ├── verify.html      # Email verification
│   │   ├── forgot_password.html
│   │   ├── reset_password.html
│   │   └── errors/          # Error pages
│   └── static/
│       └── styles.css       # Styling
├── config.py                # Configuration
├── main.py                  # Entry point
├── requirements.txt         # Dependencies
├── .env.example             # Environment template
└── PRODUCTION_GUIDE.md      # Deployment guide
```

## 🔧 Technologies Used

### Backend
- **Flask** - Web framework
- **SQLAlchemy** - ORM
- **Flask-Login** - Authentication
- **Flask-Mail** - Email sending
- **Flask-WTF** - CSRF protection
- **Flask-Limiter** - Rate limiting
- **Flask-Talisman** - Security headers

### Frontend
- **Bootstrap 5** - CSS framework
- **Font Awesome** - Icons
- **Vanilla JavaScript** - No jQuery required
- **HTML5** - Semantic markup

### Database
- **SQLite** - Development
- **PostgreSQL** - Production

## 📊 API Endpoints

### Authentication
- `POST /login` - User login
- `POST /signup` - User registration
- `GET /logout` - User logout
- `POST /verify/<email>` - Email verification
- `POST /forgot_password` - Password reset request
- `POST /reset_password/<email>` - Password reset

### Notes
- `GET /` - Get all notes
- `POST /` - Create new note
- `POST /delete/<id>` - Delete note
- `GET /api/notes` - Get notes as JSON

## 🔐 Security Best Practices

✅ **Implemented:**
- Password hashing with pbkdf2
- CSRF token validation
- Input sanitization
- Rate limiting
- Security headers
- Session security
- Logging and monitoring

## 📱 Browser Support

- ✅ Chrome/Edge (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Mobile browsers

## 🚀 Deployment

### Deploy to Render
See [PRODUCTION_GUIDE.md](PRODUCTION_GUIDE.md) for:
- Full deployment instructions
- Environment configuration
- Database setup
- Email configuration
- Security checklist

### Deploy with Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

## 🐛 Troubleshooting

### Emails not sending?
- Verify Gmail app-specific password
- Check spam folder
- Review logs in `logs/app.log`

### Database errors?
- Ensure directory permissions
- For PostgreSQL, verify connection string
- Check database user privileges

### CSRF token errors?
- Clear browser cookies
- Ensure forms include `{{ csrf_token() }}`
- Check that SESSION_COOKIE settings are correct

## 📝 Logging

Logs are stored in `logs/app.log` with automatic rotation.

```bash
# View live logs
tail -f logs/app.log

# View recent errors
grep ERROR logs/app.log
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📄 License

This project is open source and available under the MIT License.

## 👨‍💻 Author

**Ragav Radhesh**

Built with ❤️ for productivity

## 📞 Support

For issues and questions:
1. Check the [PRODUCTION_GUIDE.md](PRODUCTION_GUIDE.md)
2. Review logs in `logs/app.log`
3. Check GitHub issues

## 🎯 Roadmap

- [ ] Dark/Light theme toggle
- [ ] Note categories/tags
- [ ] Note sharing feature
- [ ] Rich text editor
- [ ] Note export (PDF, Markdown)
- [ ] Mobile app
- [ ] Two-factor authentication
- [ ] Note search functionality

---

**Last Updated**: May 2026
