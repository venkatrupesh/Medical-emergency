# Train API Configuration
# Replace with your actual API keys

# Option 1: RailwayAPI.com (Free tier: 500 requests/day)
RAILWAY_API_KEY = "YOUR_RAILWAY_API_KEY"
RAILWAY_API_URL = "https://indianrailapi.com/api/v2"

# Option 2: RapidAPI Indian Railway (Free tier: 100 requests/month)
RAPIDAPI_KEY = "YOUR_RAPIDAPI_KEY"
RAPIDAPI_HOST = "indian-railway-api.p.rapidapi.com"

# Option 3: IRCTC/Indian Railways Official (Requires registration)
IRCTC_API_KEY = "YOUR_IRCTC_API_KEY"

# Option 4: Where Is My Train API (Free with registration)
WIMT_API_KEY = "YOUR_WIMT_API_KEY"

# API Endpoints
TRAIN_INFO_ENDPOINT = "/TrainInformation"
TRAIN_SCHEDULE_ENDPOINT = "/TrainSchedule"
LIVE_STATION_ENDPOINT = "/LiveStation"

# Fallback to simulation if APIs fail
USE_SIMULATION_FALLBACK = True