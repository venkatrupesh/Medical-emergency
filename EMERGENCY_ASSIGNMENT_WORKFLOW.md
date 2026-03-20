# Emergency Assignment Workflow

## 🔄 How It Works

### Step 1: User Reports Emergency
1. Passenger goes to: http://localhost:5000/emergency
2. Fills out the emergency form:
   - Passenger Name
   - Phone Number
   - Train Number
   - Coach & Seat
   - Emergency Type
   - Description
   - Location (optional)
3. Submits the report
4. Emergency is saved with status: **"Pending"**

### Step 2: Admin Views All Emergencies
1. Admin logs in at: http://localhost:5000/admin_login
   - Username: `admin`
   - Password: `admin123`
2. Goes to Admin Dashboard: http://localhost:5000/authority_dashboard
3. Sees **ALL emergency reports** from all trains
4. For each emergency, the system shows:
   - Passenger details
   - Train information
   - Emergency type
   - **Nearest Station** (automatically calculated)
   - **Assigned To** status (Not Assigned / Assigned to Station)

### Step 3: Admin Assigns Emergency to Station Master
1. Admin reviews the emergency details
2. System automatically suggests the **nearest station** based on train location
3. Admin clicks: **"📤 Assign to [STATION_CODE]"** button
4. Confirmation dialog appears:
   ```
   Assign this emergency to New Delhi (NDLS)?
   
   Train: 12301
   Passenger: John Doe
   Emergency: heart_attack
   ETA: 45 minutes
   
   This emergency will appear ONLY in New Delhi Station Master's dashboard.
   ```
5. Admin confirms the assignment
6. System updates the database:
   - `assigned_station_code` = NDLS
   - `assigned_station_name` = New Delhi
   - `assigned_by_admin` = admin
   - `assigned_at` = current timestamp

### Step 4: Station Master Sees Assigned Emergency
1. Station Master logs in at: http://localhost:5000/station_master_login
   - Station Code: `NDLS` (or any assigned station)
   - Password: `station123`
2. Goes to Station Master Dashboard: http://localhost:5000/station_master_dashboard
3. Sees **ONLY emergencies assigned to their station**
4. Other station masters **DO NOT** see this emergency
5. Station Master can:
   - View passenger details
   - See train information
   - Contact passenger via phone
   - Arrange medical team
   - Update emergency status

## 🎯 Key Features

### ✅ Station-Specific Routing
- Each emergency is assigned to **ONE specific station**
- Only that station master sees the emergency
- Other stations don't see unrelated emergencies
- Reduces clutter and confusion

### ✅ Admin Control
- Admin has full visibility of all emergencies
- Admin decides which station handles each emergency
- Admin can see assignment status at a glance
- Admin can track which emergencies are assigned vs. not assigned

### ✅ Visual Indicators
In the Admin Dashboard:
- **Green Badge "✓ Assigned"** - Emergency is assigned to a station
- **Yellow Badge "Not Assigned"** - Emergency needs assignment
- **Disabled Button** - Shows which station it's assigned to
- **Active Button** - Ready to assign to nearest station

### ✅ Database Tracking
New fields in `emergency_reports` table:
- `nearest_station_code` - Automatically calculated nearest station
- `nearest_station_name` - Name of nearest station
- `assigned_station_code` - Station code where emergency is assigned
- `assigned_station_name` - Station name where emergency is assigned
- `assigned_by_admin` - Which admin assigned it
- `assigned_at` - Timestamp of assignment

## 📊 Example Scenario

### Scenario: Heart Attack on Train 12301

1. **Passenger Reports** (10:00 AM)
   - Train: 12301 (Howrah Rajdhani)
   - Emergency: Heart Attack
   - Location: Between Kanpur and Allahabad

2. **Admin Reviews** (10:02 AM)
   - Logs into admin dashboard
   - Sees new emergency report
   - System calculates nearest station: **Allahabad Junction (PRYJ)**
   - ETA: 35 minutes

3. **Admin Assigns** (10:03 AM)
   - Clicks "📤 Assign to PRYJ"
   - Confirms assignment
   - Emergency now assigned to Allahabad Junction

