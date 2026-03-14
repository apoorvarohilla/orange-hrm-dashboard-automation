# System Architecture & Flow Diagram

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER BROWSER                                 │
│                     localhost:5173                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │ React Dashboard   │
                    ├─────────────────┤
                    │ AutomationForm  │
                    │ StatusPanel     │
                    │ EmployeeTable   │
                    └────────┬────────┘
                             │
                    HTTP/JSON │ POST /api/run
                             │ GET /api/employees
                             │ GET /api/export-csv
                             │
┌────────────────────────────┼────────────────────────────┐
│                            │                            │
│                 ┌──────────▼──────────┐                 │
│                 │  Flask Backend      │                 │
│                 │  localhost:9000     │                 │
│                 ├────────────────────┤                 │
│                 │ • Request Handler   │                 │
│                 │ • Error Handling    │                 │
│                 │ • Logging           │                 │
│                 │ • CSV Export        │                 │
│                 └──────────┬──────────┘                 │
│                            │                            │
│                            │ selenium/webdriver        │
│                 ┌──────────▼──────────┐                 │
│                 │  Browser Automation │                 │
│                 ├────────────────────┤                 │
│                 │ • Launch Chrome     │                 │
│                 │ • Navigate & Wait   │                 │
│                 │ • Fill Forms        │                 │
│                 │ • Extract Data      │                 │
│                 │ • Handle Errors     │                 │
│                 └──────────┬──────────┘                 │
│                            │                            │
└────────────────────────────┼────────────────────────────┘
                             │
                 HTTPS ┌──────▼──────────┐
                       │  OrangeHRM      │
                       │  Demo Site      │
                       │                 │
                       │ + Login         │
                       │ + PIM Module    │
                       │ + Add Employee  │
                       │ + List Employees│
                       │ + Logout        │
                       └─────────────────┘
```

## 🔄 Data Flow Sequence

```
1. USER INTERACTION
   └─→ Fill dashboard form (credentials, employee details)
       └─→ Click "Trigger Automation"

2. FRONTEND PROCESSING
   └─→ Validate required fields
       └─→ Send POST request to /api/run
           └─→ JSON payload with all data

3. BACKEND PROCESSING
   └─→ Receive request
       └─→ Launch Chrome browser
           └─→ Navigate to OrangeHRM
               └─→ Wait for login form
                   └─→ Enter credentials
                       └─→ Submit login
                           └─→ Wait for navigation
                               └─→ Navigate to PIM
                                   └─→ Click Add Employee
                                       └─→ Fill employee form
                                           └─→ Submit form
                                               └─→ Verify creation
                                                   └─→ Extract employee list
                                                       └─→ Logout
                                                           └─→ Close browser

4. FRONTEND DISPLAY
   └─→ Display logs in real-time
       └─→ Show created employee info
           └─→ Populate employee table
               └─→ Enable CSV export button

5. USER EXPORTS DATA
   └─→ Click "Export as CSV"
       └─→ Download employees_{timestamp}.csv
```

## 📊 Component Hierarchy

```
App (src/pages/Index.tsx)
│
├── Header
│   └── Title + Status Badge
│
├── Main Grid
│   │
│   ├── Left Column (380px)
│   │   ├── AutomationForm
│   │   │   ├── Username Input
│   │   │   ├── Password Input
│   │   │   ├── First Name Input
│   │   │   ├── Last Name Input
│   │   │   ├── Employee ID Input
│   │   │   └── Submit Button
│   │   │
│   │   ├── Created Employee Panel
│   │   │   └── Employee Details Display
│   │   │
│   │   └── Export CSV Button
│   │
│   └── Right Column (Flexible)
│       ├── StatusPanel
│       │   ├── Header with Status
│       │   └── Log List
│       │       └── Log Entries (info/success/error/warning)
│       │
│       └── EmployeeTable (conditional)
│           ├── Table Header
│           │   ├── # (index)
│           │   ├── Employee ID
│           │   ├── First Name
│           │   ├── Last Name
│           │   └── Status
│           │
│           └── Table Rows
│               └── Employee Entries
```

## 🔌 API Endpoint Architecture

```
HTTP Requests
    │
    ├─→ POST /api/run
    │   Input: { username, password, firstName, lastName, employeeId }
    │   Process: Selenium automation
    │   Output: { status, logs, employees, createdEmployee, timestamp }
    │
    ├─→ GET /api/employees
    │   Input: None
    │   Process: Return latest extracted employees
    │   Output: { status, employees, count, timestamp }
    │
    ├─→ GET /api/export-csv
    │   Input: None
    │   Process: Generate CSV from latest employees
    │   Output: .csv file download
    │
    └─→ GET /api/health
        Input: None
        Process: Check service health
        Output: { status, service, version, timestamp }
