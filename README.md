# Railway Passenger Health Emergency Assistance System

A web-based emergency assistance system that connects train passengers with railway authorities for immediate medical help during their journey.

## 🎯 Objective
Reduce in-train medical deaths by 50% through quick emergency reporting and response coordination.

## 🚀 Features
- **Emergency Reporting**: Passengers can quickly report health emergencies
- **Location Tracking**: Automatic location capture for precise assistance
- **Real-time Dashboard**: Railway authorities can monitor and respond to emergencies
- **Status Tracking**: Track emergency resolution progress
- **Mobile Responsive**: Works on all devices

## 🛠️ Tech Stack
- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Flask (Python)
- **Database**: SQLite

## 📋 Setup Instructions

1. **Install Python** (3.7 or higher)

2. **Install Dependencies**:
   ```bash
   pip install Flask
   ```

3. **Run the Application**:
   ```bash
   python app.py
   ```

4. **Access the System**:
   - Open your browser and go to: `http://localhost:5000`

## 🚨 How to Use

### For Passengers:
1. Visit the website
2. Click "Report Emergency"
3. Fill in your details and emergency information
4. Allow location access for precise help
5. Submit the report
6. Help will be dispatched to the nearest station

### For Railway Authorities:
1. Access the Dashboard
2. Monitor incoming emergency reports
3. Update status as you respond
4. Coordinate with nearby stations for medical assistance

## 📱 Emergency Types Supported
- Heart Attack
- Breathing Difficulty
- Severe Pain
- Unconscious
- Injury/Accident
- High Fever
- Other medical emergencies

## 🔧 System Architecture
```
Frontend (HTML/CSS/JS) → Flask Backend → SQLite Database
                     ↓
              Emergency Reports Storage
                     ↓
           Railway Authority Dashboard
```

## 📊 Expected Impact
- **50% reduction** in medical emergency response time
- **Immediate notification** to railway authorities
- **Location-based assistance** from nearest stations
- **Real-time tracking** of emergency status

## 🚀 Future Enhancements
- SMS/Email notifications
- Integration with hospital networks
- Mobile app development
- AI-powered emergency classification
- Multi-language support

## 📞 Emergency Contact Integration
The system includes pre-configured railway station contacts for immediate assistance coordination.

---
**Built to save lives on rails** 🚂❤️