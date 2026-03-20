# TrainCare Connect - Quick Start Guide

## 🚀 Starting the Application

```bash
python app.py
```

The application will start on: **http://localhost:5000**

## 🌐 Language Translation System

### How to Change Language

1. **Look for the Language Button** in the top-right corner:
   ```
   🌐 English ▼
   ```

2. **Click the button** - A dropdown menu will appear with 6 languages:
   - 🇬🇧 **English**
   - 🇮🇳 **हिंदी** (Hindi)
   - 🇮🇳 **తెలుగు** (Telugu)
   - 🇮🇳 **தமிழ்** (Tamil)
   - 🇮🇳 **বাংলা** (Bengali)
   - 🇮🇳 **മലയാളം** (Malayalam)

3. **Select your language** - The page will reload with all text translated

### Testing Telugu Translation

1. Go to: http://localhost:5000/emergency
2. Click the language button (🌐 English ▼)
3. Select: 🇮🇳 తెలుగు
4. The page will reload and you should see:

**Before (English):**
- Report Emergency
- Passenger Name
- Phone Number
- Train Number
- Emergency Type

**After (Telugu):**
- అత్యవసర పరిస్థితిని నివేదించండి
- ప్రయాణికుడి పేరు
- ఫోన్ నంబర్
- రైలు నంబర్
- అత్యవసర రకం

## 🔐 Login Credentials

### For Passengers
- Go to: http://localhost:5000/login
- Click "Sign Up" to create an account
- Or use test credentials if you've created them

### For Admin
- Go to: http://localhost:5000/admin_login
- Username: `admin`
- Password: `admin123`

### For Station Masters
- Go to: http://localhost:5000/station_master_login
- Station Code: `NDLS` (New Delhi) or `BCT` (Mumbai Central) or `MAS` (Chennai Central)
- Password: `station123`

## 📍 Available Pages

### Public Pages
- **Homepage**: http://localhost:5000/
- **Emergency Form**: http://localhost:5000/emergency
- **Login**: http://localhost:5000/login
- **Admin Login**: http://localhost:5000/admin_login
- **Station Master Login**: http://localhost:5000/station_master_login

### After Login
- **User Dashboard**: http://localhost:5000/user_dashboard
- **Admin Dashboard**: http://localhost:5000/admin_portal
- **Station Master Dashboard**: http://localhost:5000/station_master_dashboard

## 🎨 Modern UI Features

### Design Highlights
- ✅ Clean, professional gradient design
- ✅ Smooth animations and transitions
- ✅ Responsive layout (works on mobile)
- ✅ Accessible color contrast
- ✅ Modern card-based interface
- ✅ Frosted glass header effect
- ✅ Interactive button hover effects

### Color Scheme
- **Primary**: Blue gradient (#2563eb → #3b82f6)
- **Success**: Green (#10b981)
- **Danger**: Red (#ef4444)
- **Warning**: Amber (#f59e0b)

## 🐛 Debugging

### Check Browser Console
Press `F12` to open Developer Tools and check the Console tab.

You should see:
```
=== Language Support Initialization ===
✓ Loaded translations for language: en
✓ Total translation keys: 128
✓ Setting up language dropdown
✓ Language dropdown setup complete
=== Initialization Complete ===
```

### If Language Dropdown Doesn't Appear
1. Hard refresh the page: `Ctrl+F5` (Windows) or `Cmd+Shift+R` (Mac)
2. Clear browser cache
3. Check console for JavaScript errors

### If Translations Don't Work
1. Check console logs for errors
2. Verify you're on a supported page (/, /emergency, /login, etc.)
3. Make sure the page has fully loaded before clicking language button

## 📊 Test Translation System

Run this command to verify all translations are loaded:
```bash
python test_translations.py
```

Expected output:
```
=== Language System Test ===

Available languages:
  en: English 🇬🇧
  hi: हिंदी 🇮🇳
  te: తెలుగు 🇮🇳
  ta: தமிழ் 🇮🇳
  bn: বাংলা 🇮🇳
  ml: മലയാളം 🇮🇳

Telugu translations count: 128
```

## 🎯 Key Features

### For Passengers
- Report medical emergencies during train journey
- Track emergency status
- Get location-based assistance
- Multi-language support

### For Station Masters
- View emergencies approaching their station
- Real-time emergency notifications
- Station-specific dashboard
- Quick response coordination

### For Admin
- View all emergency reports
- Monitor system-wide status
- Manage stations and hospitals
- Analytics and reporting

## 📱 Mobile Responsive

The application is fully responsive and works on:
- 📱 Mobile phones (320px+)
- 📱 Tablets (768px+)
- 💻 Laptops (1024px+)
- 🖥️ Desktops (1280px+)

## 🆘 Emergency Helpline

**Railway Emergency Number: 139**

Available 24/7 for immediate assistance.

## 📝 Notes

- All pages use the modern professional design
- Language preference is saved in session
- Translations work on all major pages
- System supports 128+ translation keys
- Real-time emergency tracking
- Location-based hospital recommendations

## 🔧 Technical Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **Design**: Modern Professional CSS Framework
- **Languages**: 6 Indian languages + English
- **Features**: Real-time updates, geolocation, responsive design

---

**Need Help?** Check the browser console (F12) for detailed logs and error messages.
