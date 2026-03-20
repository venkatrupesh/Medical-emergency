from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import sqlite3
from datetime import datetime
import os
import requests
import json
import math
import hashlib
from languages import TRANSLATIONS, LANGUAGES, get_translation, get_available_languages

app = Flask(__name__)
app.secret_key = 'railway_emergency_secret_key_2024'

# Add tojson filter for templates
@app.template_filter('tojson')
def tojson_filter(obj):
    return json.dumps(obj)

# Database setup
def init_db():
    conn = sqlite3.connect('emergency_reports.db')
    cursor = conn.cursor()
    
    # Check if tables exist, if not create them
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='emergency_reports'")
    if not cursor.fetchone():
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emergency_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                passenger_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                train_number TEXT NOT NULL,
                coach TEXT NOT NULL,
                seat TEXT NOT NULL,
                emergency_type TEXT NOT NULL,
                description TEXT NOT NULL,
                location TEXT,
                status TEXT DEFAULT 'pending',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                station_name TEXT NOT NULL,
                station_code TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                contact_number TEXT NOT NULL,
                medical_facility TEXT DEFAULT 'available',
                station_manager_name TEXT,
                station_manager_phone TEXT,
                hospitals_nearby TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hospitals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hospital_name TEXT NOT NULL,
                station_code TEXT NOT NULL,
                distance_from_station REAL NOT NULL,
                contact_number TEXT NOT NULL,
                specialties TEXT NOT NULL,
                emergency_available TEXT DEFAULT 'yes',
                ambulance_available TEXT DEFAULT 'yes',
                latitude REAL,
                longitude REAL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS train_locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                train_number TEXT NOT NULL,
                train_name TEXT NOT NULL,
                current_latitude REAL,
                current_longitude REAL,
                last_station TEXT,
                next_station TEXT,
                speed REAL DEFAULT 0,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS train_database (
                train_number TEXT PRIMARY KEY,
                train_name TEXT NOT NULL,
                source_station TEXT NOT NULL,
                destination_station TEXT NOT NULL,
                route_stations TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                phone TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    # Insert comprehensive train data with 100+ trains
    train_data = [
        # Rajdhani Trains
        ('12301', 'Howrah Rajdhani Express', 'New Delhi', 'Howrah', 'New Delhi,Kanpur Central,Allahabad Junction,Varanasi Junction,Patna Junction,Howrah Junction'),
        ('12302', 'Howrah Rajdhani Express', 'Howrah', 'New Delhi', 'Howrah Junction,Patna Junction,Varanasi Junction,Allahabad Junction,Kanpur Central,New Delhi'),
        ('12951', 'Mumbai Rajdhani Express', 'New Delhi', 'Mumbai Central', 'New Delhi,Kota Junction,Vadodara Junction,Mumbai Central'),
        ('12952', 'Mumbai Rajdhani Express', 'Mumbai Central', 'New Delhi', 'Mumbai Central,Vadodara Junction,Kota Junction,New Delhi'),
        ('12423', 'Dibrugarh Rajdhani Express', 'New Delhi', 'Dibrugarh', 'New Delhi,Ghaziabad,Lucknow,Gonda Junction,Gorakhpur,Dibrugarh'),
        ('12424', 'Dibrugarh Rajdhani Express', 'Dibrugarh', 'New Delhi', 'Dibrugarh,Gorakhpur,Gonda Junction,Lucknow,Ghaziabad,New Delhi'),
        ('12431', 'Trivandrum Rajdhani Express', 'New Delhi', 'Trivandrum Central', 'New Delhi,Kota Junction,Mumbai Central,Ernakulam Junction,Trivandrum Central'),
        ('12432', 'Trivandrum Rajdhani Express', 'Trivandrum Central', 'New Delhi', 'Trivandrum Central,Ernakulam Junction,Mumbai Central,Kota Junction,New Delhi'),
        ('12953', 'August Kranti Rajdhani Express', 'New Delhi', 'Mumbai Central', 'New Delhi,Mathura Junction,Kota Junction,Ratlam Junction,Vadodara Junction,Mumbai Central'),
        ('12954', 'August Kranti Rajdhani Express', 'Mumbai Central', 'New Delhi', 'Mumbai Central,Vadodara Junction,Ratlam Junction,Kota Junction,Mathura Junction,New Delhi'),
        
        # Shatabdi Trains
        ('12001', 'Bhopal Shatabdi Express', 'New Delhi', 'Bhopal Junction', 'New Delhi,Gwalior Junction,Jhansi Junction,Bhopal Junction'),
        ('12002', 'Bhopal Shatabdi Express', 'Bhopal Junction', 'New Delhi', 'Bhopal Junction,Jhansi Junction,Gwalior Junction,New Delhi'),
        ('12009', 'Amritsar Shatabdi Express', 'New Delhi', 'Amritsar Junction', 'New Delhi,Ambala Cantonment,Ludhiana Junction,Amritsar Junction'),
        ('12010', 'Amritsar Shatabdi Express', 'Amritsar Junction', 'New Delhi', 'Amritsar Junction,Ludhiana Junction,Ambala Cantonment,New Delhi'),
        ('12017', 'Dehradun Shatabdi Express', 'New Delhi', 'Dehradun', 'New Delhi,Saharanpur Junction,Roorkee,Haridwar Junction,Dehradun'),
        ('12018', 'Dehradun Shatabdi Express', 'Dehradun', 'New Delhi', 'Dehradun,Haridwar Junction,Roorkee,Saharanpur Junction,New Delhi'),
        ('12025', 'Kalka Shatabdi Express', 'New Delhi', 'Kalka', 'New Delhi,Ambala Cantonment,Chandigarh,Kalka'),
        ('12026', 'Kalka Shatabdi Express', 'Kalka', 'New Delhi', 'Kalka,Chandigarh,Ambala Cantonment,New Delhi'),
        ('12027', 'Chennai Shatabdi Express', 'Chennai Central', 'Mysore Junction', 'Chennai Central,Katpadi Junction,Bangalore City Junction,Mysore Junction'),
        ('12028', 'Chennai Shatabdi Express', 'Mysore Junction', 'Chennai Central', 'Mysore Junction,Bangalore City Junction,Katpadi Junction,Chennai Central'),
        
        # Duronto Trains
        ('12213', 'Ypr Duronto Express', 'New Delhi', 'Yesvantpur Junction', 'New Delhi,Kota Junction,Nagpur Junction,Bangalore City Junction,Yesvantpur Junction'),
        ('12214', 'Ypr Duronto Express', 'Yesvantpur Junction', 'New Delhi', 'Yesvantpur Junction,Bangalore City Junction,Nagpur Junction,Kota Junction,New Delhi'),
        ('12259', 'Sealdah Duronto Express', 'New Delhi', 'Sealdah', 'New Delhi,Kanpur Central,Allahabad Junction,Asansol Junction,Sealdah'),
        ('12260', 'Sealdah Duronto Express', 'Sealdah', 'New Delhi', 'Sealdah,Asansol Junction,Allahabad Junction,Kanpur Central,New Delhi'),
        ('12269', 'Chennai Duronto Express', 'New Delhi', 'Chennai Central', 'New Delhi,Jhansi Junction,Bhopal Junction,Nagpur Junction,Vijayawada Junction,Chennai Central'),
        ('12270', 'Chennai Duronto Express', 'Chennai Central', 'New Delhi', 'Chennai Central,Vijayawada Junction,Nagpur Junction,Bhopal Junction,Jhansi Junction,New Delhi'),
        
        # Popular Express Trains
        ('12621', 'Tamil Nadu Express', 'New Delhi', 'Chennai Central', 'New Delhi,Mathura Junction,Agra Cantonment,Jhansi Junction,Bhopal Junction,Nagpur Junction,Balharshah,Vijayawada Junction,Chennai Central'),
        ('12622', 'Tamil Nadu Express', 'Chennai Central', 'New Delhi', 'Chennai Central,Vijayawada Junction,Balharshah,Nagpur Junction,Bhopal Junction,Jhansi Junction,Agra Cantonment,Mathura Junction,New Delhi'),
        ('12615', 'Grand Trunk Express', 'New Delhi', 'Chennai Central', 'New Delhi,Agra Cantonment,Jhansi Junction,Bhopal Junction,Itarsi Junction,Nagpur Junction,Chennai Central'),
        ('12616', 'Grand Trunk Express', 'Chennai Central', 'New Delhi', 'Chennai Central,Nagpur Junction,Itarsi Junction,Bhopal Junction,Jhansi Junction,Agra Cantonment,New Delhi'),
        ('12650', 'Karnataka Express', 'New Delhi', 'Bangalore City Junction', 'New Delhi,Mathura Junction,Agra Cantonment,Jhansi Junction,Bhopal Junction,Kacheguda,Bangalore City Junction'),
        ('12649', 'Karnataka Express', 'Bangalore City Junction', 'New Delhi', 'Bangalore City Junction,Kacheguda,Bhopal Junction,Jhansi Junction,Agra Cantonment,Mathura Junction,New Delhi'),
        ('12780', 'Goa Express', 'New Delhi', 'Vasco Da Gama', 'New Delhi,Kota Junction,Ratlam Junction,Vadodara Junction,Pune Junction,Vasco Da Gama'),
        ('12779', 'Goa Express', 'Vasco Da Gama', 'New Delhi', 'Vasco Da Gama,Pune Junction,Vadodara Junction,Ratlam Junction,Kota Junction,New Delhi'),
        
        # Regional Trains
        ('12797', 'Venkatadri Express', 'Secunderabad Junction', 'Tirupati', 'Secunderabad Junction,Kacheguda,Mahabubnagar,Kurnool City,Anantapur,Tirupati'),
        ('12798', 'Venkatadri Express', 'Tirupati', 'Secunderabad Junction', 'Tirupati,Anantapur,Kurnool City,Mahabubnagar,Kacheguda,Secunderabad Junction'),
        ('18047', 'Amaravathi Express', 'Howrah Junction', 'Amaravathi', 'Howrah Junction,Bhubaneswar,Visakhapatnam Junction,Vijayawada Junction,Amaravathi'),
        ('18048', 'Amaravathi Express', 'Amaravathi', 'Howrah Junction', 'Amaravathi,Vijayawada Junction,Visakhapatnam Junction,Bhubaneswar,Howrah Junction'),
        ('12295', 'Sanghamitra Express', 'Bangalore City Junction', 'Patna Junction', 'Bangalore City Junction,Kacheguda,Nagpur Junction,Itarsi Junction,Allahabad Junction,Patna Junction'),
        ('12296', 'Sanghamitra Express', 'Patna Junction', 'Bangalore City Junction', 'Patna Junction,Allahabad Junction,Itarsi Junction,Nagpur Junction,Kacheguda,Bangalore City Junction'),
        ('12807', 'Samta Express', 'New Delhi', 'Darbhanga Junction', 'New Delhi,Kanpur Central,Lucknow Junction,Gorakhpur Junction,Muzaffarpur Junction,Darbhanga Junction'),
        ('12808', 'Samta Express', 'Darbhanga Junction', 'New Delhi', 'Darbhanga Junction,Muzaffarpur Junction,Gorakhpur Junction,Lucknow Junction,Kanpur Central,New Delhi'),
        
        # Mumbai Trains
        ('12137', 'Punjab Mail', 'Mumbai CST', 'Firozpur Cantonment', 'Mumbai CST,Kalyan Junction,Nashik Road,Manmad Junction,Jalgaon Junction,Kota Junction,New Delhi,Ambala Cantonment,Firozpur Cantonment'),
        ('12138', 'Punjab Mail', 'Firozpur Cantonment', 'Mumbai CST', 'Firozpur Cantonment,Ambala Cantonment,New Delhi,Kota Junction,Jalgaon Junction,Manmad Junction,Nashik Road,Kalyan Junction,Mumbai CST'),
        ('12617', 'Mangala Express', 'New Delhi', 'Ernakulam Junction', 'New Delhi,Kota Junction,Vadodara Junction,Mumbai Central,Pune Junction,Ernakulam Junction'),
        ('12618', 'Mangala Express', 'Ernakulam Junction', 'New Delhi', 'Ernakulam Junction,Pune Junction,Mumbai Central,Vadodara Junction,Kota Junction,New Delhi'),
        ('12701', 'Hussainsagar Express', 'Mumbai CST', 'Hyderabad Deccan', 'Mumbai CST,Pune Junction,Solapur Junction,Gulbarga,Secunderabad Junction,Hyderabad Deccan'),
        ('12702', 'Hussainsagar Express', 'Hyderabad Deccan', 'Mumbai CST', 'Hyderabad Deccan,Secunderabad Junction,Gulbarga,Solapur Junction,Pune Junction,Mumbai CST'),
        
        # South Indian Trains
        ('12639', 'Brindavan Express', 'Chennai Central', 'Bangalore City Junction', 'Chennai Central,Katpadi Junction,Jolarpettai Junction,Bangalore City Junction'),
        ('12640', 'Brindavan Express', 'Bangalore City Junction', 'Chennai Central', 'Bangalore City Junction,Jolarpettai Junction,Katpadi Junction,Chennai Central'),
        ('12677', 'Ernakulam Express', 'Chennai Central', 'Ernakulam Junction', 'Chennai Central,Villupuram Junction,Trichy Junction,Madurai Junction,Ernakulam Junction'),
        ('12678', 'Ernakulam Express', 'Ernakulam Junction', 'Chennai Central', 'Ernakulam Junction,Madurai Junction,Trichy Junction,Villupuram Junction,Chennai Central'),
        ('16525', 'Island Express', 'Bangalore City Junction', 'Kanyakumari', 'Bangalore City Junction,Salem Junction,Madurai Junction,Tirunelveli Junction,Kanyakumari'),
        ('16526', 'Island Express', 'Kanyakumari', 'Bangalore City Junction', 'Kanyakumari,Tirunelveli Junction,Madurai Junction,Salem Junction,Bangalore City Junction'),
        ('12635', 'Vaigai Express', 'Chennai Central', 'Madurai Junction', 'Chennai Central,Villupuram Junction,Trichy Junction,Dindigul Junction,Madurai Junction'),
        ('12636', 'Vaigai Express', 'Madurai Junction', 'Chennai Central', 'Madurai Junction,Dindigul Junction,Trichy Junction,Villupuram Junction,Chennai Central'),
        
        # Eastern Trains
        ('12841', 'Coromandel Express', 'Howrah Junction', 'Chennai Central', 'Howrah Junction,Kharagpur Junction,Bhubaneswar,Visakhapatnam Junction,Vijayawada Junction,Chennai Central'),
        ('12842', 'Coromandel Express', 'Chennai Central', 'Howrah Junction', 'Chennai Central,Vijayawada Junction,Visakhapatnam Junction,Bhubaneswar,Kharagpur Junction,Howrah Junction'),
        ('12859', 'Gitanjali Express', 'Mumbai CST', 'Howrah Junction', 'Mumbai CST,Nagpur Junction,Raipur Junction,Bilaspur Junction,Howrah Junction'),
        ('12860', 'Gitanjali Express', 'Howrah Junction', 'Mumbai CST', 'Howrah Junction,Bilaspur Junction,Raipur Junction,Nagpur Junction,Mumbai CST'),
        ('12875', 'Neelachal Express', 'New Delhi', 'Puri', 'New Delhi,Kanpur Central,Allahabad Junction,Varanasi Junction,Bhubaneswar,Puri'),
        ('12876', 'Neelachal Express', 'Puri', 'New Delhi', 'Puri,Bhubaneswar,Varanasi Junction,Allahabad Junction,Kanpur Central,New Delhi'),
        ('12019', 'Shatabdi Express', 'New Delhi', 'Bhopal Junction', 'New Delhi,Gwalior Junction,Jhansi Junction,Bhopal Junction'),
        ('12020', 'Shatabdi Express', 'Bhopal Junction', 'New Delhi', 'Bhopal Junction,Jhansi Junction,Gwalior Junction,New Delhi'),
        
        # Western Trains
        ('12009', 'Shatabdi Express', 'Mumbai Central', 'Ahmedabad Junction', 'Mumbai Central,Borivali,Vapi,Surat,Bharuch Junction,Vadodara Junction,Ahmedabad Junction'),
        ('12010', 'Shatabdi Express', 'Ahmedabad Junction', 'Mumbai Central', 'Ahmedabad Junction,Vadodara Junction,Bharuch Junction,Surat,Vapi,Borivali,Mumbai Central'),
        ('12927', 'Vadodara Express', 'Mumbai Central', 'Vadodara Junction', 'Mumbai Central,Borivali,Vapi,Surat,Bharuch Junction,Vadodara Junction'),
        ('12928', 'Vadodara Express', 'Vadodara Junction', 'Mumbai Central', 'Vadodara Junction,Bharuch Junction,Surat,Vapi,Borivali,Mumbai Central'),
        ('19019', 'Dehradun Express', 'Mumbai Bandra Terminus', 'Dehradun', 'Mumbai Bandra Terminus,Kota Junction,Jaipur Junction,Delhi Junction,Saharanpur Junction,Dehradun'),
        ('19020', 'Dehradun Express', 'Dehradun', 'Mumbai Bandra Terminus', 'Dehradun,Saharanpur Junction,Delhi Junction,Jaipur Junction,Kota Junction,Mumbai Bandra Terminus'),
        
        # Additional Popular Trains
        ('12003', 'Lucknow Shatabdi Express', 'New Delhi', 'Lucknow Junction', 'New Delhi,Ghaziabad,Kanpur Central,Lucknow Junction'),
        ('12004', 'Lucknow Shatabdi Express', 'Lucknow Junction', 'New Delhi', 'Lucknow Junction,Kanpur Central,Ghaziabad,New Delhi'),
        ('12011', 'Kalka Shatabdi Express', 'New Delhi', 'Kalka', 'New Delhi,Ambala Cantonment,Chandigarh,Kalka'),
        ('12012', 'Kalka Shatabdi Express', 'Kalka', 'New Delhi', 'Kalka,Chandigarh,Ambala Cantonment,New Delhi'),
        ('12051', 'Jan Shatabdi Express', 'New Delhi', 'Kathgodam', 'New Delhi,Ghaziabad,Moradabad,Rampur,Kathgodam'),
        ('12052', 'Jan Shatabdi Express', 'Kathgodam', 'New Delhi', 'Kathgodam,Rampur,Moradabad,Ghaziabad,New Delhi'),
        ('12263', 'Pune Duronto Express', 'New Delhi', 'Pune Junction', 'New Delhi,Kota Junction,Ratlam Junction,Vadodara Junction,Pune Junction'),
        ('12264', 'Pune Duronto Express', 'Pune Junction', 'New Delhi', 'Pune Junction,Vadodara Junction,Ratlam Junction,Kota Junction,New Delhi'),
        ('12273', 'Howrah Duronto Express', 'New Delhi', 'Howrah Junction', 'New Delhi,Kanpur Central,Allahabad Junction,Varanasi Junction,Howrah Junction'),
        ('12274', 'Howrah Duronto Express', 'Howrah Junction', 'New Delhi', 'Howrah Junction,Varanasi Junction,Allahabad Junction,Kanpur Central,New Delhi'),
        
        # Superfast Trains
        ('12313', 'Sealdah Rajdhani Express', 'New Delhi', 'Sealdah', 'New Delhi,Kanpur Central,Allahabad Junction,Malda Town,Sealdah'),
        ('12314', 'Sealdah Rajdhani Express', 'Sealdah', 'New Delhi', 'Sealdah,Malda Town,Allahabad Junction,Kanpur Central,New Delhi'),
        ('12381', 'Poorva Express', 'New Delhi', 'Howrah Junction', 'New Delhi,Kanpur Central,Allahabad Junction,Varanasi Junction,Patna Junction,Howrah Junction'),
        ('12382', 'Poorva Express', 'Howrah Junction', 'New Delhi', 'Howrah Junction,Patna Junction,Varanasi Junction,Allahabad Junction,Kanpur Central,New Delhi'),
        ('12555', 'Gorakhdham Express', 'New Delhi', 'Gorakhpur Junction', 'New Delhi,Ghaziabad,Lucknow Junction,Faizabad Junction,Gorakhpur Junction'),
        ('12556', 'Gorakhdham Express', 'Gorakhpur Junction', 'New Delhi', 'Gorakhpur Junction,Faizabad Junction,Lucknow Junction,Ghaziabad,New Delhi'),
        ('12801', 'Purushottam Express', 'New Delhi', 'Puri', 'New Delhi,Kanpur Central,Allahabad Junction,Varanasi Junction,Bhubaneswar,Puri'),
        ('12802', 'Purushottam Express', 'Puri', 'New Delhi', 'Puri,Bhubaneswar,Varanasi Junction,Allahabad Junction,Kanpur Central,New Delhi'),
        
        # Mail Trains
        ('12903', 'Golden Temple Mail', 'Mumbai Central', 'Amritsar Junction', 'Mumbai Central,Vadodara Junction,Kota Junction,New Delhi,Ambala Cantonment,Amritsar Junction'),
        ('12904', 'Golden Temple Mail', 'Amritsar Junction', 'Mumbai Central', 'Amritsar Junction,Ambala Cantonment,New Delhi,Kota Junction,Vadodara Junction,Mumbai Central'),
        ('12925', 'Paschim Express', 'Mumbai Central', 'Amritsar Junction', 'Mumbai Central,Vadodara Junction,Ajmer Junction,Jaipur Junction,New Delhi,Amritsar Junction'),
        ('12926', 'Paschim Express', 'Amritsar Junction', 'Mumbai Central', 'Amritsar Junction,New Delhi,Jaipur Junction,Ajmer Junction,Vadodara Junction,Mumbai Central'),
        
        # Intercity Trains
        ('12015', 'Ajmer Shatabdi Express', 'New Delhi', 'Ajmer Junction', 'New Delhi,Jaipur Junction,Ajmer Junction'),
        ('12016', 'Ajmer Shatabdi Express', 'Ajmer Junction', 'New Delhi', 'Ajmer Junction,Jaipur Junction,New Delhi'),
        ('12023', 'Janata Express', 'New Delhi', 'Chandigarh', 'New Delhi,Panipat Junction,Ambala Cantonment,Chandigarh'),
        ('12024', 'Janata Express', 'Chandigarh', 'New Delhi', 'Chandigarh,Ambala Cantonment,Panipat Junction,New Delhi'),
        
        # Special Trains
        ('22691', 'Rajdhani Express', 'New Delhi', 'Bangalore Cantonment', 'New Delhi,Kota Junction,Secunderabad Junction,Bangalore Cantonment'),
        ('22692', 'Rajdhani Express', 'Bangalore Cantonment', 'New Delhi', 'Bangalore Cantonment,Secunderabad Junction,Kota Junction,New Delhi'),
        ('22413', 'Rajdhani Express', 'New Delhi', 'Patna Junction', 'New Delhi,Kanpur Central,Allahabad Junction,Patna Junction'),
        ('22414', 'Rajdhani Express', 'Patna Junction', 'New Delhi', 'Patna Junction,Allahabad Junction,Kanpur Central,New Delhi'),
        
        # Garib Rath Trains
        ('12909', 'Garib Rath Express', 'Mumbai Central', 'Hazrat Nizamuddin', 'Mumbai Central,Vadodara Junction,Kota Junction,Hazrat Nizamuddin'),
        ('12910', 'Garib Rath Express', 'Hazrat Nizamuddin', 'Mumbai Central', 'Hazrat Nizamuddin,Kota Junction,Vadodara Junction,Mumbai Central'),
        ('12917', 'Garib Rath Express', 'Howrah Junction', 'Anand Vihar Terminal', 'Howrah Junction,Asansol Junction,Allahabad Junction,Anand Vihar Terminal'),
        ('12918', 'Garib Rath Express', 'Anand Vihar Terminal', 'Howrah Junction', 'Anand Vihar Terminal,Allahabad Junction,Asansol Junction,Howrah Junction')
    ]
    
    cursor.executemany('INSERT OR IGNORE INTO train_database VALUES (?, ?, ?, ?, ?)', train_data)
    
    # Insert comprehensive station data with coordinates and medical info
    stations_data = [
        # Major Junction Stations
        ('New Delhi', 'NDLS', 28.6448, 77.2097, '+91-11-23340000', 'available', 'Rajesh Kumar', '+91-11-23340001', 'AIIMS Delhi, Safdarjung Hospital, RML Hospital'),
        ('Mumbai Central', 'BCT', 19.0330, 72.8397, '+91-22-22070000', 'available', 'Suresh Patil', '+91-22-22070001', 'KEM Hospital, JJ Hospital, Tata Memorial Hospital'),
        ('Mumbai CST', 'CSMT', 18.9398, 72.8355, '+91-22-22694040', 'available', 'Station Manager', '+91-22-22694041', 'JJ Hospital, GT Hospital'),
        ('Chennai Central', 'MAS', 13.0827, 80.2707, '+91-44-25330000', 'available', 'Ravi Shankar', '+91-44-25330001', 'Government General Hospital, Apollo Hospital, MIOT Hospital'),
        ('Howrah Junction', 'HWH', 22.5726, 88.3639, '+91-33-26382217', 'available', 'Station Manager', '+91-33-26382218', 'Medical College Hospital Kolkata'),
        ('Bangalore City Junction', 'SBC', 12.9716, 77.5946, '+91-80-26700000', 'available', 'Station Manager', '+91-80-26700001', 'Victoria Hospital, Manipal Hospital'),
        ('Secunderabad Junction', 'SC', 17.4399, 78.4983, '+91-40-27020000', 'available', 'Station Manager', '+91-40-27020001', 'Gandhi Hospital, Osmania Hospital'),
        
        # North Indian Stations
        ('Kanpur Central', 'CNB', 26.4499, 80.3319, '+91-512-2323015', 'available', 'Station Manager', '+91-512-2323016', 'GSVM Medical College Kanpur'),
        ('Allahabad Junction', 'PRYJ', 25.4358, 81.8463, '+91-532-2408128', 'available', 'Station Manager', '+91-532-2408129', 'MLN Medical College Allahabad'),
        ('Varanasi Junction', 'BSB', 25.3176, 82.9739, '+91-542-2501072', 'available', 'Station Manager', '+91-542-2501073', 'BHU Hospital, Heritage Hospital'),
        ('Patna Junction', 'PNBE', 25.5941, 85.1376, '+91-612-2675131', 'available', 'Station Manager', '+91-612-2675132', 'AIIMS Patna, PMCH Patna'),
        ('Lucknow Junction', 'LJN', 26.8467, 80.9462, '+91-522-2208000', 'available', 'Station Manager', '+91-522-2208001', 'KGMU Lucknow, Balrampur Hospital'),
        ('Agra Cantonment', 'AGC', 27.1767, 78.0081, '+91-562-2226284', 'available', 'Station Manager', '+91-562-2226285', 'SN Medical College Agra'),
        ('Jhansi Junction', 'JHS', 25.4484, 78.5685, '+91-510-2470131', 'available', 'Station Manager', '+91-510-2470132', 'Medical College Jhansi'),
        ('Gwalior Junction', 'GWL', 26.2183, 78.1828, '+91-751-2423018', 'available', 'Station Manager', '+91-751-2423019', 'Jaya Arogya Hospital Gwalior'),
        
        # Western Stations
        ('Ahmedabad Junction', 'ADI', 23.0225, 72.5714, '+91-79-22140000', 'available', 'Station Manager', '+91-79-22140001', 'Civil Hospital Ahmedabad'),
        ('Vadodara Junction', 'BRC', 22.3072, 73.1812, '+91-265-2427131', 'available', 'Station Manager', '+91-265-2427132', 'SSG Hospital Vadodara'),
        ('Surat', 'ST', 21.1702, 72.8311, '+91-261-2476284', 'available', 'Station Manager', '+91-261-2476285', 'New Civil Hospital Surat'),
        ('Pune Junction', 'PUNE', 18.5204, 73.8567, '+91-20-26120000', 'available', 'Station Manager', '+91-20-26120001', 'Sassoon Hospital, Ruby Hall Clinic'),
        ('Kota Junction', 'KOTA', 25.2138, 75.8648, '+91-744-2450131', 'available', 'Station Manager', '+91-744-2450132', 'MBS Hospital Kota'),
        ('Jaipur Junction', 'JP', 26.9124, 75.7873, '+91-141-2200000', 'available', 'Station Manager', '+91-141-2200001', 'SMS Hospital Jaipur'),
        
        # South Indian Stations
        ('Ernakulam Junction', 'ERS', 9.9312, 76.2673, '+91-484-2375131', 'available', 'Station Manager', '+91-484-2375132', 'Medical Trust Hospital, Lakeshore Hospital'),
        ('Trivandrum Central', 'TVC', 8.5241, 76.9366, '+91-471-2323016', 'available', 'Station Manager', '+91-471-2323017', 'Medical College Hospital Trivandrum'),
        ('Madurai Junction', 'MDU', 9.9252, 78.1198, '+91-452-2537131', 'available', 'Station Manager', '+91-452-2537132', 'Government Rajaji Hospital Madurai'),
        ('Coimbatore Junction', 'CBE', 11.0168, 76.9558, '+91-422-2223018', 'available', 'Station Manager', '+91-422-2223019', 'Coimbatore Medical College Hospital'),
        ('Vijayawada Junction', 'BZA', 16.5062, 80.6480, '+91-866-2571072', 'available', 'Station Manager', '+91-866-2571073', 'Government General Hospital Vijayawada'),
        ('Visakhapatnam Junction', 'VSKP', 17.7231, 83.3219, '+91-891-2746284', 'available', 'Station Manager', '+91-891-2746285', 'King George Hospital, GITAM Hospital'),
        ('Tirupati', 'TPTY', 13.6288, 79.4192, '+91-877-2287000', 'available', 'Venkat Reddy', '+91-877-2287001', 'SVIMS Hospital, Ruia Hospital, Sri Venkateswara Hospital'),
        ('Chittoor', 'CTO', 13.2172, 79.1003, '+91-8572-248000', 'available', 'Mohan Krishna', '+91-8572-248001', 'Government Hospital Chittoor, Apollo Reach Hospital, Narayana Hospital'),
        
        # Eastern Stations
        ('Bhubaneswar', 'BBS', 20.2961, 85.8245, '+91-674-2303018', 'available', 'Station Manager', '+91-674-2303019', 'AIIMS Bhubaneswar, Capital Hospital'),
        ('Puri', 'PURI', 19.8135, 85.8312, '+91-6752-222644', 'available', 'Station Manager', '+91-6752-222645', 'District Headquarters Hospital Puri'),
        ('Kharagpur Junction', 'KGP', 22.3460, 87.3200, '+91-3222-255131', 'available', 'Station Manager', '+91-3222-255132', 'IIT Kharagpur Hospital'),
        ('Asansol Junction', 'ASN', 23.6739, 86.9524, '+91-341-2550131', 'available', 'Station Manager', '+91-341-2550132', 'Asansol District Hospital'),
        ('Sealdah', 'SDAH', 22.5697, 88.3697, '+91-33-22350131', 'available', 'Station Manager', '+91-33-22350132', 'NRS Medical College'),
        
        # Central Indian Stations
        ('Bhopal Junction', 'BPL', 23.2599, 77.4126, '+91-755-2746284', 'available', 'Station Manager', '+91-755-2746285', 'AIIMS Bhopal, Hamidia Hospital'),
        ('Nagpur Junction', 'NGP', 21.1458, 79.0882, '+91-712-2746284', 'available', 'Station Manager', '+91-712-2746285', 'AIIMS Nagpur, Orange City Hospital'),
        ('Itarsi Junction', 'ET', 22.6173, 77.7640, '+91-7574-252644', 'available', 'Station Manager', '+91-7574-252645', 'District Hospital Itarsi'),
        ('Raipur Junction', 'R', 21.2514, 81.6296, '+91-771-2746284', 'available', 'Station Manager', '+91-771-2746285', 'Dr. Bhimrao Ambedkar Hospital'),
        ('Bilaspur Junction', 'BSP', 22.0797, 82.1409, '+91-7752-222644', 'available', 'Station Manager', '+91-7752-222645', 'CIMS Hospital'),
        
        # Additional Important Stations
        ('Gorakhpur Junction', 'GKP', 26.7606, 83.3732, '+91-551-2201072', 'available', 'Station Manager', '+91-551-2201073', 'BRD Medical College'),
        ('Dehradun', 'DDN', 30.3165, 78.0322, '+91-135-2746284', 'available', 'Station Manager', '+91-135-2746285', 'Doon Hospital'),
        ('Haridwar Junction', 'HW', 29.9457, 78.1642, '+91-1334-265131', 'available', 'Station Manager', '+91-1334-265132', 'Haridwar Hospital'),
        ('Amritsar Junction', 'ASR', 31.6340, 74.8723, '+91-183-2746284', 'available', 'Station Manager', '+91-183-2746285', 'Government Hospital Amritsar'),
        ('Chandigarh', 'CDG', 30.7333, 76.7794, '+91-172-2746284', 'available', 'Station Manager', '+91-172-2746285', 'PGI Chandigarh'),
        ('Kalka', 'KLK', 30.8398, 76.9378, '+91-1733-222644', 'available', 'Station Manager', '+91-1733-222645', 'Local Hospital')
    ]
    
    cursor.executemany('INSERT OR IGNORE INTO stations (station_name, station_code, latitude, longitude, contact_number, medical_facility, station_manager_name, station_manager_phone, hospitals_nearby) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', stations_data)
    
    # Insert hospital data
    hospitals_data = [
        ('AIIMS Delhi', 'NDLS', 2.5, '+91-11-26588500', 'Cardiology, Neurology, Emergency', 'yes', 'yes', 28.5672, 77.2100),
        ('Safdarjung Hospital', 'NDLS', 3.2, '+91-11-26165060', 'General Medicine, Surgery, Emergency', 'yes', 'yes', 28.5678, 77.2089),
        ('KEM Hospital', 'BCT', 1.8, '+91-22-24136051', 'Emergency, Trauma, General Medicine', 'yes', 'yes', 19.0176, 72.8562),
        ('JJ Hospital', 'BCT', 2.1, '+91-22-23735555', 'Emergency, Surgery, Cardiology', 'yes', 'yes', 18.9647, 72.8258),
        ('Government General Hospital', 'MAS', 1.5, '+91-44-25281351', 'Emergency, General Medicine, Surgery', 'yes', 'yes', 13.0878, 80.2785),
        ('Apollo Hospital Chennai', 'MAS', 4.2, '+91-44-28296000', 'Cardiology, Neurology, Emergency', 'yes', 'yes', 13.0358, 80.2297),
        ('SVIMS Hospital', 'TPTY', 2.8, '+91-877-2287777', 'Cardiology, Neurology, Emergency', 'yes', 'yes', 13.6833, 79.3667),
        ('Ruia Hospital', 'TPTY', 1.2, '+91-877-2248888', 'General Medicine, Emergency', 'yes', 'yes', 13.6458, 79.4067),
        ('Government Hospital Chittoor', 'CTO', 0.8, '+91-8572-248100', 'Emergency, General Medicine, Surgery', 'yes', 'yes', 13.2150, 79.1050),
        ('Apollo Reach Hospital Chittoor', 'CTO', 2.1, '+91-8572-248200', 'Cardiology, Emergency, ICU', 'yes', 'yes', 13.2200, 79.0950)
    ]
    
    cursor.executemany('INSERT OR IGNORE INTO hospitals (hospital_name, station_code, distance_from_station, contact_number, specialties, emergency_available, ambulance_available, latitude, longitude) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', hospitals_data)
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    lang = session.get('language', request.args.get('lang', 'en'))
    if lang not in LANGUAGES:
        lang = 'en'
    translations = TRANSLATIONS.get(lang, TRANSLATIONS['en']).copy()
    translations['_currentLang'] = lang
    return render_template('index.html', lang=lang, translations=translations, languages=LANGUAGES)

@app.route('/set_language/<lang_code>')
def set_language(lang_code):
    if lang_code in LANGUAGES:
        session['language'] = lang_code
        print(f"Language set to: {lang_code}")
    
    # Get redirect URL from query parameter
    redirect_url = request.args.get('redirect')
    if redirect_url:
        return redirect(redirect_url)
    
    return redirect(url_for('index'))

@app.route('/get_translations/<lang_code>')
def get_translations(lang_code):
    """API endpoint to get translations for a specific language"""
    if lang_code in TRANSLATIONS:
        return jsonify({
            'success': True,
            'language': LANGUAGES[lang_code],
            'translations': TRANSLATIONS[lang_code]
        })
    return jsonify({'success': False, 'message': 'Language not supported'})

@app.route('/emergency')
def emergency_form():
    lang = session.get('language', 'en')
    translations = TRANSLATIONS.get(lang, TRANSLATIONS['en']).copy()
    translations['_currentLang'] = lang
    return render_template('emergency_ultra.html', lang=lang, translations=translations, languages=LANGUAGES, session=session)

@app.route('/login')
def login():
    lang = session.get('language', 'en')
    translations = TRANSLATIONS.get(lang, TRANSLATIONS['en']).copy()
    translations['_currentLang'] = lang
    return render_template('login.html', lang=lang, translations=translations, languages=LANGUAGES)

@app.route('/signup')
def signup():
    lang = session.get('language', 'en')
    # Prepare translations with current language marker
    translations = TRANSLATIONS.get(lang, TRANSLATIONS['en']).copy()
    translations['_currentLang'] = lang
    return render_template('signup.html', lang=lang, translations=translations, languages=LANGUAGES)

@app.route('/login', methods=['POST'])
def login_post():
    data = request.get_json()
    username = data['username']
    password = hashlib.sha256(data['password'].encode()).hexdigest()
    
    conn = sqlite3.connect('emergency_reports.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        session['user_id'] = user[0]
        session['username'] = user[1]
        return jsonify({'success': True, 'message': 'Login successful'})
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'})

@app.route('/signup', methods=['POST'])
def signup_post():
    data = request.get_json()
    username = data['username']
    email = data['email']
    password = hashlib.sha256(data['password'].encode()).hexdigest()
    phone = data['phone']
    
    conn = sqlite3.connect('emergency_reports.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('INSERT INTO users (username, email, password, phone) VALUES (?, ?, ?, ?)',
                      (username, email, password, phone))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Account created successfully'})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'success': False, 'message': 'Username or email already exists'})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/admin_logout')
def admin_logout():
    session.pop('is_admin', None)
    session.pop('admin_username', None)
    return redirect(url_for('index'))

@app.route('/user_dashboard')
def user_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    lang = session.get('language', 'en')
    # Prepare translations with current language marker
    translations = TRANSLATIONS.get(lang, TRANSLATIONS['en']).copy()
    translations['_currentLang'] = lang
    return render_template('user_dashboard.html', username=session.get('username'), lang=lang, translations=translations, languages=LANGUAGES)

@app.route('/admin_login')
def admin_login():
    lang = session.get('language', 'en')
    # Prepare translations with current language marker
    translations = TRANSLATIONS.get(lang, TRANSLATIONS['en']).copy()
    translations['_currentLang'] = lang
    return render_template('admin_login.html', lang=lang, translations=translations, languages=LANGUAGES)

@app.route('/admin_login', methods=['POST'])
def admin_login_post():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # Simple admin credentials (in production, use database)
    if username == 'admin' and password == 'admin123':
        session['is_admin'] = True
        session['admin_username'] = username
        return jsonify({'success': True, 'message': 'Admin login successful'})
    else:
        return jsonify({'success': False, 'message': 'Invalid admin credentials'})

@app.route('/authority_dashboard')
def authority_dashboard():
    # Check if admin is logged in
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    
    try:
        conn = sqlite3.connect('emergency_reports.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM emergency_reports ORDER BY timestamp DESC')
        reports = cursor.fetchall()
        
        # Calculate stats
        total_count = len(reports)
        sos_count = len([r for r in reports if r[6] == 'sos'])
        pending_count = len([r for r in reports if r[9] == 'pending'])
        resolved_count = len([r for r in reports if r[9] == 'resolved'])
        
        # Get train location and nearest stations with hospitals for each report
        enhanced_reports = []
        for report in reports:
            try:
                train_location = get_train_location(report[3])  # train_number
                nearest_stations = find_nearest_stations_with_hospitals(
                    train_location['latitude'], train_location['longitude'], report[3]
                )
                
                enhanced_reports.append({
                    'report': report,
                    'train_location': train_location,
                    'nearest_stations': nearest_stations if nearest_stations else []
                })
            except Exception as e:
                print(f"Error processing report {report[0]}: {e}")
                # Add report with default values
                enhanced_reports.append({
                    'report': report,
                    'train_location': {'train_name': f'Train {report[3]}', 'speed': 0, 'latitude': 0, 'longitude': 0, 'last_station': 'Unknown', 'next_station': 'Unknown'},
                    'nearest_stations': []
                })
        
        conn.close()
        lang = session.get('language', 'en')
        # Prepare translations with current language marker
        translations = TRANSLATIONS.get(lang, TRANSLATIONS['en']).copy()
        translations['_currentLang'] = lang
        # Use professional design template
        return render_template('authority_dashboard_utilitarian.html', 
                             enhanced_reports=enhanced_reports,
                             total_count=total_count,
                             sos_count=sos_count,
                             pending_count=pending_count,
                             resolved_count=resolved_count,
                             lang=lang,
                             translations=translations,
                             languages=LANGUAGES)
    except Exception as e:
        print(f"Database error: {e}")
        # Database not initialized, initialize it
        init_db()
        lang = session.get('language', 'en')
        # Use utilitarian design template
        return render_template('authority_dashboard_utilitarian.html', 
                             enhanced_reports=[],
                             total_count=0,
                             sos_count=0,
                             pending_count=0,
                             resolved_count=0,
                             lang=lang,
                             translations=TRANSLATIONS.get(lang, TRANSLATIONS['en']),
                             languages=LANGUAGES)

@app.route('/dashboard')
def dashboard():
    # Redirect to authority dashboard for backward compatibility
    return redirect(url_for('authority_dashboard'))

# Station Master Routes
@app.route('/station_master_login')
def station_master_login():
    lang = session.get('language', 'en')
    translations = TRANSLATIONS.get(lang, TRANSLATIONS['en']).copy()
    translations['_currentLang'] = lang
    return render_template('station_master_login.html', lang=lang, translations=translations, languages=LANGUAGES)

@app.route('/station_master_login', methods=['POST'])
def station_master_login_post():
    data = request.get_json()
    station_code = data.get('station_code', '').upper()
    password = data.get('password')
    
    # Simple station master credentials (station_code as username, password: station123)
    if password == 'station123':
        # Verify station exists
        try:
            conn = sqlite3.connect('emergency_reports.db')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM stations WHERE station_code = ?', (station_code,))
            station = cursor.fetchone()
            conn.close()
            
            if station:
                session['is_station_master'] = True
                session['station_code'] = station_code
                session['station_name'] = station[1]
                return jsonify({'success': True, 'message': 'Station master login successful'})
            else:
                return jsonify({'success': False, 'message': 'Invalid station code'})
        except Exception as e:
            return jsonify({'success': False, 'message': 'Database error'})
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'})

@app.route('/station_master_dashboard')
def station_master_dashboard():
    if not session.get('is_station_master'):
        return redirect(url_for('station_master_login'))
    
    station_code = session.get('station_code')
    station_name = session.get('station_name')
    
    try:
        conn = sqlite3.connect('emergency_reports.db')
        cursor = conn.cursor()
        
        # Get station info
        cursor.execute('SELECT * FROM stations WHERE station_code = ?', (station_code,))
        station = cursor.fetchone()
        
        # Get emergency reports assigned to this station
        cursor.execute('''
            SELECT * FROM emergency_reports 
            WHERE assigned_station_code = ? 
            ORDER BY timestamp DESC
        ''', (station_code,))
        assigned_reports = cursor.fetchall()
        
        # Convert to dictionary format
        station_reports = []
        for report in assigned_reports:
            try:
                train_location = get_train_location(report[3])
                station_reports.append({
                    'id': report[0],
                    'passenger_name': report[1],
                    'phone': report[2],
                    'train_number': report[3],
                    'coach': report[4],
                    'seat': report[5],
                    'emergency_type': report[6],
                    'description': report[7],
                    'status': report[9],
                    'timestamp': report[10],
                    'nearest_station_code': report[11] if len(report) > 11 else None,
                    'nearest_station_name': report[12] if len(report) > 12 else None,
                    'assigned_station_code': report[13] if len(report) > 13 else None,
                    'assigned_station_name': report[14] if len(report) > 14 else None,
                    'assigned_by_admin': report[15] if len(report) > 15 else None,
                    'assigned_at': report[16] if len(report) > 16 else None,
                    'train_name': train_location.get('train_name', f'Train {report[3]}'),
                    'eta_minutes': 'N/A',
                    'distance_km': 'N/A'
                })
            except Exception as e:
                print(f"Error processing report {report[0]}: {e}")
                station_reports.append({
                    'id': report[0],
                    'passenger_name': report[1],
                    'phone': report[2],
                    'train_number': report[3],
                    'coach': report[4],
                    'seat': report[5],
                    'emergency_type': report[6],
                    'description': report[7],
                    'status': report[9],
                    'timestamp': report[10],
                    'train_name': f'Train {report[3]}',
                    'eta_minutes': 'N/A',
                    'distance_km': 'N/A'
                })
        
        # Calculate stats
        approaching_count = len(station_reports)
        pending_count = len([r for r in station_reports if r['status'] == 'pending'])
        resolved_count = len([r for r in station_reports if r['status'] == 'resolved'])
        
        conn.close()
        
        lang = session.get('language', 'en')
        translations = TRANSLATIONS.get(lang, TRANSLATIONS['en']).copy()
        translations['_currentLang'] = lang
        
        return render_template('station_master_dashboard.html',
                             station_name=station_name,
                             station_code=station_code,
                             contact_number=station[5] if station else 'N/A',
                             medical_facility=station[6] if station else 'N/A',
                             hospitals_nearby=station[9] if station else 'N/A',
                             reports=station_reports,
                             approaching_count=approaching_count,
                             pending_count=pending_count,
                             resolved_count=resolved_count,
                             lang=lang,
                             translations=translations,
                             languages=LANGUAGES)
    except Exception as e:
        print(f"Error in station master dashboard: {e}")
        import traceback
        traceback.print_exc()
        lang = session.get('language', 'en')
        return render_template('station_master_dashboard.html',
                             station_name=station_name,
                             station_code=station_code,
                             contact_number='N/A',
                             medical_facility='N/A',
                             hospitals_nearby='N/A',
                             reports=[],
                             approaching_count=0,
                             pending_count=0,
                             resolved_count=0,
                             lang=lang,
                             translations=TRANSLATIONS.get(lang, TRANSLATIONS['en']),
                             languages=LANGUAGES)

# Admin: Assign emergency to station master
@app.route('/assign_emergency', methods=['POST'])
def assign_emergency():
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized access'})
    
    try:
        data = request.get_json()
        emergency_id = data.get('emergency_id')
        station_code = data.get('station_code')
        station_name = data.get('station_name')
        
        if not emergency_id or not station_code:
            return jsonify({'success': False, 'message': 'Missing required fields'})
        
        conn = sqlite3.connect('emergency_reports.db')
        cursor = conn.cursor()
        
        # Update emergency report with assigned station
        cursor.execute('''
            UPDATE emergency_reports 
            SET assigned_station_code = ?,
                assigned_station_name = ?,
                assigned_by_admin = ?,
                assigned_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (station_code, station_name, session.get('username', 'admin'), emergency_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': f'Emergency assigned to {station_name} ({station_code}) successfully'
        })
    except Exception as e:
        print(f"Error assigning emergency: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/station_master_logout')
def station_master_logout():
    session.pop('is_station_master', None)
    session.pop('station_code', None)
    session.pop('station_name', None)
    return redirect(url_for('index'))

@app.route('/submit_emergency', methods=['POST'])
def submit_emergency():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401
    
    try:
        data = request.get_json()
        
        conn = sqlite3.connect('emergency_reports.db')
        cursor = conn.cursor()
        
        # Use logged-in username instead of form input
        passenger_name = session.get('username', data.get('passenger_name', 'Unknown'))
        
        # Insert emergency report
        location = data.get('location', 'Unknown')
        location_lat = data.get('location_lat')
        location_lng = data.get('location_lng')
        
        # If we have lat/lng but no location name, create location string
        if location_lat and location_lng and location == 'Unknown':
            location = f"Lat: {location_lat}, Lng: {location_lng}"
        
        cursor.execute('''
            INSERT INTO emergency_reports 
            (passenger_name, phone, train_number, coach, seat, emergency_type, description, location)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            passenger_name,
            data['phone'],
            data['train_number'],
            data['coach'],
            data['seat'],
            data['emergency_type'],
            data['description'],
            location
        ))
        
        report_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Get or simulate train location
        train_location = get_train_location(data['train_number'])
        nearest_stations = []
        if train_location:
            # Find nearest stations
            nearest_stations = find_nearest_stations(train_location['latitude'], train_location['longitude'])
            
            # Alert nearby stations (simulate)
            alert_nearby_stations(nearest_stations, {
                'report_id': report_id,
                'train_number': data['train_number'],
                'emergency_type': data['emergency_type'],
                'passenger_name': passenger_name
            })
        
        return jsonify({
            'success': True,
            'message': 'Emergency report submitted! Nearby stations alerted.',
            'report_id': report_id,
            'train_location': train_location,
            'nearest_stations': nearest_stations
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': 'Error submitting emergency report'
        }), 500

