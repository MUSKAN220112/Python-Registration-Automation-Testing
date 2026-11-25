from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as expected
from selenium.webdriver.support.ui import Select, WebDriverWait


class RegistrationPage:
    URL = "/register"
    FIELD_IDS = (
        "first_name", "last_name", "email", "mobile_number", "password",
        "confirm_password", "date_of_birth", "address", "country", "state",
        "city", "postal_code",
    )

    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.wait = WebDriverWait(driver, 10)

    def open(self):
        self.driver.get(self.base_url + self.URL)
        self.wait.until(expected.visibility_of_element_located((By.ID, "first_name")))
        return self

    def fill(self, data):
        for field in self.FIELD_IDS:
            element = self.driver.find_element(By.ID, field)
            element.clear()
            element.send_keys(str(data.get(field, "")))
        Select(self.driver.find_element(By.ID, "gender")).select_by_value(data.get("gender", ""))
        checkbox = self.driver.find_element(By.NAME, "terms_accepted")
        if bool(data.get("terms_accepted")) != checkbox.is_selected():
            checkbox.click()
        return self

    def submit(self):
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        return self

    def reset(self):
        self.driver.find_element(By.CSS_SELECTOR, "button[type='reset']").click()
        return self

    def status_text(self):
        nodes = self.driver.find_elements(By.CSS_SELECTOR, "[role='status'], [role='alert']")
        self.wait.until(lambda driver: any(node.is_displayed() for node in nodes))
        return " ".join(node.text for node in nodes if node.is_displayed())
