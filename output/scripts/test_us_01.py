# US: US-01

from playwright.sync_api import sync_playwright, expect

# TC: Us01 Tc01
def test_us01_tc01():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000')
        expect(page).to_have_title('Home Page')
        expect(page.locator('#header')).to_be_visible()
        browser.close()

# TC: Us01 Tc02
def test_us01_tc02():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000/login')
        expect(page).to_have_title('Login Page')
        expect(page.locator('#login-email')).to_be_visible()
        browser.close()

# TC: Us01 Tc03
def test_us01_tc03():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000/register')
        expect(page).to_have_title('Register Page')
        expect(page.locator('#email')).to_be_visible()
        browser.close()

# TC: Us01 Tc04
def test_us01_tc04():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000/profile')
        expect(page).to_have_title('Profile Page')
        expect(page.locator('#profile-info')).to_be_visible()
        browser.close()