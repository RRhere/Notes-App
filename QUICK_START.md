# ⚡ QUICK START GUIDE

Get your modern Notes App running in 5 minutes!

## 🚀 Installation

### Step 1: Setup Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure App
```bash
# Copy example config
cp .env.example .env

# Edit .env with your settings (minimal required):
# FLASK_ENV=development
# SECRET_KEY=dev-secret-key (or use: python -c "import secrets; print(secrets.token_hex(32))")
# MAIL_USERNAME=your-email@gmail.com (or skip for testing)
# MAIL_PASSWORD=your-app-password (or skip for testing)
```

### Step 4: Run App
```bash
python main.py
```

Visit: http://localhost:5000

---

## 🎯 Quick Test

### Create Account
1. Click "Signup"
2. Enter email, name, password
3. For testing: Check console for OTP (or use random 6-digit)
4. Verify email
5. Login!

### Create Notes
1. Enter title: "My First Note"
2. Enter content: "Hello, Notes App!"
3. Click "Save Note"
4. See toast notification: "Note saved successfully!"

### Delete Notes
1. Click trash icon on any note
2. Confirm deletion in modal
3. Note disappears with animation
4. See success toast

### Test Loading States
- Watch loading overlay during form submissions
- See button state change to "Saving..."

### Test Toast Notifications
- Form errors show as error toasts
- Success messages appear as success toasts
- All auto-dismiss after 5 seconds

---

## 📧 Email Setup (Optional for Testing)

### Gmail Configuration
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Windows Computer"
3. Generate password
4. Add to .env:
   ```env
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=16-character-password
   ```
5. Restart app

### Test Email
1. Go to forgot_password
2. Enter your email
3. Check your email for verification code
4. Use code to reset password

---

## 🔧 Development Tips

### View Logs
```bash
# Real-time logs
tail -f logs/app.log

# On Windows, use:
# type nul > logs/app.log  # Create if not exists
# then monitor in your IDE
```

### Database Reset
```bash
# Delete database
rm website/temp1.db

# Restart app - creates new database
python main.py
```

### Flask Shell (Advanced)
```bash
python -c "from website import create_app; from website import db; app = create_app(); app.app_context().push(); print('Database connected')"
```

### Debug Mode
Set in .env:
```env
FLASK_ENV=development
```
App will reload on file changes

---

## 📊 Feature Checklist

- [x] Modern UI with dark theme
- [x] Loading indicators
- [x] Toast notifications
- [x] Password strength indicator
- [x] Character counters
- [x] Email verification
- [x] Error pages
- [x] Rate limiting
- [x] Security headers
- [x] Logging

---

## 🐛 Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'flask'"
**Solution**: Activate virtual environment first
```bash
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate
```

### Issue: "Port 5000 already in use"
**Solution**: Use different port
```bash
# Edit .env or run:
python main.py  # Will use FLASK_PORT from .env, defaults to 5000
```

### Issue: Emails not sending
**Solution**: 
- Check MAIL_USERNAME and MAIL_PASSWORD in .env
- Ensure Gmail app-specific password is correct
- Check logs: `logs/app.log`
- For development, skip email verification

### Issue: CSRF token error on forms
**Solution**:
- Ensure all forms have `{{ csrf_token() }}`
- Clear browser cookies
- Restart the app

### Issue: Database locked
**Solution**:
```bash
# Kill any running processes
# Then restart app
python main.py
```

---

## 🔐 Security Notes

### Development
- ✅ Use `SECRET_KEY=dev-secret-key` (it's just for dev!)
- ✅ CSRF protection enabled
- ✅ Rate limiting active
- ✅ All data is stored locally

### Before Production
- ⚠️ Generate strong SECRET_KEY
- ⚠️ Set FLASK_ENV=production
- ⚠️ Use PostgreSQL database
- ⚠️ Configure HTTPS
- ⚠️ Review PRODUCTION_GUIDE.md

---

## 📱 Browser Testing

### Test Responsive Design
1. Open Chrome DevTools (F12)
2. Click device toggle (Ctrl+Shift+M)
3. Test on different screen sizes:
   - Mobile: 375px
   - Tablet: 768px
   - Desktop: 1920px

### Dark Mode
Already implemented! App uses dark theme by default.

---

## 🎨 Customize Appearance

### Colors
Edit `website/static/styles.css`:
```css
:root {
    --primary: #ff004f;           /* Main accent color */
    --bg-color: #0f172a;          /* Background */
    --text-color: #ffffff;         /* Text color */
    /* ... more colors */
}
```

### Fonts
Already using "Poppins" from Google Fonts. Change in templates:
```html
<link href="https://fonts.googleapis.com/css2?family=YOUR_FONT:wght@300;400;500;600;700&display=swap" rel="stylesheet">
```

---

## 📚 Next Steps

1. **Read UPGRADE_SUMMARY.md** - See all improvements
2. **Review PRODUCTION_GUIDE.md** - Deployment guide
3. **Check README.md** - Full documentation
4. **Explore Code** - Well-commented files in `website/`

---

## 🚀 Deploy to Production

### Render.com (Easiest)
See render.yaml in your project for deployment config

### Self-Hosted
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

### Heroku (Deprecated but supported)
```bash
git push heroku main
```

---

## 💡 Pro Tips

✨ **Tip 1**: Use Chrome DevTools to test API responses
- Network tab → check JSON responses from `/api/notes`

✨ **Tip 2**: Test on mobile
- Use `python main.py` then visit from phone on same network
- Replace localhost with your computer's IP: `http://192.168.x.x:5000`

✨ **Tip 3**: Check logs for debugging
- All auth events logged to `logs/app.log`
- Search for "ERROR" to find issues

✨ **Tip 4**: Use password strength indicator
- When signing up, watch real-time password strength update
- Helps users create strong passwords

✨ **Tip 5**: Test rate limiting
- Try logging in 6 times quickly - 6th will be blocked
- Check error message in toast notification

---

## 📞 Quick Help

```bash
# See installed packages
pip list

# Update all packages
pip install --upgrade -r requirements.txt

# Check Python version
python --version

# Generate strong secret key
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## ✅ Verification Checklist

After starting the app, verify:

- [ ] App loads at http://localhost:5000
- [ ] Can view login page
- [ ] Navbar is visible and styled
- [ ] Footer is at bottom
- [ ] No console errors (F12)
- [ ] Responsive on mobile (F12 → Toggle device)
- [ ] Can type in form fields
- [ ] Form has loading state on submit

---

## 🎓 Learning Resources

- **Flask Docs**: https://flask.palletsprojects.com/
- **Bootstrap Docs**: https://getbootstrap.com/docs/5.0/
- **MDN Web Docs**: https://developer.mozilla.org/
- **Python Docs**: https://docs.python.org/3/

---

## 🎉 You're All Set!

Your modern Notes App is ready to use! 

**Key Features to Try:**
- 📝 Create your first note
- 🔐 Test password strength on signup
- 📧 Reset password (test email if configured)
- 📱 View on mobile
- 🎨 Enjoy the modern interface!

---

**Need help?** Check the logs or review PRODUCTION_GUIDE.md

Happy note-taking! 🚀