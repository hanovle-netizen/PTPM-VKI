from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

URL = "https://www.globalsqa.com/angularJs-protractor/SimpleCalculator/"


class CalculatorPage:
    _FIRST_INPUT = (By.CSS_SELECTOR, "input[ng-model='a']")
    _SECOND_INPUT = (By.CSS_SELECTOR, "input[ng-model='b']")
    _OPERATION = (By.CSS_SELECTOR, "select[ng-model='operation']")
    _INC_A = (By.CSS_SELECTOR, "button[ng-click='inca()']")
    _DEC_A = (By.CSS_SELECTOR, "button[ng-click='deca()']")
    _INC_B = (By.CSS_SELECTOR, "button[ng-click='incb()']")
    _DEC_B = (By.CSS_SELECTOR, "button[ng-click='decb()']")
    _RESULT = (By.CSS_SELECTOR, "b.result")

    def __init__(self, driver, timeout=15):
        self._driver = driver
        self._wait = WebDriverWait(driver, timeout)

    def open(self):
        self._driver.get(URL)
        self._wait.until(EC.visibility_of_element_located(self._FIRST_INPUT))
        return self

    def _type(self, locator, value):
        field = self._wait.until(EC.visibility_of_element_located(locator))
        field.clear()
        field.send_keys(str(value))

    def _click(self, locator):
        self._wait.until(EC.element_to_be_clickable(locator)).click()

    def enter_first_number(self, value):
        self._type(self._FIRST_INPUT, value)

    def enter_second_number(self, value):
        self._type(self._SECOND_INPUT, value)

    def select_operation(self, operation):
        Select(self._wait.until(EC.visibility_of_element_located(self._OPERATION))) \
            .select_by_visible_text(operation)

    def increment_first(self):
        self._click(self._INC_A)

    def decrement_first(self):
        self._click(self._DEC_A)

    def increment_second(self):
        self._click(self._INC_B)

    def decrement_second(self):
        self._click(self._DEC_B)

    def get_first_value(self):
        return self._driver.find_element(*self._FIRST_INPUT).get_attribute("value")

    def get_second_value(self):
        return self._driver.find_element(*self._SECOND_INPUT).get_attribute("value")

    def get_available_operations(self):
        return [o.text for o in Select(self._driver.find_element(*self._OPERATION)).options]

    def get_result_text(self):
        """Полный текст результата, например '2 + 3 = 5'."""
        return self._driver.find_element(*self._RESULT).text

    def get_result(self):
        """Только значение после знака '='."""
        return self.get_result_text().rsplit("=", 1)[1].strip()

    def calculate(self, first, operation, second):
        self.enter_first_number(first)
        self.select_operation(operation)
        self.enter_second_number(second)
        return self.get_result()