@app.route('/update_status/<int:report_id>/<status>')
def update_status(report_id, status):
    conn = sqlite3.connect('emergency_reports.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE emergency_reports SET status = ? WHERE id = ?', (status, report_id))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

def get_real_train_data(train_number):
    """Fetch real train data from multiple API sources"""
    
    # Method 1: Try RailwayAPI.com
    try:
        api_url = f"https://indianrailapi.com/api/v2/TrainInformation/apikey/YOUR_API_KEY/TrainNumber/{train_number}"
        response = requests.get(api_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('ResponseCode') == '200':
                return parse_railway_api_data(data)
    except Exception as e:
        print(f"RailwayAPI Error: {e}")
    
    # Method 2: Try RapidAPI
    try:
        url = f"https://indian-railway-api.p.rapidapi.com/trains/{train_number}"
        headers = {
            "X-RapidAPI-Key": "YOUR_RAPIDAPI_KEY",
            "X-RapidAPI-Host": "indian-railway-api.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            return parse_rapidapi_data(response.json())
    except Exception as e:
        print(f"RapidAPI Error: {e}")
    
    # Method 3: Try Where Is My Train API
    try:
        url = f"https://whereismytrain.in/api/train/{train_number}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return parse_wimt_data(response.json())
    except Exception as e:
        print(f"WIMT API Error: {e}")
    
    return None

def parse_railway_api_data(data):
    """Parse RailwayAPI.com response"""
    try:
        train_info = data.get('Train', {})
        return {
            'train_name': train_info.get('TrainName', ''),
            'source': train_info.get('Source', ''),
            'destination': train_info.get('Destination', ''),
            'current_station': train_info.get('CurrentStation', ''),
            'delay': train_info.get('DelayMinutes', 0),
            'status': train_info.get('TrainStatus', '')
        }
    except Exception as e:
        print(f"Parse error: {e}")
        return None

def parse_rapidapi_data(data):
    """Parse RapidAPI response"""
    try:
        return {
            'train_name': data.get('name', ''),
            'source': data.get('source', ''),
            'destination': data.get('destination', ''),
            'current_station': data.get('current_station', ''),
            'delay': data.get('delay', 0),
            'status': data.get('status', '')
        }
    except Exception as e:
        print(f"Parse error: {e}")
        return None

def parse_wimt_data(data):
    """Parse Where Is My Train response"""
    try:
        return {
            'train_name': data.get('trainName', ''),
            'source': data.get('from', ''),
            'destination': data.get('to', ''),
            'current_station': data.get('currentStation', ''),
            'delay': data.get('delayMinutes', 0),
            'status': data.get('status', '')
        }
    except Exception as e:
        print(f"Parse error: {e}")
        return None

def get_train_location(train_number):
    """Get current train location - try real API first, fallback to simulation"""
    conn = sqlite3.connect('emergency_reports.db')
    cursor = conn.cursor()
    
    # Try to get real train data first
    real_data = get_real_train_data(train_number)
    if real_data:
        # Process real API data here
        # This would depend on the API response format
        pass
    
    # Check if train location exists in local cache
    cursor.execute('SELECT * FROM train_locations WHERE train_number = ?', (train_number,))
    location = cursor.fetchone()
    
    if not location:
        # Simulate train location based on train number
        import random
        
        # Try real API first, then fallback to database
        real_data = get_real_train_data(train_number)
        
        # Get train data from local database
        cursor.execute('SELECT * FROM train_database WHERE train_number = ?', (train_number,))
        train_info = cursor.fetchone()
        
        if train_info:
            train_name = train_info[1]
            source = train_info[2]
            destination = train_info[3]
            route_stations = train_info[4].split(',')
            
            # Get coordinates for source and destination
            cursor.execute('SELECT latitude, longitude FROM stations WHERE station_name = ? OR station_code = ?', (source, source))
            source_coords = cursor.fetchone()
            cursor.execute('SELECT latitude, longitude FROM stations WHERE station_name = ? OR station_code = ?', (destination, destination))
            dest_coords = cursor.fetchone()
            
            if source_coords and dest_coords:
                # Simulate position between source and destination
                import random
                progress = random.uniform(0.2, 0.8)  # 20% to 80% of journey
                lat = source_coords[0] + (dest_coords[0] - source_coords[0]) * progress
                lng = source_coords[1] + (dest_coords[1] - source_coords[1]) * progress
                
                # Determine current stations based on progress
                station_index = int(progress * (len(route_stations) - 1))
                last_station = route_stations[max(0, station_index)]
                next_station = route_stations[min(len(route_stations) - 1, station_index + 1)]
            else:
                # Use source and destination from train info
                lat, lng = 20.5937, 78.9629  # Center of India
                last_station, next_station = source, destination
        else:
            # Unknown train - use realistic default route
            import random
            default_routes = [
                (28.6448, 77.2097, 'New Delhi', 'Mumbai Central', f'Express {train_number}'),
                (19.0330, 72.8397, 'Mumbai Central', 'Chennai Central', f'Superfast {train_number}'),
                (13.0827, 80.2707, 'Chennai Central', 'Bangalore', f'Mail {train_number}'),
                (22.5726, 88.3639, 'Kolkata', 'New Delhi', f'Rajdhani {train_number}')
            ]
            lat, lng, last_station, next_station, train_name = random.choice(default_routes)
            # Add variation for realistic movement
            lat += random.uniform(-0.1, 0.1)
            lng += random.uniform(-0.1, 0.1)
        
        # Add slight variation for realistic movement
        lat += random.uniform(-0.05, 0.05)
        lng += random.uniform(-0.05, 0.05)
        speed = random.uniform(75, 105)  # Realistic train speeds
        
        cursor.execute('''
            INSERT INTO train_locations 
            (train_number, train_name, current_latitude, current_longitude, last_station, next_station, speed)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (train_number, train_name, lat, lng, last_station, next_station, speed))
        conn.commit()
        
        location_data = {
            'train_number': train_number,
            'train_name': train_name,
            'latitude': lat,
            'longitude': lng,
            'last_station': last_station,
            'next_station': next_station,
            'speed': speed
        }
    else:
        location_data = {
            'train_number': location[1],
            'train_name': location[2],
            'latitude': location[3],
            'longitude': location[4],
            'last_station': location[5],
            'next_station': location[6],
            'speed': location[7]
        }
    
    conn.close()
    return location_data

def find_nearest_stations_with_hospitals(lat, lng, train_number, radius_km=100):
    """Find nearest stations with hospital information based on train direction"""
    conn = sqlite3.connect('emergency_reports.db')
    cursor = conn.cursor()
    
    # Get train route to determine direction
    cursor.execute('SELECT route_stations FROM train_database WHERE train_number = ?', (train_number,))
    train_route_row = cursor.fetchone()
    train_route = list(train_route_row) if train_route_row else None
    
    cursor.execute('SELECT * FROM stations')
    stations = [list(row) for row in cursor.fetchall()]
    
    nearest = []
    for station in stations:
        distance = calculate_distance(lat, lng, station[3], station[4])
        if distance <= radius_km:
            # Get hospitals for this station
            cursor.execute('SELECT * FROM hospitals WHERE station_code = ?', (station[2],))
            
            hospital_list = []
            for hospital in [list(h) for h in cursor.fetchall()]:
                hospital_list.append({
                    'name': hospital[1],
                    'distance': hospital[3],
                    'contact': hospital[4],
                    'specialties': hospital[5],
                    'emergency': hospital[6],
                    'ambulance': hospital[7]
                })
            
            # Determine if station is ahead in route
            is_ahead = True
            if train_route:
                route_stations = str(train_route[0]).split(',')
                try:
                    current_idx = next((i for i, s in enumerate(route_stations) if s.strip() in station[1]), -1)
                    is_ahead = current_idx > len(route_stations) // 2
                except:
                    is_ahead = True
            
            nearest.append({
                'name': station[1],
                'code': station[2],
                'distance_km': round(distance, 2),
                'contact': station[5],
                'medical_facility': station[6],
                'manager_name': station[7] if len(station) > 7 else 'Station Manager',
                'manager_phone': station[8] if len(station) > 8 else station[5],
                'hospitals_nearby': station[9] if len(station) > 9 else 'General Hospital',
                'hospitals': hospital_list,
                'is_ahead_in_route': is_ahead,
                'eta_minutes': calculate_eta(distance, 80)  # Assuming 80 km/h average speed
            })
    
    conn.close()
    
    # Sort by distance and prioritize stations ahead in route
    nearest.sort(key=lambda x: (not x['is_ahead_in_route'], x['distance_km']))
    return nearest[:5]

def calculate_eta(distance_km, speed_kmh):
    """Calculate estimated time of arrival in minutes"""
    if speed_kmh <= 0:
        speed_kmh = 60  # Default speed
    return round((distance_km / speed_kmh) * 60)

def find_nearest_stations(lat, lng, radius_km=100):
    """Legacy function for backward compatibility"""
    return find_nearest_stations_with_hospitals(lat, lng, None, radius_km)

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in km"""
    R = 6371
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

def alert_nearby_stations(stations, emergency_data):
    """Alert nearby stations about emergency"""
    for station in stations:
        print(f"ALERT SENT TO {station['name']}:")
        print(f"   Emergency Report ID: {emergency_data['report_id']}")
        print(f"   Train: {emergency_data['train_number']}")
        print(f"   Emergency: {emergency_data['emergency_type']}")
        print(f"   Distance: {station['distance_km']} km")
        print(f"   Contact: {station['contact']}")
        print("   Medical team dispatched!\n")

@app.route('/track_train/<train_number>')
def track_train(train_number):
    """Real-time train tracking endpoint"""
    # Check if request wants JSON or HTML
    if request.headers.get('Accept') == 'application/json' or request.args.get('format') == 'json':
        location = get_train_location(train_number)
        if location:
            nearest_stations = find_nearest_stations(location['latitude'], location['longitude'])
            return jsonify({
                'success': True,
                'train_location': location,
                'nearest_stations': nearest_stations
            })
        return jsonify({'success': False, 'message': 'Train not found'})
    else:
        # Return HTML page
        lang = session.get('language', 'en')
        return render_template('train_info.html', train_number=train_number, lang=lang, translations=TRANSLATIONS.get(lang, TRANSLATIONS['en']), languages=LANGUAGES)

@app.route('/search_trains')
def search_trains():
    """Search trains by number or name"""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'trains': []})
    
    conn = sqlite3.connect('emergency_reports.db')
    cursor = conn.cursor()
    
    # Search by train number, name, source, or destination
    cursor.execute('''
        SELECT train_number, train_name, source_station, destination_station, route_stations 
        FROM train_database 
        WHERE train_number LIKE ? OR train_name LIKE ? OR source_station LIKE ? OR destination_station LIKE ?
        ORDER BY 
            CASE 
                WHEN train_number LIKE ? THEN 1
                WHEN train_name LIKE ? THEN 2
                ELSE 3
            END,
            train_number
        LIMIT 25
    ''', (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%', f'{query}%', f'{query}%'))
    
    trains = cursor.fetchall()
    conn.close()
    
    train_list = [{
        'number': train[0],
        'name': train[1],
        'source': train[2],
        'destination': train[3],
        'route': train[4] if len(train) > 4 else ''
    } for train in trains]
    
    return jsonify({'trains': train_list})

@app.route('/get_train_info/<train_number>')
def get_train_info(train_number):
    """Get detailed train information"""
    # Check if request wants JSON or HTML
    if request.headers.get('Accept') == 'application/json' or request.args.get('format') == 'json':
        conn = sqlite3.connect('emergency_reports.db')
        cursor = conn.cursor()
        
        # Get train details
        cursor.execute('SELECT * FROM train_database WHERE train_number = ?', (train_number,))
        train_info = cursor.fetchone()
        
        if not train_info:
            conn.close()
            return jsonify({'success': False, 'message': 'Train not found'})
        
        # Get current location
        location = get_train_location(train_number)
        
        # Get route stations
        route_stations = train_info[4].split(',')
        
        conn.close()
        
        return jsonify({
            'success': True,
            'train_number': train_info[0],
            'train_name': train_info[1],
            'source': train_info[2],
            'destination': train_info[3],
            'route_stations': route_stations,
            'current_location': location
        })
    else:
        # Return HTML page
        lang = session.get('language', 'en')
        return render_template('train_info.html', train_number=train_number, lang=lang, translations=TRANSLATIONS.get(lang, TRANSLATIONS['en']), languages=LANGUAGES)

@app.route('/train_tracker')
def train_tracker():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    lang = session.get('language', 'en')
    return render_template('train_tracker.html', lang=lang, translations=TRANSLATIONS.get(lang, TRANSLATIONS['en']), languages=LANGUAGES)

@app.route('/train_search')
def train_search():
    lang = session.get('language', 'en')
    return render_template('train_search.html', lang=lang, translations=TRANSLATIONS.get(lang, TRANSLATIONS['en']), languages=LANGUAGES)

@app.route('/medical_response')
def medical_response():
    emergency_id = request.args.get('id')
    
    # Get emergency report data
    emergency_data = None
    if emergency_id:
        conn = sqlite3.connect('emergency_reports.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM emergency_reports WHERE id = ?', (emergency_id,))
        report = cursor.fetchone()
        conn.close()
        
        if report:
            emergency_data = {
                'id': report[0],
                'passenger_name': report[1],
                'phone': report[2],
                'train_number': report[3],
                'coach': report[4],
                'seat': report[5],
                'emergency_type': report[6],
                'description': report[7],
                'location': report[8],
                'status': report[9],
                'timestamp': report[10]
            }
    
    lang = session.get('language', 'en')
    return render_template('medical_response.html', emergency_id=emergency_id, emergency_data=emergency_data, lang=lang, translations=TRANSLATIONS.get(lang, TRANSLATIONS['en']), languages=LANGUAGES)

@app.route('/popular_trains')
def popular_trains():
    """Get list of popular trains"""
    conn = sqlite3.connect('emergency_reports.db')
    cursor = conn.cursor()
    
    # Get popular trains (Rajdhani, Shatabdi, Duronto)
    cursor.execute('''
        SELECT train_number, train_name, source_station, destination_station 
        FROM train_database 
        WHERE train_name LIKE '%Rajdhani%' OR train_name LIKE '%Shatabdi%' OR train_name LIKE '%Duronto%'
        ORDER BY train_number 
        LIMIT 15
    ''')
    
    trains = cursor.fetchall()
    conn.close()
    
    popular_list = [{
        'number': train[0],
        'name': train[1],
        'source': train[2],
        'destination': train[3]
    } for train in trains]
    
    return jsonify({'trains': popular_list})

@app.route('/emergency_map/<int:report_id>')
def emergency_map(report_id):
    """Show emergency location on map"""
    conn = sqlite3.connect('emergency_reports.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM emergency_reports WHERE id = ?', (report_id,))
    report = cursor.fetchone()
    conn.close()
    
    if report:
        train_location = get_train_location(report[3])
        nearest_stations = find_nearest_stations(train_location['latitude'], train_location['longitude'])
        
        lang = session.get('language', 'en')
        return render_template('emergency_map.html', 
                             report=report, 
                             train_location=train_location,
                             nearest_stations=nearest_stations,
                             lang=lang,
                             translations=TRANSLATIONS.get(lang, TRANSLATIONS['en']),
                             languages=LANGUAGES)
    return "Emergency report not found", 404

@app.route('/stations_near/<train_number>')
def stations_near_train(train_number):
    """Get stations near a specific train with hospital information"""
    location = get_train_location(train_number)
    if location:
        nearest_stations = find_nearest_stations_with_hospitals(
            location['latitude'], location['longitude'], train_number, radius_km=50
        )
        return jsonify({
            'success': True,
            'train_location': location,
            'stations': nearest_stations
        })
    return jsonify({'success': False, 'message': 'Train not found'})

@app.route('/virtual_tour')
def virtual_tour():
    lang = session.get('language', 'en')
    return render_template('virtual_tour.html', lang=lang, translations=TRANSLATIONS.get(lang, TRANSLATIONS['en']), languages=LANGUAGES)

@app.route('/seat_recommendation')
def seat_recommendation():
    lang = session.get('language', 'en')
    return render_template('virtual_tour.html', lang=lang, translations=TRANSLATIONS.get(lang, TRANSLATIONS['en']), languages=LANGUAGES)

@app.route('/ai_health')
def ai_health():
    lang = session.get('language', 'en')
    return render_template('ai_health_assistant.html', lang=lang, translations=TRANSLATIONS.get(lang, TRANSLATIONS['en']), languages=LANGUAGES)

@app.route('/crowd_monitor')
def crowd_monitor():
    lang = session.get('language', 'en')
    return render_template('crowd_monitor.html', lang=lang, translations=TRANSLATIONS.get(lang, TRANSLATIONS['en']), languages=LANGUAGES)

@app.route('/medical_bot')
def medical_bot():
    lang = session.get('language', 'en')
    return render_template('medical_bot.html', lang=lang, translations=TRANSLATIONS.get(lang, TRANSLATIONS['en']), languages=LANGUAGES)

# ---------- Medical Bot Knowledge Base ----------

_MEDICAL_KNOWLEDGE = [
    # --- EMERGENCY / CRITICAL ---
    {
        'keywords': ['chest pain', 'heart attack', 'cardiac', 'heart pain'],
        'title': '🚨 Chest Pain / Possible Heart Attack',
        'message': 'Chest pain can be a sign of a heart attack. Please treat this seriously.',
        'steps': [
            'Call 112 or 139 (Railway Helpline) IMMEDIATELY.',
            'Sit down and rest. Do NOT exert yourself.',
            'If available, chew one aspirin tablet (300 mg) unless you are allergic.',
            'Loosen any tight clothing around the chest.',
            'If the person becomes unconscious, begin CPR.',
            'Notify the train attendant/TT for emergency medical stop.',
            'Use the Emergency SOS feature on this app to alert station authorities.',
        ],
        'emergency': 'This is a medical emergency. Call 112 immediately!',
        'disclaimer': 'This guidance is for first aid only. Professional medical attention is critical.',
    },
    {
        'keywords': ['cpr', 'cardiopulmonary', 'resuscitation', 'no pulse', 'not breathing', 'cardiac arrest'],
        'title': '🫀 CPR — Cardiopulmonary Resuscitation',
        'message': 'CPR can save a life when someone is not breathing or has no pulse.',
        'steps': [
            '1. CHECK: Tap the person and shout "Are you OK?" Check for breathing (look, listen, feel for 10 seconds).',
            '2. CALL: Have someone call 112 immediately. If alone, call first then start CPR.',
            '3. Push hard and fast on the center of the chest — 30 compressions at 100-120 per minute.',
            '4. Open the airway by tilting the head back and lifting the chin.',
            '5. Give 2 rescue breaths (1 second each). Watch for chest rise.',
            '6. Repeat cycles of 30 compressions + 2 breaths until help arrives.',
            '7. If an AED is available, turn it on and follow voice prompts.',
            'For infants: Use 2 fingers for compressions on the breastbone.',
        ],
        'emergency': 'CPR should only be performed on someone who is unresponsive with no normal breathing.',
        'disclaimer': 'Hands-only CPR (compressions without breaths) is acceptable if untrained.',
    },
    {
        'keywords': ['choking', 'something stuck', 'cannot swallow', 'airway blocked', 'heimlich'],
        'title': '🆘 Choking — Airway Obstruction',
        'message': 'Choking can be life-threatening. Act quickly.',
        'steps': [
            'If the person can cough forcefully, encourage them to keep coughing.',
            'If they cannot cough, speak,  or breathe: Stand behind them.',
            'Place your fist just above the navel, grab with other hand.',
            'Perform quick upward abdominal thrusts (Heimlich maneuver).',
            'Repeat until the object is dislodged or the person becomes unconscious.',
            'If unconscious, lower to ground and begin CPR. Check the mouth before each breath.',
            'For infants: Give 5 back blows, then 5 chest thrusts.',
        ],
        'emergency': 'If the person becomes unconscious, call 112 and begin CPR.',
        'disclaimer': 'This is emergency first aid guidance.',
    },
    {
        'keywords': ['stroke', 'one sided', 'face drooping', 'arm weakness', 'speech difficulty', 'slurred', 'paralysis'],
        'title': '🧠 Stroke Warning Signs — Act FAST!',
        'message': 'Use the FAST method to check for stroke:',
        'steps': [
            'F — Face: Ask the person to smile. Does one side droop?',
            'A — Arms: Ask them to raise both arms. Does one drift down?',
            'S — Speech: Ask them to repeat a simple phrase. Is speech slurred?',
            'T — Time: If ANY of these signs appear, call 112 RIGHT NOW.',
            'Note the time symptoms started — this is critical for treatment.',
            'Do NOT give food, drink, or medication.',
            'Keep the person comfortable and monitor breathing.',
        ],
        'emergency': 'Stroke treatment is time-critical. Every minute counts!',
        'disclaimer': 'This is emergency guidance. Professional treatment is essential.',
    },
    {
        'keywords': ['severe bleeding', 'heavy bleeding', 'blood loss', 'hemorrhage', 'wound bleeding'],
        'title': '🩸 Severe Bleeding Control',
        'message': 'Controlling severe bleeding quickly can save a life.',
        'steps': [
            'Apply direct, firm pressure on the wound with a clean cloth.',
            'Do NOT remove the cloth if blood soaks through — add more layers on top.',
            'If possible, elevate the injured limb above heart level.',
            'If bleeding does not stop with pressure, apply a makeshift tourniquet above the wound.',
            'Keep the person lying down and warm to prevent shock.',
            'Call 112 / 139 immediately for emergency help.',
            'Monitor the person for signs of shock: pale skin, rapid breathing, confusion.',
        ],
        'emergency': 'Severe bleeding is a medical emergency. Call 112!',
        'disclaimer': 'Apply continuous pressure until medical help arrives.',
    },
    # --- FIRST AID ---
    {
        'keywords': ['burn', 'burns', 'scalded', 'scald', 'hot water burn', 'fire burn'],
        'title': '🔥 Burns — First Aid Treatment',
        'message': 'Proper first aid for burns reduces pain and prevents complications.',
        'steps': [
            'Cool the burn immediately under cool (NOT ice cold) running water for at least 10-20 minutes.',
            'Remove jewelry or tight items near the burn before swelling occurs.',
            'Do NOT apply butter, toothpaste, ice, or home remedies — these can worsen burns.',
            'Cover with a clean, non-stick bandage or cling film loosely.',
            'Take over-the-counter pain relief like paracetamol if needed.',
            'For blisters: Do NOT pop them. They protect against infection.',
            'Seek medical attention for burns larger than your palm, on face/joints, or deep burns.',
        ],
        'warning': 'For severe/deep burns or burns covering a large area, call 112 immediately.',
        'disclaimer': 'This is first aid guidance. Severe burns require professional medical care.',
    },
    {
        'keywords': ['cut', 'cuts', 'wound', 'wounds', 'laceration', 'bleeding cut', 'knife cut'],
        'title': '🩹 Cuts & Wounds — First Aid',
        'message': 'Most minor cuts can be treated at home with proper first aid.',
        'steps': [
            'Wash your hands before treating the wound.',
            'Apply gentle pressure with a clean cloth to stop bleeding.',
            'Clean the wound gently with clean water. Remove any visible debris.',
            'Apply an antiseptic solution or antibacterial ointment.',
            'Cover with a sterile bandage or adhesive dressing.',
            'Change the dressing daily or if it gets wet/dirty.',
            'Watch for signs of infection: increasing redness, swelling, warmth, pus, or fever.',
        ],
        'warning': 'Seek medical help if the cut is deep, won\'t stop bleeding, or shows signs of infection.',
        'disclaimer': 'This is general first aid guidance.',
    },
    {
        'keywords': ['fracture', 'broken bone', 'broken arm', 'broken leg', 'sprain', 'dislocation'],
        'title': '🦴 Fractures & Sprains',
        'message': 'If you suspect a broken bone, immobilize the area and seek medical help.',
        'steps': [
            'Do NOT try to realign or move the broken bone.',
            'Immobilize the area: Use a makeshift splint (roll of newspaper, stick, etc.) padded with cloth.',
            'Apply ice wrapped in cloth (not directly on skin) to reduce swelling — 20 min on, 20 min off.',
            'Elevate the injured limb if possible.',
            'For sprains: Rest, Ice, Compression, Elevation (RICE method).',
            'Take paracetamol for pain relief. Avoid ibuprofen if there is significant swelling.',
            'Seek medical evaluation at the next station or call for assistance.',
        ],
        'warning': 'If the bone has broken the skin (open fracture) or the person cannot move, call 112.',
        'disclaimer': 'Fractures require professional medical evaluation and treatment.',
    },
    # --- COMMON SYMPTOMS ---
    {
        'keywords': ['fever', 'temperature', 'high temperature', 'hot body', 'feverish', 'feeling hot'],
        'title': '🌡️ Fever Management',
        'message': 'Fever is the body\'s natural response to infection. Here\'s how to manage it:',
        'steps': [
            'Take paracetamol (500mg) or ibuprofen as directed on the packaging.',
            'Stay hydrated — drink plenty of water, ORS, or clear fluids.',
            'Rest as much as possible. Avoid strenuous activity.',
            'Use a damp cloth on the forehead for comfort.',
            'Wear light, comfortable clothing. Don\'t over-bundle.',
            'Monitor temperature regularly if possible.',
            'Seek medical help if fever exceeds 103°F (39.4°C) or lasts more than 3 days.',
        ],
        'warning': 'High fever with stiff neck, severe headache, or rash needs immediate medical attention.',
        'disclaimer': 'This is general health guidance, not a diagnosis.',
    },
    {
        'keywords': ['headache', 'head pain', 'migraine', 'head ache', 'head hurting'],
        'title': '🤕 Headache Relief',
        'message': 'Most headaches can be managed with these steps:',
        'steps': [
            'Drink water — dehydration is a common cause of headaches, especially during travel.',
            'Rest in a quiet, dimly lit area if possible.',
            'Take paracetamol (500mg) or ibuprofen for pain relief.',
            'Apply a cold or warm compress to your forehead or neck.',
            'Gently massage your temples and the base of your skull.',
            'Avoid screen time and bright lights.',
            'Practice deep breathing: Inhale for 4 counts, hold 4, exhale 4.',
            'Eat something light if you haven\'t eaten — low blood sugar triggers headaches.',
        ],
        'warning': 'Seek emergency help if headache is sudden and severe, or accompanied by confusion, vision changes, or stiff neck.',
        'disclaimer': 'This is general guidance. Persistent or severe headaches should be evaluated by a doctor.',
    },
    {
        'keywords': ['nausea', 'vomiting', 'vomit', 'throwing up', 'feeling sick', 'upset stomach'],
        'title': '🤢 Nausea & Vomiting',
        'message': 'Nausea and vomiting can have many causes. Here is how to manage:',
        'steps': [
            'Take small sips of clear fluids — water, ginger tea, or ORS solution.',
            'Avoid solid foods until the vomiting stops. Then start with bland foods (crackers, toast, rice).',
            'Sit upright or lie on your side to prevent choking if vomiting.',
            'If available, suck on ginger candy or take ginger tablets — ginger helps reduce nausea.',
            'Avoid strong smells, greasy, or spicy food.',
            'Get fresh air if possible (open a window on the train).',
            'If vomiting continues for more than 24 hours, seek medical help.',
        ],
        'warning': 'Seek emergency care if vomiting blood, or if accompanied by severe abdominal pain or high fever.',
        'disclaimer': 'This is general guidance. Persistent vomiting may indicate a serious condition.',
    },
    {
        'keywords': ['dizziness', 'dizzy', 'lightheaded', 'vertigo', 'feeling faint', 'room spinning'],
        'title': '😵 Dizziness & Lightheadedness',
        'message': 'Dizziness can be caused by dehydration, low blood pressure, or inner ear issues.',
        'steps': [
            'Sit or lie down immediately to prevent falls.',
            'Drink water or an electrolyte drink — dehydration is a common cause.',
            'If sitting, put your head between your knees.',
            'Breathe slowly and deeply through your nose.',
            'Avoid sudden position changes — get up slowly.',
            'Eat something if you haven\'t eaten recently — low blood sugar can cause dizziness.',
            'Avoid caffeine and alcohol.',
            'If symptoms persist after 15-20 minutes, notify the train attendant.',
        ],
        'warning': 'Seek emergency help if dizziness is accompanied by chest pain, severe headache, numbness, or slurred speech.',
        'disclaimer': 'Persistent or recurrent dizziness should be evaluated by a doctor.',
    },
    {
        'keywords': ['breathing', 'breathless', 'shortness of breath', 'breathing difficulty', 'can\'t breathe', 'asthma attack', 'wheezing'],
        'title': '🫁 Breathing Difficulty',
        'message': 'Difficulty breathing requires immediate attention.',
        'steps': [
            'Sit upright — this opens the airways better than lying down.',
            'Loosen any tight clothing around the chest and neck.',
            'If you have an inhaler (asthma), use it as prescribed.',
            'Try pursed-lip breathing: Breathe in through nose for 2 counts, out through pursed lips for 4 counts.',
            'Stay calm — anxiety worsens breathing difficulty.',
            'Get fresh air if possible.',
            'If someone is having an asthma attack without an inhaler, have them sit upright and call 112.',
            'Notify the train attendant/TT immediately.',
        ],
        'emergency': 'If breathing is severely impaired, lips turn blue, or person is unable to speak, call 112 IMMEDIATELY.',
        'disclaimer': 'Severe breathing difficulty is a medical emergency.',
    },
    {
        'keywords': ['abdominal', 'stomach pain', 'belly pain', 'stomach ache', 'tummy pain', 'stomach cramps', 'cramps'],
        'title': '🤧 Abdominal/Stomach Pain',
        'message': 'Stomach pain has many causes. Here is general guidance:',
        'steps': [
            'Rest in a comfortable position — lying on your side may help.',
            'Sip warm water or herbal tea (peppermint or ginger).',
            'Avoid spicy, fried, or heavy food.',
            'If gas-related, try walking slowly or gentle movement.',
            'A hot water bottle or warm compress on the abdomen can help relieve cramps.',
            'Take antacid if you suspect acidity/heartburn.',
            'Avoid painkillers like aspirin/ibuprofen on empty stomach as they can worsen pain.',
        ],
        'warning': 'Seek medical help if pain is severe, persistent, or accompanied by fever, vomiting blood, or inability to pass gas.',
        'disclaimer': 'Persistent abdominal pain should be evaluated by a doctor.',
    },
    {
        'keywords': ['diarrhea', 'loose motions', 'loose stools', 'watery stool', 'frequent stools'],
        'title': '💧 Diarrhea Management',
        'message': 'Diarrhea can lead to dangerous dehydration. Here is how to manage:',
        'steps': [
            'Stay hydrated! Drink ORS (Oral Rehydration Solution) — mix in clean water as per instructions.',
            'If no ORS: Mix 6 teaspoons sugar + ½ teaspoon salt in 1 liter clean water.',
            'Take small, frequent sips rather than large amounts at once.',
            'Eat bland foods: rice, bananas, toast, boiled potatoes.',
            'Avoid dairy, caffeine, alcohol, and spicy foods.',
            'Wash hands thoroughly after using the bathroom.',
            'Zinc supplements can help reduce duration (especially in children).',
        ],
        'warning': 'Seek medical help if diarrhea persists beyond 2 days, contains blood, or if you feel severely dehydrated.',
        'disclaimer': 'This is general guidance. Severe diarrhea requires medical treatment.',
    },
    # --- FOOD & TRAVEL ---
    {
        'keywords': ['food poisoning', 'bad food', 'spoiled food', 'ate something bad', 'food safety'],
        'title': '🍽️ Food Poisoning',
        'message': 'Food poisoning from contaminated food is common during travel.',
        'steps': [
            'Stay hydrated — sip on ORS solution, clear broths, or coconut water.',
            'Rest your stomach — avoid eating solid food for a few hours.',
            'When ready, eat bland foods: dry toast, rice, bananas, plain crackers.',
            'Avoid dairy products, caffeine, alcohol, and fatty or spicy foods.',
            'If vomiting, lie on your side to prevent choking.',
            'Take an over-the-counter anti-nausea medication if available.',
            'Practice good hygiene — wash hands frequently.',
            'Prevention: On trains, eat only freshly cooked food; avoid cut fruits from vendors.',
        ],
        'warning': 'Seek medical help if symptoms are severe, there is blood in vomit/stool, or fever exceeds 101°F.',
        'disclaimer': 'Most food poisoning resolves in 1-2 days. Seek help if symptoms persist.',
    },
    {
        'keywords': ['motion sickness', 'travel sickness', 'car sick', 'train sick', 'nausea travel'],
        'title': '🚆 Motion Sickness on Trains',
        'message': 'Motion sickness is common and manageable.',
        'steps': [
            'Sit facing the direction of travel if possible.',
            'Focus on a fixed point in the distance or close your eyes.',
            'Get fresh air — open a window or stand near the door between coaches.',
            'Chew ginger candy or sip ginger tea — ginger is a natural anti-nausea remedy.',
            'Avoid reading or looking at screens while the train is moving.',
            'Eat light, plain food before travel. Avoid heavy, greasy meals.',
            'If you have anti-motion sickness tablets (Dramamine/Dimenhydrinate), take as directed.',
            'Pressure bands on the wrist (P6 acupressure point) can help some people.',
        ],
        'disclaimer': 'Motion sickness is not dangerous but can be very uncomfortable.',
    },
    {
        'keywords': ['dehydration', 'dehydrated', 'thirsty', 'dry mouth', 'not enough water'],
        'title': '💧 Dehydration — Symptoms & Treatment',
        'message': 'Dehydration is common during train journeys, especially in hot weather.',
        'steps': [
            'Drink water frequently — don\'t wait until you feel thirsty.',
            'ORS solution is ideal: Mix 6 tsp sugar + ½ tsp salt in 1L clean water.',
            'Coconut water and buttermilk are excellent natural rehydrators.',
            'Avoid excess tea, coffee, and alcohol — they can worsen dehydration.',
            'Watch for symptoms: dark yellow urine, dry lips, headache, dizziness, fatigue.',
            'In children and elderly, dehydration can progress quickly — monitor closely.',
            'Eat water-rich fruits if available: watermelon, cucumber, oranges.',
            'Carry a reusable water bottle on train journeys.',
        ],
        'warning': 'Severe dehydration (confusion, no urination, sunken eyes) needs immediate medical help.',
        'disclaimer': 'Stay proactive about hydration during long train journeys.',
    },
    # --- CHRONIC CONDITIONS ---
    {
        'keywords': ['diabetes', 'diabetic', 'blood sugar', 'sugar level', 'insulin', 'hypoglycemia', 'high sugar'],
        'title': '💉 Diabetes Management on Journeys',
        'message': 'Managing diabetes during travel requires preparation and vigilance.',
        'steps': [
            'Keep all medications/insulin in your carry-on, never in checked luggage.',
            'Carry glucose tablets or candy for low blood sugar emergencies.',
            'If blood sugar drops (shaking, sweating, confusion): eat sugar/candy immediately.',
            'Maintain regular meal times as much as possible.',
            'Stay hydrated with water. Avoid sugary drinks.',
            'Carry a medical ID card mentioning your condition.',
            'Keep snacks handy: nuts, whole grain biscuits, fruits.',
            'Monitor blood sugar levels more frequently during travel.',
            'Inform co-passengers about your condition in case of emergency.',
        ],
        'warning': 'Seek medical help if blood sugar remains very high or very low despite treatment.',
        'disclaimer': 'Follow your doctor\'s prescribed treatment plan.',
    },
    {
        'keywords': ['blood pressure', 'hypertension', 'bp high', 'bp low', 'high bp', 'low bp'],
        'title': '❤️ Blood Pressure Management',
        'message': 'Managing blood pressure during travel:',
        'steps': [
            'Take all prescribed blood pressure medications on time, even while traveling.',
            'Limit salt intake and avoid very salty train snacks.',
            'Stay hydrated — dehydration can affect blood pressure.',
            'Avoid sitting in the same position for hours — stretch and walk in the aisle periodically.',
            'Practice deep breathing if you feel stressed or anxious.',
            'For low BP: Lie down, elevate legs, sip salty water or ORS.',
            'For high BP: Rest, avoid caffeine, practice calm breathing.',
            'Carry a portable BP monitor if possible.',
        ],
        'warning': 'Seek immediate help if BP is extremely high (>180/120) or if experiencing chest pain/vision changes.',
        'disclaimer': 'Follow your doctor\'s advice regarding medication and lifestyle.',
    },
    {
        'keywords': ['asthma', 'inhaler', 'breathing condition', 'chronic breathing'],
        'title': '🌬️ Asthma Management',
        'message': 'Managing asthma during train travel:',
        'steps': [
            'Always carry your reliever inhaler (usually blue) within easy reach.',
            'If having symptoms: Use inhaler — 2 puffs, wait 30 seconds between puffs.',
            'Sit upright to help open airways.',
            'Stay away from triggers: dust, smoke, strong perfumes.',
            'On trains, avoid sitting near windows where dust can blow in.',
            'If symptoms worsen after using inhaler, take 2 more puffs after 2 minutes.',
            'Stay calm — anxiety can make an asthma attack worse.',
            'If inhaler is not helping, seek emergency help immediately.',
        ],
        'emergency': 'If reliever inhaler is not working or lips turn blue, call 112 immediately.',
        'disclaimer': 'Asthma management should follow your doctor\'s action plan.',
    },
    # --- MENTAL HEALTH ---
    {
        'keywords': ['anxiety', 'anxious', 'panic attack', 'panic', 'nervous', 'worried', 'fear'],
        'title': '🧠 Anxiety & Panic Attacks',
        'message': 'Panic attacks feel terrifying but are not life-threatening. Here is how to manage:',
        'steps': [
            '5-4-3-2-1 Grounding: Name 5 things you see, 4 you touch, 3 you hear, 2 you smell, 1 you taste.',
            'Breathe slowly: Inhale 4 counts, hold 4 counts, exhale 6 counts. Repeat 5-10 times.',
            'Remind yourself: "This is a panic attack. It will pass. I am safe."',
            'Unclench your jaw, relax your shoulders, loosen your hands.',
            'Focus on physical sensations — feel your feet on the ground.',
            'If possible, splash cold water on your face or hold something cold.',
            'Avoid caffeine and alcohol which can trigger anxiety.',
            'Talk to someone you trust if you feel overwhelmed.',
        ],
        'disclaimer': 'If you experience frequent panic attacks, please consult a mental health professional.',
    },
    {
        'keywords': ['stress', 'stressed', 'overwhelmed', 'burnout', 'tension', 'mental health'],
        'title': '🧘 Stress Management',
        'message': 'Stress during travel is common. Here are practical tips:',
        'steps': [
            'Deep breathing exercise: Breathe in for 4 counts, hold for 7, exhale for 8.',
            'Progressive muscle relaxation: Tense and release each muscle group from toes to head.',
            'Listen to calming music or nature sounds if you have headphones.',
            'Take a short walk through the train if possible.',
            'Stay hydrated and eat regular meals — hunger and dehydration worsen stress.',
            'Limit news and social media if they increase your anxiety.',
            'Journal or write down your thoughts — getting them on paper helps..',
            'Remember: It\'s okay to ask for help. Talk to train staff or co-passengers.',
        ],
        'disclaimer': 'If stress is persistent and affecting daily life, consider reaching out to a counselor.',
    },
    # --- ALLERGIES ---
    {
        'keywords': ['allergy', 'allergic', 'allergic reaction', 'hives', 'rash', 'itching', 'swelling face'],
        'title': '⚠️ Allergic Reactions',
        'message': 'Allergic reactions range from mild to life-threatening.',
        'steps': [
            'For mild reactions (hives, itching): Take an antihistamine if available.',
            'Apply a cold compress to itchy or swollen areas.',
            'Remove the allergen if known (stop eating the food, move away from the trigger).',
            'For insect stings: Remove the stinger, clean the area, apply ice.',
            'Watch for signs of severe reaction (anaphylaxis): difficulty breathing, facial swelling, dizziness.',
            'If the person has an EpiPen, help them use it on the outer thigh.',
            'Call 112 if throat is swelling, breathing becomes difficult, or the person feels faint.',
        ],
        'emergency': 'Anaphylaxis (severe reaction) is life-threatening. Use EpiPen and call 112!',
        'disclaimer': 'Carry antihistamines if you have known allergies, especially while traveling.',
    },
    # --- PREVENTIVE CARE ---
    {
        'keywords': ['hygiene', 'hand wash', 'clean', 'sanitation', 'germs', 'infection prevention'],
        'title': '🧼 Hygiene & Infection Prevention',
        'message': 'Good hygiene prevents many illnesses, especially during travel.',
        'steps': [
            'Wash hands with soap for at least 20 seconds, especially before eating.',
            'Carry hand sanitizer (60%+ alcohol) when soap is unavailable.',
            'Avoid touching your face — especially eyes, nose, and mouth.',
            'Use clean water for drinking. If unsure, drink packaged bottled water.',
            'Carry wet wipes to clean surfaces like berth handles and trays.',
            'Cover your mouth/nose when coughing or sneezing.',
            'Keep your personal belongings clean and food covered.',
            'Use toilet seat sanitizer or cover the seat with tissue paper.',
        ],
        'disclaimer': 'Prevention is always better than cure, especially during long journeys.',
    },
    {
        'keywords': ['nutrition', 'diet', 'healthy eating', 'what to eat', 'food tips', 'travel food'],
        'title': '🥗 Nutrition Tips for Train Travel',
        'message': 'Eating well during train journeys keeps your energy up and prevents illness.',
        'steps': [
            'Pack home-cooked meals when possible — they are safer than vendor food.',
            'Carry dry snacks: roasted nuts, biscuits, energy bars, dried fruits.',
            'Bring fruits that don\'t need cutting: bananas, apples, oranges.',
            'Avoid cut fruits and salads sold on platforms — they may be contaminated.',
            'Eat freshly cooked, hot food from IRCTC-authorized pantry cars.',
            'Stay hydrated with sealed bottled water.',
            'Carry ORS packets for long journeys, especially in summer.',
            'Avoid excessive tea/coffee — they can cause dehydration.',
        ],
        'disclaimer': 'Food safety is crucial during travel to avoid gastrointestinal infections.',
    },
    # --- SNAKE BITE / INSECT ---
    {
        'keywords': ['snake bite', 'snake', 'insect bite', 'spider bite', 'scorpion'],
        'title': '🐍 Snake & Insect Bites',
        'message': 'Stay calm and follow these steps:',
        'steps': [
            'Keep the person calm and still — movement spreads venom faster.',
            'Immobilize the bitten limb and keep it below heart level.',
            'Remove any rings, watches, or tight clothing near the bite.',
            'Clean the wound gently. Do NOT suck out venom or cut the wound.',
            'Do NOT apply a tourniquet or ice.',
            'Note the time of the bite and appearance of the snake if possible.',
            'Call 112 and seek anti-venom treatment at the nearest hospital.',
            'Monitor for symptoms: swelling, pain, nausea, difficulty breathing.',
        ],
        'emergency': 'Snake bites require immediate hospital treatment. Call 112!',
        'disclaimer': 'Do not use traditional remedies. Seek medical help immediately.',
    },
    # --- GENERAL / CATCH-ALL ---
    {
        'keywords': ['hello', 'hi', 'hey', 'good morning', 'good evening', 'help'],
        'title': '👋 Welcome to MedAssist!',
        'message': 'Hello! I\'m here to help you with health and medical guidance.',
        'steps': [
            'You can ask me about any health symptoms or conditions.',
            'Try questions like: "What to do for a headache?", "How to treat burns?", "CPR steps"',
            'Use the topic buttons on the sidebar for quick help.',
            'For emergencies, always call 112 (National) or 139 (Railway).',
        ],
        'disclaimer': 'I provide general health guidance. Always consult a doctor for proper diagnosis.',
    },
    {
        'keywords': ['thank', 'thanks', 'thank you', 'bye', 'goodbye'],
        'title': '🙏 Thank You!',
        'message': 'You\'re welcome! Stay safe and healthy on your journey.',
        'steps': [
            'Remember: For any emergency, call 112 or Railway Helpline 139.',
            'You can come back anytime for more health guidance.',
            'Take care and have a safe journey! 🚆',
        ],
        'disclaimer': 'This bot is always available for health questions.',
    },
    {
        'keywords': ['cold', 'cough', 'runny nose', 'sore throat', 'sneezing', 'congestion', 'flu'],
        'title': '🤧 Cold, Cough & Flu',
        'message': 'Common cold and flu symptoms can be managed with these tips:',
        'steps': [
            'Rest as much as possible — your body needs energy to fight the infection.',
            'Stay hydrated: warm water, herbal tea with honey and ginger, warm soup.',
            'For sore throat: Gargle with warm salt water (½ tsp salt in a glass of warm water).',
            'Take paracetamol for body ache and fever.',
            'Steam inhalation helps clear congestion — inhale steam from hot water for 5-10 minutes.',
            'Avoid cold drinks and ice cream.',
            'Cover your mouth when sneezing/coughing to prevent spreading.',
            'Use a nasal decongestant spray if congestion is severe (short-term only).',
        ],
        'warning': 'See a doctor if fever is high, symptoms last more than a week, or breathing becomes difficult.',
        'disclaimer': 'Most colds resolve in 5-7 days. Seek help if symptoms are severe.',
    },
    {
        'keywords': ['eye', 'eye pain', 'eye infection', 'red eye', 'something in eye', 'eye irritation'],
        'title': '👁️ Eye Problems',
        'message': 'Eye issues on trains can be caused by dust, wind, or infection.',
        'steps': [
            'If something is in your eye: Blink repeatedly, let tears wash it out naturally.',
            'Do NOT rub your eye — this can scratch the surface.',
            'Wash the eye gently with clean water if possible.',
            'Wear sunglasses to protect from dust and wind on the train.',
            'For red, itchy eyes: Apply a cool, damp cloth as a compress.',
            'If wearing contact lenses, remove them if your eye is irritated.',
            'Avoid touching or rubbing eyes with unwashed hands.',
        ],
        'warning': 'Seek medical help for sudden vision changes, severe pain, or chemical splashes.',
        'disclaimer': 'This is general guidance. Eye conditions require professional evaluation.',
    },
    {
        'keywords': ['fainting', 'fainted', 'unconscious', 'collapsed', 'passed out'],
        'title': '😵 Fainting / Loss of Consciousness',
        'message': 'If someone has fainted:',
        'steps': [
            'Lay the person on their back and elevate their legs about 12 inches.',
            'Loosen any tight clothing.',
            'Check for breathing. If not breathing, begin CPR and call 112.',
            'If breathing, keep them in recovery position (on their side).',
            'Do NOT give food or water if unconscious.',
            'Fan them gently and apply a cool cloth to the forehead.',
            'When they wake up, give small sips of water and keep them lying down for 15 minutes.',
            'Ask about medical conditions: diabetes, epilepsy, heart problems.',
        ],
        'emergency': 'If the person does not regain consciousness within 1 minute, call 112.',
        'disclaimer': 'Fainting can be caused by many conditions — medical evaluation is recommended.',
    },
    {
        'keywords': ['sunstroke', 'heat stroke', 'heat exhaustion', 'sun exposure', 'overheating'],
        'title': '☀️ Heat Stroke / Heat Exhaustion',
        'message': 'Heat-related illness is common on trains during summer.',
        'steps': [
            'Move the person to a cooler area (AC coach, shaded part of the train).',
            'Remove excess clothing and fan the person.',
            'Apply cool, wet cloths to neck, armpits, and groin.',
            'Give sips of cool water if the person is conscious.',
            'Do NOT give large amounts of water at once.',
            'If available, apply ice packs to neck and armpits.',
            'Heat stroke signs: hot/red/dry skin, confusion, high body temperature (>104°F).',
        ],
        'emergency': 'Heat stroke is a medical emergency. If person is confused or has very high temp, call 112!',
        'disclaimer': 'Prevention: stay hydrated, wear light clothing, and avoid sun exposure during peak hours.',
    },
]


def _match_medical_query(message):
    """Match user message to medical knowledge base using keyword matching."""
    msg_lower = message.lower().strip()
    words = set(msg_lower.split())

    best_match = None
    best_score = 0

    for entry in _MEDICAL_KNOWLEDGE:
        score = 0
        for kw in entry['keywords']:
            kw_words = kw.lower().split()
            # Check if the full keyword phrase appears in the message
            if kw.lower() in msg_lower:
                score += len(kw_words) * 3  # Multi-word match bonus
            else:
                # Check individual keyword words
                for kw_word in kw_words:
                    if kw_word in words:
                        score += 1

        if score > best_score:
            best_score = score
            best_match = entry

    return best_match if best_score > 0 else None


@app.route('/api/medical_bot', methods=['POST'])
def api_medical_bot():
    """Medical bot chat endpoint.

    Uses a comprehensive rule-based system to provide health guidance
    based on keyword matching against a curated medical knowledge base.
    """
    payload = request.get_json(silent=True) or {}
    message = payload.get('message', '').strip()

    if not message:
        return jsonify({
            'success': False,
            'message': 'Please provide a health-related question.',
        })

    # Check if user is asking about non-medical topics
    non_medical = ['weather', 'sports', 'cricket', 'movie', 'politics', 'recipe', 'cooking',
                   'game', 'music', 'song', 'joke', 'funny', 'math', 'calculate', 'programming',
                   'code', 'software', 'shopping', 'price', 'buy', 'stock market']
    msg_lower = message.lower()
    if any(nm in msg_lower for nm in non_medical):
        return jsonify({
            'success': True,
            'response': {
                'title': '🏥 Medical Topics Only',
                'message': 'I\'m a medical health assistant and can only help with health-related questions.',
                'steps': [
                    'Try asking about symptoms, first aid, or health conditions.',
                    'Example: "How to treat a headache?" or "What to do for a burn?"',
                    'Use the topic buttons for quick health guidance.',
                ],
                'disclaimer': 'I specialize in health and medical guidance only.',
            }
        })

    match = _match_medical_query(message)

    if match:
        response = {
            'title': match.get('title', ''),
            'message': match.get('message', ''),
            'steps': match.get('steps', []),
            'disclaimer': match.get('disclaimer', 'This is general health guidance, not a diagnosis.'),
        }
        if match.get('warning'):
            response['warning'] = match['warning']
        if match.get('emergency'):
            response['emergency'] = match['emergency']
        return jsonify({'success': True, 'response': response})

    # Fallback for unrecognized queries
    return jsonify({
        'success': True,
        'response': {
            'title': '🤔 Let me help you',
            'message': 'I couldn\'t find specific guidance for your query, but here are some general tips:',
            'steps': [
                'Try describing your symptoms more specifically (e.g., "I have a headache and fever").',
                'Use the quick-action chips or sidebar topics for common health issues.',
                'For emergencies, always call 112 (National) or 139 (Railway Helpline).',
                'You can ask about: first aid, fever, headache, burns, CPR, diabetes, anxiety, and more.',
            ],
            'disclaimer': 'For specific medical advice, please consult a healthcare professional.',
        }
    })


@app.route('/features')
def features():
    lang = session.get('language', 'en')
    features_data = {
        'ai_health': {'title': 'AI Health Assistant', 'description': 'Real-time medical guidance', 'icon': '🤖'},
        'medical_bot': {'title': 'Medical Health Bot', 'description': 'Chat-based medical guidance', 'icon': '💬'},
        'crowd_monitor': {'title': 'Train Crowd Monitor', 'description': 'Real-time coach occupancy', 'icon': '📊'},
        'emergency_tracking': {'title': 'Emergency Response Tracking', 'description': 'Live tracking with ETA', 'icon': '🚨'},
        'multi_language': {'title': 'Multi-Language Support', 'description': '6 Indian languages', 'icon': '🌐'},
        'predictive_alerts': {'title': 'Predictive Health Alerts', 'description': 'AI-powered health risk prediction', 'icon': '⚠️'},
        'station_network': {'title': 'Smart Station Network', 'description': '40+ railway stations', 'icon': '🚉'}
    }
    return render_template('features.html', features=features_data, lang=lang, translations=TRANSLATIONS.get(lang, TRANSLATIONS['en']), languages=LANGUAGES)


def _normalize_text_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        items = value
    else:
        items = str(value).split(',')
    return [str(x).strip().lower() for x in items if str(x).strip()]


def _health_triage(symptoms, age=None, pregnant=None):
    """Deterministic triage.

    Returns safe guidance without claiming diagnosis.
    """
    s = set(_normalize_text_list(symptoms))

    # Red flags (seek emergency care)
    red_flags = {
        'chest pain',
        'severe chest pain',
        'difficulty breathing',
        'shortness of breath',
        'breathing difficulty',
        'unconscious',
        'fainting',
        'seizure',
        'severe bleeding',
        'stroke symptoms',
        'one-sided weakness',
        'slurred speech',
        'confusion',
        'severe allergic reaction',
        'anaphylaxis',
        'severe burn',
        'head injury',
        'severe headache',
        'vomiting blood',
        'blood in stool',
    }

    # Medium urgency flags
    urgent_flags = {
        'high fever',
        'fever',
        'persistent vomiting',
        'dehydration',
        'severe abdominal pain',
        'abdominal pain',
        'wheezing',
        'moderate bleeding',
        'fracture',
    }

    # Determine category
    emergency = bool(s.intersection(red_flags))
    urgent = bool(s.intersection(urgent_flags))

    # Special population adjustments
    try:
        if age is not None and int(age) >= 65 and (emergency or urgent):
            urgent = True
        if pregnant and (urgent or emergency):
            urgent = True
    except Exception:
        pass

    if emergency:
        level = 'emergency'
        actions = [
            'Call 112 / 108 (ambulance) or Railway Helpline 139 immediately.',
            'If safe, notify the coach attendant/TT and request medical assistance at the next station.',
            'Do not give food/drink if unconscious or having severe breathing difficulty.',
            'Use the Emergency SOS feature in this app to file a report for coordination.'
        ]
    elif urgent:
        level = 'urgent'
        actions = [
            'Seek medical evaluation as soon as possible (next major station / nearest medical facility).',
            'Monitor symptoms; if worsening or new chest pain/breathing difficulty occurs, treat as emergency.',
            'Use the Emergency SOS feature if you need station support.'
        ]
    else:
        level = 'self_care'
        actions = [
            'Consider rest, hydration, and basic first aid if appropriate.',
            'If symptoms persist, worsen, or you develop chest pain/breathing difficulty, seek urgent care.',
            'Use Emergency SOS if you feel unsafe or need assistance.'
        ]

    return {
        'triage_level': level,
        'actions': actions,
        'disclaimer': 'This is safety triage guidance and not a medical diagnosis.'
    }


@app.route('/api/health_triage', methods=['POST'])
def api_health_triage():
    """Health guidance endpoint.

    This endpoint is deterministic and avoids inaccurate AI/diagnosis claims.
    If a real medical AI provider is configured in the future, it can be integrated
    behind a separate provider path.
    """
    payload = request.get_json(silent=True) or {}

    symptoms = payload.get('symptoms')
    age = payload.get('age')
    pregnant = payload.get('pregnant')

    result = _health_triage(symptoms, age=age, pregnant=bool(pregnant) if pregnant is not None else None)

    return jsonify({
        'success': True,
        'status': 'ok',
        'source': 'deterministic_triage',
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'result': result
    })


@app.route('/api/crowd_data/<train_number>')
def get_crowd_data(train_number):
    """Crowd data endpoint.

    This project previously returned simulated/random occupancy, which can be misleading.
    To ensure the UI never shows inaccurate results, this endpoint now returns
    "unavailable" unless a real data source is configured.

    Configure a provider by setting environment variables and implementing the
    provider fetch below.
    """

    provider = os.environ.get('CROWD_DATA_PROVIDER', '').strip().lower()

    # If no provider configured, return clearly labeled simulated data for demo use.
    if not provider:
        # Deterministic simulation seeded on train number so values are stable per train.
        import random
        try:
            conn = sqlite3.connect('emergency_reports.db')
            cursor = conn.cursor()
            cursor.execute('SELECT train_name FROM train_database WHERE train_number = ?', (train_number,))
            row = cursor.fetchone()
            conn.close()
        except Exception:
            row = None
        train_name = row[0] if row else f'Train {train_number}'

        seed = int(hashlib.md5(str(train_number).encode('utf-8')).hexdigest(), 16) % (2**32)
        rng = random.Random(seed)

        # Decide coach composition
        sl_count = rng.randint(6, 10)   # Sleeper
        b_count = rng.randint(2, 4)     # 3A
        a_count = rng.randint(1, 2)     # 2A
        gen_count = rng.randint(1, 2)   # General

        coaches = []

        # General coaches (GEN)
        for i in range(1, gen_count + 1):
            capacity = 90
            occ = rng.randint(35, 98)
            coaches.append({
                'coach': f'GS{i}',
                'type': 'GEN',
                'capacity': capacity,
                'occupancy': occ,
                'seats_available': max(0, int(round(capacity * (100 - occ) / 100)))
            })

        # Sleeper (SL): S1..Sx
        for i in range(1, sl_count + 1):
            capacity = 72
            occ = rng.randint(30, 95)
            coaches.append({
                'coach': f'S{i}',
                'type': 'SL',
                'capacity': capacity,
                'occupancy': occ,
                'seats_available': max(0, int(round(capacity * (100 - occ) / 100)))
            })

        # AC 3-tier (3A): B1..Bx
        for i in range(1, b_count + 1):
            capacity = 64
            occ = rng.randint(25, 92)
            coaches.append({
                'coach': f'B{i}',
                'type': '3A',
                'capacity': capacity,
                'occupancy': occ,
                'seats_available': max(0, int(round(capacity * (100 - occ) / 100)))
            })

        # AC 2-tier (2A): A1..Ax
        for i in range(1, a_count + 1):
            capacity = 48
            occ = rng.randint(20, 85)
            coaches.append({
                'coach': f'A{i}',
                'type': '2A',
                'capacity': capacity,
                'occupancy': occ,
                'seats_available': max(0, int(round(capacity * (100 - occ) / 100)))
            })

        # Sort by conventional order: GS -> S -> B -> A, then numeric index
        def coach_key(c):
            prefix = c['coach'][0]
            num_str = ''.join(ch for ch in c['coach'] if ch.isdigit())
            num = int(num_str) if num_str else 0
            order = {'G': 0, 'S': 1, 'B': 2, 'A': 3}.get(prefix, 4)
            return (order, num)

        coaches.sort(key=coach_key)

        return jsonify({
            'success': True,
            'train': train_number,
            'train_name': train_name,
            'status': 'simulated',
            'message': 'Simulated occupancy for demonstration. Not real-time.',
            'source': 'simulation',
            'last_updated': datetime.utcnow().isoformat() + 'Z',
            'coaches': coaches
        })

    # Placeholder for future provider integration.
    # Example:
    # if provider == 'your_provider_name':
    #     data = fetch_crowd_from_provider(train_number)
    #     return jsonify(data)

    return jsonify({
        'success': False,
        'train': train_number,
        'status': 'unavailable',
        'message': f'Crowd provider "{provider}" is set but not implemented.',
        'source': provider,
        'last_updated': None,
        'coaches': []
    }), 503


@app.route('/api/train_comfort_score/<train_number>')
def get_train_comfort_score(train_number):
    """Comfort score endpoint.

    Previously random. Random comfort scores are inherently inaccurate.
    This endpoint now returns "unavailable" unless computed from real inputs.
    """

    provider = os.environ.get('COMFORT_SCORE_PROVIDER', '').strip().lower()
    if not provider:
        return jsonify({
            'success': False,
            'train': train_number,
            'status': 'unavailable',
            'message': 'Comfort score requires real inputs (occupancy/temperature/etc.). Not configured.',
            'source': None,
            'last_updated': None
        }), 503

    return jsonify({
        'success': False,
        'train': train_number,
        'status': 'unavailable',
        'message': f'Comfort provider "{provider}" is set but not implemented.',
        'source': provider,
        'last_updated': None
    }), 503

@app.route('/api/emergency_stats')
def get_emergency_stats():
    conn = sqlite3.connect('emergency_reports.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM emergency_reports')
    total = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM emergency_reports WHERE status = "resolved"')
    resolved = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM emergency_reports WHERE status = "pending"')
    pending = cursor.fetchone()[0]
    conn.close()
    return jsonify({'total_emergencies': total, 'resolved': resolved, 'pending': pending, 'avg_response_time_minutes': 8, 'success_rate': f"{(resolved/total*100):.1f}%" if total > 0 else "0%"})

@app.route('/alert_station_manager', methods=['POST'])
def alert_station_manager():
    """Send alert to station manager for medical arrangement"""
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 403
    
    data = request.get_json()
    station_code = data.get('station_code')
    station_name = data.get('station_name')
    emergency_type = data.get('emergency_type')
    train_number = data.get('train_number')
    train_name = data.get('train_name', '')
    eta_minutes = data.get('eta_minutes')
    report_id = data.get('report_id')
    passenger_name = data.get('passenger_name', '')
    coach = data.get('coach', '')
    seat = data.get('seat', '')
    
    # Get station manager details
    conn = sqlite3.connect('emergency_reports.db')
    cursor = conn.cursor()
    cursor.execute('SELECT station_manager_name, station_manager_phone, contact_number FROM stations WHERE station_code = ?', (station_code,))
    station_info = cursor.fetchone()
    conn.close()
    
    manager_name = station_info[0] if station_info and station_info[0] else 'Station Manager'
    manager_phone = station_info[1] if station_info and station_info[1] else (station_info[2] if station_info and station_info[2] else 'N/A')
    
    alert_message = f"""MEDICAL EMERGENCY ALERT

Report ID: #{report_id}
Train Number: {train_number}
Train Name: {train_name}
Emergency Type: {emergency_type}
Passenger: {passenger_name}
Coach: {coach}, Seat: {seat}
ETA to Station: {eta_minutes} minutes

ACTION REQUIRED:
- Arrange medical team at platform
- Prepare ambulance for immediate dispatch
- Coordinate with train crew
- Contact: {manager_phone}

This is an automated alert from Railway Emergency Response System."""
    
    print(f"ALERT SENT TO STATION {station_code} ({station_name}):")
    print(alert_message)
    print(f"Station Manager: {manager_name}")
    print(f"Contact: {manager_phone}")
    
    return jsonify({
        'success': True,
        'message': f'Station manager at {station_name} ({station_code}) alerted successfully',
        'alert_sent_to': station_code,
        'station_name': station_name,
        'manager_name': manager_name,
        'manager_phone': manager_phone,
        'alert_message': alert_message
    })

@app.route('/all_stations')
def all_stations():
    """Get all railway stations"""
    conn = sqlite3.connect('emergency_reports.db')
    cursor = conn.cursor()
    cursor.execute('SELECT station_name, station_code, latitude, longitude FROM stations ORDER BY station_name')
    stations = cursor.fetchall()
    conn.close()
    
    station_list = [{
        'name': station[0],
        'code': station[1],
        'latitude': station[2],
        'longitude': station[3]
    } for station in stations]
    
    return jsonify({'stations': station_list})

@app.route('/api/all_trains')
def api_all_trains():
    """Get all trains from database"""
    conn = sqlite3.connect('emergency_reports.db')
    cursor = conn.cursor()
    cursor.execute('SELECT train_number, train_name, source_station, destination_station, route_stations FROM train_database ORDER BY train_number')
    trains = cursor.fetchall()
    conn.close()
    
    train_list = [{
        'number': train[0],
        'name': train[1],
        'source': train[2],
        'destination': train[3],
        'route': train[4]
    } for train in trains]
    
    return jsonify({'success': True, 'trains': train_list})

@app.route('/train_database')
def train_database():
    """Train database page"""
    lang = session.get('language', 'en')
    return render_template('train_database.html', lang=lang, translations=TRANSLATIONS.get(lang, TRANSLATIONS['en']), languages=LANGUAGES)

# IRCTC-like Features
@app.route('/train_booking')
def train_booking():
    """Train booking page"""
    lang = session.get('language', 'en')
    return render_template('train_booking.html', lang=lang, translations=TRANSLATIONS.get(lang, TRANSLATIONS['en']), languages=LANGUAGES)

@app.route('/pnr_status')
def pnr_status():
    """PNR status check page"""
    lang = session.get('language', 'en')
    return render_template('pnr_status.html', lang=lang, translations=TRANSLATIONS.get(lang, TRANSLATIONS['en']), languages=LANGUAGES)

@app.route('/seat_availability')
def seat_availability():
    """Seat availability check page"""
    lang = session.get('language', 'en')
    return render_template('seat_availability.html', lang=lang, translations=TRANSLATIONS.get(lang, TRANSLATIONS['en']), languages=LANGUAGES)

@app.route('/train_schedule')
def train_schedule():
    """Train schedule page"""
    lang = session.get('language', 'en')
    return render_template('train_schedule.html', lang=lang, translations=TRANSLATIONS.get(lang, TRANSLATIONS['en']), languages=LANGUAGES)

@app.route('/fare_enquiry')
def fare_enquiry():
    """Fare enquiry page"""
    lang = session.get('language', 'en')
    return render_template('fare_enquiry.html', lang=lang, translations=TRANSLATIONS.get(lang, TRANSLATIONS['en']), languages=LANGUAGES)

@app.route('/api/check_pnr/<pnr>')
def check_pnr(pnr):
    """API endpoint to check PNR status"""
    # Simulate PNR check (in production, integrate with real IRCTC API)
    import random
    statuses = ['CNF', 'WL', 'RAC', 'CAN']
    classes = ['SL', '3A', '2A', '1A']
    
    # Generate mock PNR data
    pnr_data = {
        'pnr': pnr,
        'train_number': random.choice(['12301', '12951', '12001', '12213']),
        'train_name': random.choice(['Rajdhani Express', 'Shatabdi Express', 'Duronto Express']),
        'from_station': random.choice(['New Delhi', 'Mumbai Central', 'Chennai Central']),
        'to_station': random.choice(['Howrah', 'Bangalore', 'Hyderabad']),
        'journey_date': '2024-02-15',
        'passengers': [
            {
                'name': 'Passenger 1',
                'status': random.choice(statuses),
                'coach': f'{random.choice(classes)}{random.randint(1, 10)}',
                'seat': random.randint(1, 72)
            }
        ],
        'booking_status': random.choice(['Confirmed', 'Waiting List', 'RAC']),
        'chart_status': 'CHART PREPARED'
    }
    
    return jsonify({'success': True, 'data': pnr_data})

@app.route('/api/check_seat_availability')
def check_seat_availability():
    """API endpoint to check seat availability"""
    train_number = request.args.get('train_number')
    from_station = request.args.get('from_station')
    to_station = request.args.get('to_station')
    date = request.args.get('date')
    class_code = request.args.get('class', 'SL')
    
    # Simulate seat availability check
    import random
    availability_data = {
        'train_number': train_number,
        'train_name': 'Express Train',
        'from_station': from_station,
        'to_station': to_station,
        'date': date,
        'class': class_code,
        'availability': {
            'available': random.randint(0, 50),
            'waiting_list': random.randint(0, 20),
            'rac': random.randint(0, 10)
        },
        'fare': random.randint(500, 3000)
    }
    
    return jsonify({'success': True, 'data': availability_data})

@app.route('/api/get_train_schedule/<train_number>')
def get_train_schedule(train_number):
    """API endpoint to get train schedule"""
    conn = sqlite3.connect('emergency_reports.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM train_database WHERE train_number = ?', (train_number,))
    train_info = cursor.fetchone()
    
    if train_info:
        route_stations = train_info[4].split(',')
        schedule = []
        
        import random
        current_time = 480  # 8:00 AM in minutes
        
        for i, station in enumerate(route_stations):
            schedule.append({
                'station': station.strip(),
                'arrival': f'{current_time // 60:02d}:{current_time % 60:02d}',
                'departure': f'{(current_time + 5) // 60:02d}:{(current_time + 5) % 60:02d}',
                'halt': '5 min',
                'day': (i // 10) + 1,
                'platform': random.randint(1, 8)
            })
            current_time += random.randint(30, 120)  # Add travel time
        
        conn.close()
        return jsonify({
            'success': True,
            'train_number': train_info[0],
            'train_name': train_info[1],
            'schedule': schedule
        })
    
    conn.close()
    return jsonify({'success': False, 'message': 'Train not found'})

@app.route('/api/get_fare')
def get_fare():
    """API endpoint to get fare information"""
    train_number = request.args.get('train_number')
    from_station = request.args.get('from_station')
    to_station = request.args.get('to_station')
    class_code = request.args.get('class', 'SL')
    
    # Simulate fare calculation
    import random
    base_fares = {
        'SL': 500,
        '3A': 1200,
        '2A': 2000,
        '1A': 3500
    }
    
    base_fare = base_fares.get(class_code, 500)
    distance_factor = random.uniform(1.0, 3.0)
    fare = int(base_fare * distance_factor)
    
    fare_data = {
        'train_number': train_number,
        'from_station': from_station,
        'to_station': to_station,
        'class': class_code,
        'base_fare': fare,
        'reservation_charge': 40,
        'service_tax': int(fare * 0.05),
        'total_fare': fare + 40 + int(fare * 0.05)
    }
    
    return jsonify({'success': True, 'data': fare_data})

@app.route('/api/my_reports')
def get_my_reports():
    """Get emergency reports for logged-in user"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in', 'reports': []}), 401
    
    username = session.get('username')
    
    try:
        conn = sqlite3.connect('emergency_reports.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, passenger_name, phone, train_number, coach, seat, 
                   emergency_type, description, location, status, timestamp
            FROM emergency_reports 
            WHERE passenger_name = ? 
            ORDER BY timestamp DESC
        ''', (username,))
        reports = cursor.fetchall()
        conn.close()
        
        report_list = []
        for report in reports:
            report_list.append({
                'id': report[0],
                'passenger_name': report[1],
                'phone': report[2],
                'train_number': report[3],
                'coach': report[4],
                'seat': report[5],
                'emergency_type': report[6],
                'description': report[7],
                'location': report[8] if report[8] else 'Not provided',
                'status': report[9],
                'timestamp': report[10]
            })
        
        return jsonify({'success': True, 'reports': report_list})
    except Exception as e:
        print(f"Error fetching reports: {e}")
        return jsonify({'success': False, 'message': str(e), 'reports': []}), 500

if __name__ == '__main__':
    init_db()
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
