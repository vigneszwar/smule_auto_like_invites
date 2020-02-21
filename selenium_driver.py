from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class Driver(object):
    pass


class ChromeDriver(Driver):
    def __init__(self, path='chromedriver.exe'):
        print("Chrome driver path - " + path)
        self.driver = webdriver.Chrome(path)

    def get(self, path):
        self.driver.get(path)

    def back(self):
        self.driver.back()

    def quit(self):
        self.driver.quit()

    def ge_by_id(self, tag_id):
        return self.driver.find_element_by_id(tag_id)

    def ge_by_link_text(self, text):
        return self.driver.find_element_by_link_text(text)

    def ge_by_name(self, name):
        return self.driver.find_element_by_name(name)

    def wge_by_name(self, name):
        return WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.NAME, name)))

    def ges_by_xpath(self, path):
        return self.driver.find_elements(By.XPATH, path)

    def ge_by_xpath(self, path):
        return self.driver.find_element(By.XPATH, path)

    def ges_by_partial_link(self, text):
        return self.driver.find_elements_by_partial_link_text(text)

    def ge_by_tag_name(self, name):
        return self.driver.find_element_by_tag_name(name)

    def ge_by_class_name(self, name):
        return self.driver.find_element_by_class_name(name)

    def wge_by_class_name(self, name):
        return WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, name)))

    def wges_by_class_name(self, name):
        return WebDriverWait(self.driver, 10).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, name)))
