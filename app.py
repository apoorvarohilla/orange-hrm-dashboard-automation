from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import traceback
import logging
import csv
import io
from datetime import datetime
import threading

app = Flask(__name__)
CORS(app)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

latest_employees = []


def create_chrome_driver_with_timeout(timeout=30):

    driver_holder = {"driver": None, "error": None}

    def create_driver():
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")
            chrome_options.add_argument("--disable-software-rasterizer")
            chrome_options.add_argument("--remote-debugging-port=9222")

            service = Service(ChromeDriverManager().install())

            driver_holder["driver"] = webdriver.Chrome(
                service=service,
                options=chrome_options
            )

        except Exception as e:
            driver_holder["error"] = str(e)

    thread = threading.Thread(target=create_driver, daemon=True)
    thread.start()
    thread.join(timeout=timeout)

    if thread.is_alive():
        driver_holder["error"] = f"Chrome driver initialization timeout ({timeout}s)"

    if driver_holder["error"]:
        raise Exception(driver_holder["error"])

    return driver_holder["driver"]


def run_automation(username, password, first_name, last_name, emp_id):

    global latest_employees

    logs = []
    employees = []
    driver = None

    try:

        logs.append("Initializing browser")
        driver = create_chrome_driver_with_timeout()

        wait = WebDriverWait(driver, 20)

        logs.append("Opening OrangeHRM")

        driver.get("https://opensource-demo.orangehrmlive.com")

        wait.until(
            EC.presence_of_element_located((By.NAME, "username"))
        )

        logs.append("Entering credentials")

        driver.find_element(By.NAME, "username").send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password)

        driver.find_element(By.XPATH, "//button[@type='submit']").click()

        wait.until(
            EC.presence_of_element_located((By.XPATH, "//span[text()='PIM']"))
        )

        logs.append("Login successful")

        driver.find_element(By.XPATH, "//span[text()='PIM']").click()

        wait.until(
            EC.presence_of_element_located((By.XPATH, "//button[normalize-space()='Add']"))
        )

        driver.find_element(By.XPATH, "//button[normalize-space()='Add']").click()

        wait.until(
            EC.presence_of_element_located((By.NAME, "firstName"))
        )

        driver.find_element(By.NAME, "firstName").send_keys(first_name)
        driver.find_element(By.NAME, "lastName").send_keys(last_name)

        emp_field = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//label[text()='Employee Id']/../following-sibling::div/input")
            )
        )

        emp_field.clear()
        emp_field.send_keys(emp_id)

        driver.find_element(By.XPATH, "//button[@type='submit']").click()

        wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//h6[text()='Personal Details']")
            )
        )

        logs.append("Employee created")

        wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//a[normalize-space()='Employee List']")
            )
        ).click()

        wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@class='oxd-table-body']")
            )
        )

        rows = driver.find_elements(By.XPATH, "//div[@class='oxd-table-body']/div")

        for r in rows[:10]:

            cols = r.find_elements(By.XPATH, ".//div[@role='cell']")

            if len(cols) >= 4:

                emp = {
                    "id": cols[1].text.strip(),
                    "firstName": cols[2].text.strip(),
                    "lastName": cols[3].text.strip(),
                    "status": cols[4].text.strip() if len(cols) > 4 else "Active"
                }

                employees.append(emp)

        latest_employees = employees

        logs.append(f"Extracted {len(employees)} employees")

        try:

            driver.find_element(By.XPATH, "//span[@class='oxd-userdropdown-tab']").click()

            wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//a[text()='Logout']")
                )
            ).click()

        except:
            logs.append("Logout failed")

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

    username = data.get("username")
    password = data.get("password")
    first_name = data.get("firstName")
    last_name = data.get("lastName")
    emp_id = data.get("employeeId")

    result = run_automation(username, password, first_name, last_name, emp_id)

    return jsonify(result)


@app.route("/api/employees", methods=["GET"])
def employees():

    return jsonify({
        "employees": latest_employees,
        "count": len(latest_employees)
    })


@app.route("/api/export-csv", methods=["GET"])
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


@app.route("/api/health", methods=["GET"])
def health():

    return jsonify({
        "status": "healthy",
        "service": "OrangeHRM Automation API"
    })


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=9000, debug=True)