# OrangeHRM Dashboard-Driven Automation

An RPA solution for automating employee operations on OrangeHRM through a React dashboard.

## Features

- **Dashboard Interface**: React dashboard for entering automation parameters
- **Automated Login**: Credential-based authentication on OrangeHRM
- **Employee Management**: Add new employees via automation
- **Data Extraction**: Extract and display employee list in table format
- **Live Logs**: Real-time logs of each automation step
- **CSV Export**: Export extracted employee data as CSV

## Prerequisites

- Node.js & npm.
- Python 3.8+
- Google Chrome browser

## Installation

1. **Clone the repository:**
   ```sh
   git clone <YOUR_GIT_URL>
   cd <PROJECT_DIRECTORY>
   ```

2. **Install frontend dependencies:**
   ```sh
   npm install
   ```

3. **Install backend dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

## Running the Application

Start both servers in separate terminals:

1. **Backend:**
   ```sh
   python app.py
   ```
   Runs on `http://localhost:9000`

2. **Frontend:**
   ```sh
   npm run dev
   ```
   Runs on `http://localhost:5173`

## Usage

1. Open `http://localhost:5173` in your browser
2. Fill in the form:
   - OrangeHRM username and password
   - First Name, Last Name, Employee ID
3. Click **Trigger Automation**
4. Monitor real-time logs
5. View extracted employee table and click **Export as CSV**

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/run` | Trigger automation |
| GET | `/api/status/<job_id>` | Poll job status and logs |
| GET | `/api/employees` | Get extracted employee list |
| GET | `/api/export-csv` | Download employee data as CSV |
| GET | `/api/health` | Health check |

## Project Structure

```
├── src/
│   ├── components/         # React components
│   │   ├── AutomationForm  # Input form
│   │   ├── StatusPanel     # Live logs panel
│   │   └── EmployeeTable   # Results table
│   └── pages/
│       └── Index.tsx       # Main dashboard page
├── app.py                  # Flask backend + Selenium automation
├── requirements.txt        # Python dependencies
└── vite.config.ts          # Vite configuration
```

## Tech Stack

- **Frontend**: React, TypeScript, Vite, Tailwind CSS, shadcn-ui
- **Backend**: Flask, Python
- **Automation**: Selenium, webdriver-manager
