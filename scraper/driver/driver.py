from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
import os

def get_driver(proxy=None):
    profile = webdriver.FirefoxProfile()
    profile.set_preference("network.http.pipelining", True)
    profile.set_preference("network.http.proxy.pipelining", True)
    profile.set_preference("network.http.pipelining.maxrequests", 8)
    profile.set_preference("content.notify.interval", 500000)
    profile.set_preference("content.notify.ontimer", True)
    profile.set_preference("content.switch.threshold", 250000)
    profile.set_preference("browser.cache.memory.capacity", 65536) # Increase the cache capacity.
    profile.set_preference("browser.startup.homepage", "about:blank")
    profile.set_preference("reader.parse-on-load.enabled", False) # Disable reader, we won't need that.
    profile.set_preference("browser.pocket.enabled", False) # Duck pocket too!
    profile.set_preference("loop.enabled", False)
    profile.set_preference("browser.chrome.toolbar_style", 1) # Text on Toolbar instead of icons
    profile.set_preference("browser.display.show_image_placeholders", False) # Don't show thumbnails on not loaded images.
    profile.set_preference("browser.display.use_document_colors", False) # Don't show document colors.
    profile.set_preference("browser.display.use_document_fonts", 0) # Don't load document fonts.
    profile.set_preference("browser.display.use_system_colors", True) # Use system colors.
    profile.set_preference("browser.formfill.enable", False) # Autofill on forms disabled.
    profile.set_preference("browser.helperApps.deleteTempFileOnExit", True) # Delete temprorary files.
    profile.set_preference("browser.shell.checkDefaultBrowser", False)
    profile.set_preference("browser.startup.homepage", "about:blank")
    profile.set_preference("browser.startup.page", 0) # blank
    profile.set_preference("browser.tabs.forceHide", True) # Disable tabs, We won't need that.
    profile.set_preference("browser.urlbar.autoFill", False) # Disable autofill on URL bar.
    profile.set_preference("browser.urlbar.autocomplete.enabled", False) # Disable autocomplete on URL bar.
    profile.set_preference("browser.urlbar.showPopup", False) # Disable list of URLs when typing on URL bar.
    profile.set_preference("browser.urlbar.showSearch", False) # Disable search bar.
    profile.set_preference("extensions.checkCompatibility", False) # Addon update disabled
    profile.set_preference("extensions.checkUpdateSecurity", False)
    profile.set_preference("extensions.update.autoUpdateEnabled", False)
    profile.set_preference("extensions.update.enabled", False)
    profile.set_preference("general.startup.browser", False)
    profile.set_preference("plugin.default_plugin_disabled", False)
    profile.set_preference("permissions.default.image", 2) # Image load disabled again
    profile.set_preference("permissions.default.stylesheet", 2)
    profile.set_preference("javascript.enabled", False)
    options = webdriver.FirefoxOptions()
    options.add_argument('--lang=en-GB')
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-notifications")
    #options.add_experimental_option('excludeSwitches', ['enable-logging'])
    if proxy:
        options.add_argument("--proxy-server=" + proxy)
    driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(), firefox_profile=profile, options=options, service_log_path=os.devnull)

    return driver
