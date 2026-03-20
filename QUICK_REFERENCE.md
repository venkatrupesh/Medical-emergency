# Quick Reference - Emergency Assignment System

## 🚀 Quick Start

### 1. Upgrade Database (ONE TIME ONLY)
```bash
python upgrade_database.py
```

### 2. Start Application
```bash
python app.py
```

### 3. Access URLs
- **Homepage**: http://localhost:5000/
- **Report Emergency**: http://localhost:5000/emergency
- **Admin Login**: http://localhost:5000/admin_login
- **Station Master Login**: http://localhost:5000/station_master_login

## 🔐 Login Credentials

| Role | URL | Username/Code | Password |
|------|-----|---------------|----------|
| **Admin** | /admin_login | admin | admin123 |
| **Station Master** | /station_master_login | NDLS, BCT, MAS, etc. | station123 |
| **Passenger** | /login | (create account) | (your password) |

## 🔄 Complete Workflow

### As Passenger
1. Go to `/emergency`
2. Fill form (name, phone, train, emergency type)
3. Submit
4. Emergency saved with status "Pending"

### As Admin
1. Login at `/admin_login`
2. Go to `/authority_dashboard`
3. See ALL emergencies
4. Click "📤 Assign to [STATION]" button
5. Confirm assignment
6. Emergency now assigned to that station

### As Station Master (NDLS)
1. Login at `/station_master_login` with code: NDLS
2. Go to `/station_master_dashboard`
3. See ONLY emergencies assigned to NDLS
4. Handle the emergency
5. Update status

### As Station Master (BCT)
1. Login at `/station_master_login` with code: BCT
2. Go to `/station_master_dashboard`
3. See ONLY emergencies assigned to BCT
4. Does NOT see NDLS emergencies

## 📊 Visual Indicators

### Admin Dashboard
- **✓ Assigned** (Green Badge) - Emergency assigned to a station
- **Not Assigned** (Yellow Badge) - Needs assignment
- **📤 Assign to [CODE]** (Green Button) - Click to assign
- **✓ Assigned to [CODE]** (Disabled Button) - Already assigned

### Station Master Dashboard
- Shows only emergencies where `assigned_station_code = YOUR_CODE`
- Empty if no emergencies assigned to your station

## 🧪 Test Scenario

### Create Emergency
```
URL: /emergency
Name: Test User
Phone: 9876543210
Train: 12301
Coach: A1
Seat: 23
Emergency: Heart Attack
```

### Admin Assigns to NDLS
```
Login: admin / admin123
Dashboard: /authority_dashboard
Action: Click "📤 Assign to NDLS"
Result: Emergency assigned to New Delhi
```

### NDLS Sees It
```
Login: NDLS / station123
Dashboard: /station_master_dashboard
Result: Emergency appears in list
```

### BCT Does NOT See It
```
Login: BCT / station123
Dashboard: /station_master_dashboard
Result: Emergency does NOT appear
```

## 📁 Key Files

| File | Purpose |
|------|---------|
| `upgrade_database.py` | Add new columns (run once) |
| `app.py` | Backend logic |
| `templates/authority_dashboard_utilitarian.html` | Admin dashboard |
| `templates/station_master_dashboard.html` | Station master dashboard |
| `EMERGENCY_ASSIGNMENT_WORKFLOW.md` | Detailed workflow |
| `IMPLEMENTATION_SUMMARY.md` | Technical details |

## 🔧 Database Columns

### New Columns in `emergency_reports`
- `nearest_station_code` - Auto-calculated
- `nearest_station_name` - Auto-calculated
- `assigned_station_code` - Set by admin
- `assigned_station_name` - Set by admin
- `assigned_by_admin` - Who assigned
- `assigned_at` - When assigned

## 🎯 Key Points

1. **Admin sees ALL emergencies** - Full visibility
2. **Admin assigns to specific station** - One-click assignment
3. **Station master sees ONLY assigned** - Filtered view
4. **No cross-station visibility** - Complete isolation
5. **Audit trail maintained** - Who assigned, when

## ⚡ Quick Commands

```bash
# Upgrade database (first time)
python upgrade_database.py

# Start app
python app.py

# Check database schema
python check_db_schema.py

# Test translations
python test_translations.py
```

## 🆘 Troubleshooting

### Emergency not showing in station master dashboard?
- Check if admin assigned it to that station
- Verify station code matches (NDLS vs ndls)
- Check `assigned_station_code` in database

### Can't assign emergency?
- Verify admin is logged in
- Check if already assigned (button disabled)
- Look for JavaScript errors in console

### Database error?
- Run `python upgrade_database.py`
- Restart the application
- Check if database file exists

## 📞 Support

Check these files for detailed help:
- `EMERGENCY_ASSIGNMENT_WORKFLOW.md` - Complete workflow
- `IMPLEMENTATION_SUMMARY.md` - Technical details
- `QUICK_START_GUIDE.md` - General guide
- `ADMIN_CREDENTIALS.md` - All login credentials

---

**System Ready!** 🚀 Start testing the emergency assignment workflow now!