4. **Station Master at Allahabad** (10:04 AM)
   - Logs into dashboard
   - Sees the emergency in their list
   - Contacts passenger: +91-9876543210
   - Arranges medical team at platform
   - Coordinates with ambulance service

5. **Station Master at Delhi** (10:04 AM)
   - Logs into dashboard
   - **Does NOT see** this emergency
   - Only sees emergencies assigned to Delhi

6. **Station Master at Mumbai** (10:04 AM)
   - Logs into dashboard
   - **Does NOT see** this emergency
   - Only sees emergencies assigned to Mumbai

## 🔧 Technical Implementation

### Database Schema
```sql
ALTER TABLE emergency_reports ADD COLUMN nearest_station_code TEXT;
ALTER TABLE emergency_reports ADD COLUMN nearest_station_name TEXT;
ALTER TABLE emergency_reports ADD COLUMN assigned_station_code TEXT;
ALTER TABLE emergency_reports ADD COLUMN assigned_station_name TEXT;
ALTER TABLE emergency_reports ADD COLUMN assigned_by_admin TEXT;
ALTER TABLE emergency_reports ADD COLUMN assigned_at DATETIME;
```

### API Endpoint
```python
POST /assign_emergency
{
    "emergency_id": 123,
    "station_code": "NDLS",
    "station_name": "New Delhi"
}
```

### Station Master Query
```sql
SELECT * FROM emergency_reports 
WHERE assigned_station_code = 'NDLS' 
ORDER BY timestamp DESC
```

## 🧪 Testing the Workflow

### Test 1: Create Emergency
```bash
1. Go to: http://localhost:5000/emergency
2. Fill form with test data
3. Submit emergency
```

### Test 2: Admin Assigns to NDLS
```bash
1. Login as admin: http://localhost:5000/admin_login
2. Go to dashboard: http://localhost:5000/authority_dashboard
3. Find the emergency in the table
4. Click "📤 Assign to NDLS" button
5. Confirm assignment
6. Verify "✓ Assigned" badge appears
```

### Test 3: NDLS Station Master Sees It
```bash
1. Login as NDLS: http://localhost:5000/station_master_login
   - Station Code: NDLS
   - Password: station123
2. Go to dashboard: http://localhost:5000/station_master_dashboard
3. Verify emergency appears in the list
```

### Test 4: BCT Station Master Does NOT See It
```bash
1. Login as BCT: http://localhost:5000/station_master_login
   - Station Code: BCT
   - Password: station123
2. Go to dashboard: http://localhost:5000/station_master_dashboard
3. Verify emergency DOES NOT appear (only BCT-assigned emergencies show)
```

## 📝 Benefits

### For Admin
- ✅ Full visibility of all emergencies
- ✅ Control over emergency routing
- ✅ Clear assignment status
- ✅ Audit trail (who assigned, when)

### For Station Masters
- ✅ See only relevant emergencies
- ✅ No clutter from other stations
- ✅ Focus on their jurisdiction
- ✅ Better response coordination

### For Passengers
- ✅ Emergency reaches right station
- ✅ Faster response time
- ✅ Proper medical coordination
- ✅ Clear accountability

## 🔄 Workflow Diagram

```
Passenger Reports Emergency
         ↓
    Saved in Database
         ↓
    Admin Dashboard (sees ALL)
         ↓
    Admin Reviews & Assigns
         ↓
    Assigned to Specific Station
         ↓
    ┌─────────────────────────────┐
    ↓                             ↓
NDLS Dashboard              BCT Dashboard
(sees NDLS only)           (sees BCT only)
    ↓                             ↓
NDLS handles               BCT handles
NDLS emergencies          BCT emergencies
```

## 🚀 Next Steps

1. **Run database upgrade**:
   ```bash
   python upgrade_database.py
   ```

2. **Start the application**:
   ```bash
   python app.py
   ```

3. **Test the workflow**:
   - Create emergency as passenger
   - Assign as admin
   - View as station master

4. **Verify isolation**:
   - Login as different station masters
   - Confirm they only see their assigned emergencies

---

**System Status**: ✅ Fully Implemented and Ready to Test!
