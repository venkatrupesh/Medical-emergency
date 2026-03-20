# Admin & Station Master Credentials

## 🔐 Admin Login

### Access URL:
```
http://localhost:5000/admin_login
```

### Credentials:
- **Username:** `admin`
- **Password:** `admin123`

### Admin Features:
- ✅ View all emergency reports system-wide
- ✅ Real-time train tracking
- ✅ Nearest station finder with hospitals
- ✅ Status management (Pending → In Progress → Resolved)
- ✅ Medical response coordination
- ✅ Live statistics dashboard
- ✅ Hospital network access (100+ hospitals)

---

## 🚉 Station Master Login

### Access URL:
```
http://localhost:5000/station_master_login
```

### Credentials:
- **Station Code:** Any valid station code (see list below)
- **Password:** `station123` (same for all stations)

### Valid Station Codes:

#### Major Stations:
- **NDLS** - New Delhi
- **BCT** - Mumbai Central
- **CSMT** - Mumbai CST
- **MAS** - Chennai Central
- **HWH** - Howrah Junction
- **SBC** - Bangalore City Junction
- **SC** - Secunderabad Junction

#### North Indian Stations:
- **CNB** - Kanpur Central
- **PRYJ** - Allahabad Junction
- **BSB** - Varanasi Junction
- **PNBE** - Patna Junction
- **LJN** - Lucknow Junction
- **AGC** - Agra Cantonment
- **JHS** - Jhansi Junction
- **GWL** - Gwalior Junction

#### Western Stations:
- **ADI** - Ahmedabad Junction
- **BRC** - Vadodara Junction
- **ST** - Surat
- **PUNE** - Pune Junction
- **KOTA** - Kota Junction
- **JP** - Jaipur Junction

#### South Indian Stations:
- **ERS** - Ernakulam Junction
- **TVC** - Trivandrum Central
- **MDU** - Madurai Junction
- **CBE** - Coimbatore Junction
- **BZA** - Vijayawada Junction
- **VSKP** - Visakhapatnam Junction
- **TPTY** - Tirupati
- **CTO** - Chittoor

#### Eastern Stations:
- **BBS** - Bhubaneswar
- **PURI** - Puri
- **KGP** - Kharagpur Junction
- **ASN** - Asansol Junction
- **SDAH** - Sealdah

#### Central Indian Stations:
- **BPL** - Bhopal Junction
- **NGP** - Nagpur Junction
- **ET** - Itarsi Junction
- **R** - Raipur Junction
- **BSP** - Bilaspur Junction

#### Additional Stations:
- **GKP** - Gorakhpur Junction
- **DDN** - Dehradun
- **HW** - Haridwar Junction
- **ASR** - Amritsar Junction
- **CDG** - Chandigarh
- **KLK** - Kalka

### Station Master Features:
- ✅ View emergencies approaching their station
- ✅ Real-time emergency notifications
- ✅ Station-specific dashboard
- ✅ Quick response coordination
- ✅ Hospital contact information
- ✅ Medical facility status

---

## 👤 Passenger Login

### Access URL:
```
http://localhost:5000/login
```

### How to Create Account:
1. Go to: http://localhost:5000/signup
2. Fill in:
   - Username
   - Email
   - Password
   - Phone Number
3. Click "Sign Up"
4. Login with your credentials

### Passenger Features:
- ✅ Report medical emergencies
- ✅ Track emergency status
- ✅ View personal dashboard
- ✅ Location-based assistance
- ✅ Multi-language support

---

## 🧪 Testing Examples

### Test as Admin:
```
1. Go to: http://localhost:5000/admin_login
2. Username: admin
3. Password: admin123
4. Click Login
5. Access Admin Dashboard
```

### Test as Station Master (New Delhi):
```
1. Go to: http://localhost:5000/station_master_login
2. Station Code: NDLS
3. Password: station123
4. Click Login
5. View emergencies approaching New Delhi station
```

### Test as Station Master (Mumbai):
```
1. Go to: http://localhost:5000/station_master_login
2. Station Code: BCT
3. Password: station123
4. Click Login
5. View emergencies approaching Mumbai Central station
```

### Test as Station Master (Chennai):
```
1. Go to: http://localhost:5000/station_master_login
2. Station Code: MAS
3. Password: station123
4. Click Login
5. View emergencies approaching Chennai Central station
```

---

## 🔒 Security Notes

⚠️ **Important:** These are demo credentials for development/testing only.

### For Production:
1. **Change all default passwords**
2. **Use environment variables** for credentials
3. **Implement proper password hashing** (bcrypt, argon2)
4. **Add role-based access control** (RBAC)
5. **Enable two-factor authentication** (2FA)
6. **Use HTTPS** for all connections
7. **Implement rate limiting** on login endpoints
8. **Add session timeout** mechanisms
9. **Log all authentication attempts**
10. **Regular security audits**

---

## 📝 Quick Reference

| Role | URL | Username/Code | Password |
|------|-----|---------------|----------|
| Admin | /admin_login | admin | admin123 |
| Station Master | /station_master_login | NDLS (or any station code) | station123 |
| Passenger | /login | (create account) | (your password) |

---

**Built for Railway Safety** 🚂❤️