```

## 🧵 Control Flow - Automation Run

```
Request arrives at /api/run
    │
    ├─→ Validate input data
    │   └─→ Check all required fields present
    │
    ├─→ Launch Chrome Browser
    │   ├─→ Set headless mode
    │   ├─→ Set window size
    │   ├─→ Disable GPU
    │   └─→ Disable sandbox
    │
    ├─→ Navigate to OrangeHRM
    │   └─→ Wait for page load
    │
    ├─→ Login Flow
    │   ├─→ Find username field (By.NAME = "username")
    │   ├─→ Send username
    │   ├─→ Find password field (By.NAME = "password")
    │   ├─→ Send password
    │   ├─→ Find submit button
    │   ├─→ Click submit
    │   └─→ Wait for PIM link existence (indicates successful login)
    │
    ├─→ Navigate to PIM
    │   ├─→ Find and click PIM link
    │   └─→ Wait for Add button
    │
    ├─→ Add Employee Flow
    │   ├─→ Click Add button
    │   ├─→ Wait for form
    │   ├─→ Find and fill firstName field
    │   ├─→ Find and fill lastName field
    │   ├─→ Find and clear employeeId field
    │   ├─→ Send employeeId
    │   ├─→ Click submit button
    │   └─→ Wait for Personal Details header
    │
    ├─→ Extract Employee List
    │   ├─→ Click Employee List link
    │   ├─→ Wait for table
    │   ├─→ Find all table rows
    │   └─→ Extract: id, firstName, lastName, status from each row
    │
    ├─→ Logout Flow
    │   ├─→ Click user dropdown
    │   ├─→ Find and click Logout
    │   └─→ Wait for logout to complete
    │
    ├─→ Close Browser
    │
    └─→ Return Response
        {
            status: "success",
            logs: [...],
            employees: [...],
            createdEmployee: {...},
            timestamp: "..."
        }
```

## 🛡️ Error Handling Flow

```
Error Occurs During Automation
    │
    ├─→ Catch Exception
    │   └─→ Capture error message & traceback
    │
    ├─→ Log Error
    │   ├─→ Write to automation.log
    │   └─→ Print to console
    │
    ├─→ Cleanup
    │   └─→ Close browser if open
    │
    └─→ Return Error Response
        {
            status: "error",
            logs: [...],
            employees: [],
            error: "error message",
            timestamp: "..."
        }
```

## 📝 Logging Architecture

```
Logs Generated
    │
    ├─→ Backend Process (app.py)
    │   ├─→ Console Output (stdout)
    │   │   Format: [timestamp] [level] message
    │   │
    │   └─→ File Output (automation.log)
    │       ├─→ Each request logged
    │       ├─→ Each step logged
    │       └─→ Errors with full traceback
    │
    └─→ Frontend Display (StatusPanel)
        ├─→ Real-time log entries
        ├─→ Color-coded by type
        │   ├─→ info (gray)
        │   ├─→ success (green)
        │   ├─→ error (red)
        │   └─→ warning (yellow)
        └─→ Auto-scroll to latest
```

## 🔄 State Management

```
Frontend State (React)
│
├── isRunning (boolean)
│   └─→ Controls form disable state
│       └─→ Controls button state (Running... vs Trigger)
│
├── logs (LogEntry[])
│   └─→ Updated on each backend message
│       └─→ Displayed in StatusPanel
│           └─→ Auto-scrolls to bottom
│
├── employees (Employee[])
│   └─→ Updated on successful automation
│       └─→ Displayed in EmployeeTable
│           └─→ Enables CSV export button
│
└── createdEmployee (FormData | null)
    └─→ Displayed in success panel
        └─→ Shows human-readable confirmation
```

## 💾 Data Models

```
FormData (Frontend)
├── username: string
├── password: string
├── firstName: string
├── lastName: string
└── employeeId: string

Employee (Extracted)
├── id: string (employee ID)
├── firstName: string
├── lastName: string
└── status: string

LogEntry (Frontend Display)
├── message: string
├── type: "info" | "success" | "error" | "warning"
└── timestamp: string (HH:MM:SS)

API Response (Success)
├── status: "success"
├── logs: string[]
├── employees: Employee[]
├── createdEmployee: FormData
└── timestamp: ISO string

API Response (Error)
├── status: "error"
├── logs: string[] (partial execution)
├── employees: []
├── error: string
└── timestamp: ISO string
```

## 🚀 Request/Response Cycle

```
┌─────────────────────────────────────────────────────────┐
│ 1. Frontend Form Submission                             │
│    Time: 0ms                                            │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│ 2. HTTP POST /api/run                                   │
│    Time: ~50ms                                          │
│    Payload: { username, password, firstName, ... }     │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│ 3. Backend Processing (async)                           │
│    Time: ~30-60 seconds (typical)                       │
│    - Launch browser                                     │
│    - Navigate & login                                   │
│    - Create employee                                    │
│    - Extract list                                       │
│    - Logout & cleanup                                   │
└─────────────────────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
    Logs sent       Status sent      Data sent
    (streamed)      (final)          (extracted)
         │               │               │
         └───────────────┴───────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│ 4. Frontend Display Update                              │
│    Time: Real-time + final update                      │
│    - Logs appear as received                            │
│    - Table populates                                    │
│    - Export button enabled                              │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│ 5. User Can Export or Run Again                         │
│    Time: User decides                                   │
└─────────────────────────────────────────────────────────┘
```

## 🎯 Key Design Principles

1. **Separation of Concerns**
   - Frontend handles UI only
   - Backend handles automation only
   - Clear API boundary between them

2. **Real-time Feedback**
   - Logs stream to frontend
   - User sees progress instantly
   - Better UX than polling

3. **Error Resilience**
   - Try-catch at all levels
   - Partial failure doesn't crash
   - Informative error messages

4. **Proper Resource Cleanup**
   - Browser always closes
   - Connections properly released
   - Logs persisted to file

5. **Scalability Ready**
   - Stateless API design
   - Can add queue for multiple runs
   - Database-ready data models

---

**Architecture Version:** 1.0  
**Last Updated:** March 2024  
**Status:** Production Ready ✅
