# Installation & Setup Guide

## System Requirements
- Node.js 16+ and npm/bun
- Python 3.8+
- Chrome/Chromium browser (for Selenium)
- pip (Python package manager)

## Quick Start

### 1. Install Frontend Dependencies
```bash
npm install
# or if using bun
bun install
```

### 2. Install Backend Dependencies
```bash
pip install -r requirements.txt
```

### 3. Create Environment File
```bash
cp .env.example .env
```

### 4. Start the Frontend Development Server
```bash
npm run dev
```
Frontend will be available at: **http://localhost:5173**

### 5. Start the Backend Server (in a new terminal)
```bash
python app.py
```
Backend API will be available at: **http://localhost:9000**

## Project Structure

```
.
├── src/                    # React frontend source
│   ├── components/        # Reusable UI components
│   ├── pages/             # Page components
│   └── lib/               # Utility functions
├── app.py                 # Flask backend main file
├── requirements.txt       # Python dependencies
├── package.json           # Node dependencies
├── vite.config.ts         # Vite configuration
└── playwright.config.ts   # Playwright test configuration
```

## Backend API Endpoints

### POST /api/run
Triggers the automation process
**Body:**
```json
{
  "username": "Admin",
  "password": "admin123",
  "firstName": "John",
  "lastName": "Doe",
  "employeeId": "EMP-0042"
}
```

**Response:**
```json
{
  "status": "success",
  "logs": [...],
  "employees": [...],
  "createdEmployee": {...},
  "timestamp": "2024-..."
}
```

### GET /api/employees
Get the latest extracted employee list

### GET /api/export-csv
Download employee data as CSV file

### GET /api/health
Health check endpoint

## Running Tests

```bash
# Run all tests once
npm run test

# Run tests in watch mode
npm run test:watch
```

## Building for Production

```bash
# Build frontend
npm run build

# Start production backend
FLASK_ENV=production python app.py
```

## Troubleshooting

### Port 9000 Already in Use
```bash
# Windows: Find and kill process on port 9000
netstat -ano | findstr :9000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -i :9000
kill -9 <PID>
```

### Chrome Driver Issues
Make sure Chrome/Chromium is installed. Selenium will attempt to download the appropriate driver automatically.

### CORS Errors
The backend includes CORS headers. Make sure the frontend is accessing the backend at `http://localhost:9000`

### Connection Refused
Ensure the backend is running before triggering automation from the frontend

## Dashboard Features

1. **Automation Form**
   - Enter OrangeHRM credentials
   - Specify employee details (First/Last name, ID)
   - View real-time status logs

2. **Status Panel**
   - Live automation logs with timestamps
   - Color-coded messages (info, success, error, warning)
   - Auto-scrolling to latest log

3. **Employee Table**
   - Display extracted employee data
   - Shows employee ID, name, and status

4. **CSV Export**
   - Download employee list as CSV file
   - Timestamped filename

## Logs

- **Frontend**: Browser console (F12)
- **Backend**: 
  - Console output
  - `automation.log` file in project root

## Notes

- Credentials are **not** stored anywhere
- Each automation run is independent
- Employee data is extracted from the OrangeHRM employee list
- The default demo credentials are: `Admin` / `admin123`

## Support

For issues or questions, refer to the main README.md file or check the automation logs for detailed error messages.
