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
from datetime import datetime

app = Flask(__name__)
CORS(app)

latest_employees = []


def create_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    return driver


def run_automation(username, password, first_name, last_name, emp_id):

    global latest_employees

    logs = []
    employees = []
    driver = None

    try:

        logs.append("Initializing browser")

        driver = create_driver()
        wait = WebDriverWait(driver, 40)

        logs.append("Opening OrangeHRM site")

        driver.get("https://opensource-demo.orangehrmlive.com/web/index.php/auth/login")

        wait.until(EC.presence_of_element_located((By.NAME, "username")))

        logs.append("Entering login credentials")

        driver.find_element(By.NAME, "username").send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password)

        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        wait.until(EC.url_contains("dashboard"))

        logs.append("Login successful")

        time.sleep(2)

        pim_menu = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='pim']"))
        )

        driver.execute_script("arguments[0].click();", pim_menu)

        logs.append("Opened PIM module")

        wait.until(EC.url_contains("viewEmployeeList"))

        add_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Add']"))
        )

        driver.execute_script("arguments[0].click();", add_btn)

        logs.append("Opened Add Employee page")

        wait.until(EC.presence_of_element_located((By.NAME, "firstName")))

        logs.append("Entering employee details")

        driver.find_element(By.NAME, "firstName").send_keys(first_name)

        driver.find_element(By.NAME, "lastName").send_keys(last_name)

        # Correct Employee ID field (4th input)
        emp_id_field = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "(//input[contains(@class,'oxd-input')])[4]")
            )
        )

        emp_id_field.clear()
        emp_id_field.send_keys(emp_id)

        save_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )

        driver.execute_script("arguments[0].click();", save_btn)

        wait.until(EC.presence_of_element_located((By.XPATH, "//h6")))

        logs.append("Employee created successfully")

        driver.get(
            "https://opensource-demo.orangehrmlive.com/web/index.php/pim/viewEmployeeList"
        )

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "oxd-table-body")))

        rows = driver.find_elements(By.CSS_SELECTOR, ".oxd-table-body > div")

        for r in rows[:10]:

            cols = r.find_elements(By.CSS_SELECTOR, "div[role='cell']")

            if len(cols) >= 4:

                emp = {
                    "id": cols[1].text.strip(),
                    "firstName": cols[2].text.strip(),
                    "lastName": cols[3].text.strip(),
                    "status": cols[4].text.strip()
                }

                employees.append(emp)

        latest_employees = employees

        logs.append(f"Extracted {len(employees)} employees")

        driver.quit()

        return {
            "status": "success",
            "logs": logs,
            "employees": employees,
            "createdEmployee": {
                "firstName": first_name,
                "lastName": last_name,
                "employeeId": emp_id
            },
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:

        logs.append("Automation failed")
        logs.append(str(e))
        logs.append(traceback.format_exc())

        if driver:
            driver.quit()

        return {
            "status": "error",
            "logs": logs,
            "employees": [],
            "error": str(e)
        }


@app.route("/api/run", methods=["POST"])
def run():

    data = request.json

    result = run_automation(
        data.get("username"),
        data.get("password"),
        data.get("firstName"),
        data.get("lastName"),
        data.get("employeeId")
    )

    return jsonify(result)


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
        fieldnames=["id", "firstName", "lastName", "status"]
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
    app.run(host="0.0.0.0", port=9000, debug=True)