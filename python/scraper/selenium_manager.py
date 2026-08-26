"""
Selenium Manager:
Initializes and manages headless Chrome / Edge WebDrivers with anti-detection flags and explicit wait helpers.
"""

import sys
import os
import time
import logging
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

class SeleniumManager:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver: Optional[webdriver.Remote] = None

    def create_driver(self) -> webdriver.Remote:
        # Try Chrome first, then Edge as fallback
        try:
            options = ChromeOptions()
            if self.headless:
                options.add_argument("--headless=new")
            options.add_argument(f"user-agent={USER_AGENT}")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--log-level=3")
            options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
            options.add_experimental_option("useAutomationExtension", False)

            # Disable image loading for faster scraping performance
            prefs = {
                "profile.managed_default_content_settings.images": 2,
                "profile.default_content_setting_values.notifications": 2
            }
            options.add_experimental_option("prefs", prefs)

            driver = webdriver.Chrome(options=options)
            driver.set_page_load_timeout(30)
            self.driver = driver
            return driver
        except Exception as chrome_err:
            # Fallback to Edge
            try:
                edge_options = EdgeOptions()
                if self.headless:
                    edge_options.add_argument("--headless=new")
                edge_options.add_argument(f"user-agent={USER_AGENT}")
                edge_options.add_argument("--disable-gpu")
                edge_options.add_argument("--no-sandbox")
                edge_options.add_argument("--disable-dev-shm-usage")
                edge_options.add_argument("--window-size=1920,1080")
                edge_options.add_argument("--disable-blink-features=AutomationControlled")
                edge_options.add_argument("--log-level=3")
                edge_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
                edge_options.add_experimental_option("useAutomationExtension", False)

                driver = webdriver.Edge(options=edge_options)
                driver.set_page_load_timeout(30)
                self.driver = driver
                return driver
            except Exception as edge_err:
                raise RuntimeError(f"Could not start Chrome or Edge WebDriver. Chrome error: {chrome_err}; Edge error: {edge_err}")

    def safe_quit(self):
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None

    def wait_for_element(self, by: By, selector: str, timeout: int = 10):
        if not self.driver:
            return None
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )

    def scroll_into_view(self, element):
        if self.driver and element:
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
