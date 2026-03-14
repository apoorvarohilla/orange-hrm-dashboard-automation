
# OrangeHRM Dashboard-Driven Automation

A comprehensive RPA solution for automating employee operations on the OrangeHRM platform through a dashboard interface.

## Features

- **Dashboard Interface**: User-friendly React dashboard for entering automation parameters
- **Automated Login**: Secure credential-based authentication on OrangeHRM
- **Employee Management**: Add new employees to the system via automation
- **Data Extraction**: Extract and display employee data in table format
- **Logging System**: Detailed logs of each automation step
- **CSV Export**: Export employee data as CSV files

## Getting Started

### Prerequisites

- Node.js & npm (https://nodejs.org/)
- Python 3.8+ with pip
- Chrome/Chromium browser for Selenium/Playwright

### Installation

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
   pip install flask flask-cors selenium python-dotenv
   ```

### Running the Application

1. **Start the frontend development server:**
   ```sh
   npm run dev
   ```
   The frontend will be available at `http://localhost:5173`

2. **Start the Flask backend server (in a separate terminal):**
   ```sh
   python app.py
   ```
   The backend will run on `http://localhost:9000`

## Tech Stack

- **Frontend**: React, TypeScript, Vite, Tailwind CSS, shadcn-ui
- **Backend**: Flask, Python
- **Browser Automation**: Playwright/Selenium
- **Testing**: Playwright, Vitest

## Project Structure

```
├── src/
│   ├── components/     # React components
│   ├── pages/          # Page components
│   ├── lib/            # Utilities
│   └── test/           # Tests
├── app.py              # Flask backend
├── vite.config.ts      # Vite configuration
└── playwright.config.ts # Playwright configuration
```

## Environment Variables

Create a `.env` file in the project root:

```
FLASK_ENV=development
FLASK_DEBUG=True
```

## Usage

1. Fill in the automation form with:
   - Username and Password for OrangeHRM
   - First Name and Last Name of the employee
   - Employee ID

2. Click "Trigger Automation"

3. Monitor the execution logs in real-time

4. View the created employee in the results table

## API Endpoints

- `POST /api/run` - Trigger automation with provided parameters
- `GET /api/employees` - Get extracted employee list

## Testing

Run tests with:
```sh
npm run test
npm run test:watch
```

## Built With

- **Vite** - Fast build tool and dev server
- **React** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **shadcn-ui** - Accessible component library
- **Flask** - Python web framework
- **Playwright** - Browser automation
