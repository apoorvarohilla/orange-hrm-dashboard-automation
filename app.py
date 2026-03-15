from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import csv
import io
import traceback
import time
import threading
import uuid
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Global state
latest_employees = []

# Job store: { job_id: { state, logs, employees, createdEmployee, timestamp, error } }
jobs = {}
jobs_lock = threading.Lock()


def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def append_log(job_id, message):
    """Thread-safe log appender so the frontend can poll live progress."""
    with jobs_lock:
        jobs[job_id]["logs"].append(message)


def run_automation(job_id, username, password, first_name, last_name, emp_id):
    """Runs entirely in a background thread. Updates jobs[job_id] in place."""

    global latest_employees
    driver = None

    try:
        # ── 1. Launch browser ──────────────────────────────────────────────
        append_log(job_id, "Initializing browser")
        driver = create_driver()
        wait = WebDriverWait(driver, 40)

        # ── 2. Open OrangeHRM ──────────────────────────────────────────────
        append_log(job_id, "Opening OrangeHRM site")
        driver.get("https://opensource-demo.orangehrmlive.com/web/index.php/auth/login")
        wait.until(EC.presence_of_element_located((By.NAME, "username")))

        # ── 3. Login ───────────────────────────────────────────────────────
        append_log(job_id, "Entering login credentials")
        driver.find_element(By.NAME, "username").send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        wait.until(EC.url_contains("dashboard"))
        append_log(job_id, "Login successful")
        time.sleep(2)

        # ── 4. Navigate to PIM ─────────────────────────────────────────────
        pim_menu = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='pim']"))
        )
        driver.execute_script("arguments[0].click();", pim_menu)
        append_log(job_id, "Navigated to PIM module")
        wait.until(EC.url_contains("viewEmployeeList"))

        # ── 5. Add new employee ────────────────────────────────────────────
        add_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Add']"))
        )
        driver.execute_script("arguments[0].click();", add_btn)
        append_log(job_id, "Opened Add Employee page")
        wait.until(EC.presence_of_element_located((By.NAME, "firstName")))

        append_log(job_id, "Entering employee details")
        driver.find_element(By.NAME, "firstName").send_keys(first_name)
        driver.find_element(By.NAME, "lastName").send_keys(last_name)

        emp_id_field = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "(//input[contains(@class,'oxd-input')])[4]")
            )
        )
        emp_id_field.clear()
        emp_id_field.send_keys(emp_id)

        # ── 6. Save employee ───────────────────────────────────────────────
        save_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        driver.execute_script("arguments[0].click();", save_btn)
        wait.until(EC.presence_of_element_located((By.XPATH, "//h6")))
        append_log(job_id, "Employee created successfully")

        # ── 7. Extract full employee list ──────────────────────────────────
        append_log(job_id, "Extracting employee list")
        driver.get(
            "https://opensource-demo.orangehrmlive.com/web/index.php/pim/viewEmployeeList"
        )
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "oxd-table-body")))
        time.sleep(2)

        rows = driver.find_elements(By.CSS_SELECTOR, ".oxd-table-body > div")
        employees = []

        for r in rows[:10]:
            cols = r.find_elements(By.CSS_SELECTOR, "div[role='cell']")
            # OrangeHRM columns:
            # [0]=checkbox [1]=ID [2]=First Name [3]=Last Name
            # [4]=Job Title [5]=Employment Status [6]=Sub Unit [7]=Actions
            if len(cols) >= 6:
                emp = {
                    "id": cols[1].text.strip(),
                    "firstName": cols[2].text.strip().split()[0] if cols[2].text.strip() else "",
                    "lastName": (
                        " ".join(cols[2].text.strip().split()[1:])
                        if len(cols[2].text.strip().split()) > 1
                        else cols[3].text.strip()
                    ),
                    "jobTitle": cols[4].text.strip(),
                    "status": cols[5].text.strip()
                }
                employees.append(emp)

        latest_employees = employees
        append_log(job_id, f"Extracted {len(employees)} employees from list")

        # ── 8. Logout ──────────────────────────────────────────────────────
        append_log(job_id, "Logging out")
        driver.get(
            "https://opensource-demo.orangehrmlive.com/web/index.php/auth/logout"
        )
        wait.until(EC.presence_of_element_located((By.NAME, "username")))
        append_log(job_id, "Logged out successfully")

        driver.quit()

        # ── 9. Mark job done ───────────────────────────────────────────────
        with jobs_lock:
            jobs[job_id].update({
                "state": "done",
                "employees": employees,
                "createdEmployee": {
                    "firstName": first_name,
                    "lastName": last_name,
                    "employeeId": emp_id
                },
                "timestamp": datetime.now().isoformat()
            })

    except Exception as e:
        append_log(job_id, "Automation failed")
        append_log(job_id, str(e))
        append_log(job_id, traceback.format_exc())

        if driver:
            try:
                driver.quit()
            except Exception:
                pass

        with jobs_lock:
            jobs[job_id].update({
                "state": "error",
                "error": str(e)
            })


# ── Routes ─────────────────────────────────────────────────────────────────

@app.route("/api/run", methods=["POST"])
def run():
    data = request.get_json(force=True, silent=True) or {}

    required_fields = ["username", "password", "firstName", "lastName", "employeeId"]
    missing = [f for f in required_fields if not data.get(f)]
    if missing:
        return jsonify({
            "status": "error",
            "error": f"Missing required fields: {', '.join(missing)}"
        }), 400

    job_id = str(uuid.uuid4())

    with jobs_lock:
        jobs[job_id] = {
            "state": "running",
            "logs": [],
            "employees": [],
            "createdEmployee": None,
            "timestamp": None,
            "error": None
        }

    thread = threading.Thread(
        target=run_automation,
        args=(
            job_id,
            data["username"],
            data["password"],
            data["firstName"],
            data["lastName"],
            data["employeeId"]
        ),
        daemon=True
    )
    thread.start()

    return jsonify({"status": "accepted", "jobId": job_id}), 202


@app.route("/api/status/<job_id>", methods=["GET"])
def job_status(job_id):
    """Poll this endpoint to get live logs and the final result."""
    with jobs_lock:
        job = jobs.get(job_id)

    if not job:
        return jsonify({"error": "Job not found"}), 404

    return jsonify({
        "jobId": job_id,
        "state": job["state"],
        "logs": job["logs"],
        "employees": job["employees"],
        "createdEmployee": job["createdEmployee"],
        "timestamp": job["timestamp"],
        "error": job["error"]
    })


@app.route("/api/employees")
def employees():
    return jsonify({
        "employees": latest_employees,
        "count": len(latest_employees)
    })


@app.route("/api/export-csv")
def export_csv():
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["id", "firstName", "lastName", "jobTitle", "status"]
    )
    writer.writeheader()
    writer.writerows(latest_employees)

    mem = io.BytesIO()
    mem.write(output.getvalue().encode("utf-8"))
    mem.seek(0)

    filename = f"employees_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return send_file(
        mem,
        mimetype="text/csv",
        as_attachment=True,
        download_name=filename
    )


@app.route("/api/health")
def health():
    return jsonify({"status": "healthy"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000, debug=False, threaded=True)