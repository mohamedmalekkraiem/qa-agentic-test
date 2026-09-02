# US: US-09

from playwright.sync_api import sync_playwright, expect

# TC: Us09 Tc01
def test_us09_tc01():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000')
        expect(page).to_have_title('Home')
        expect(page.locator('#login-link')).to_be_visible()
        browser.close()

# TC: Us09 Tc02
def test_us09_tc02():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000')
        page.click('text=Login')
        expect(page).to_have_url('http://localhost:8000/login')
        expect(page.locator('#login-email')).to_be_visible()
        browser.close()

# TC: Us09 Tc03
def test_us09_tc03():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000')
        page.click('text=Login')
        page.fill('#login-email', 'testuser')
        page.fill('#login-password', 'testpassword')
        page.click('text=Login')
        expect(page).to_have_url('http://localhost:8000/dashboard')
        expect(page.locator('#welcome-message')).to_be_visible()
        browser.close()

# TC: Us09 Tc04
def test_us09_tc04():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000')
        page.click('text=Login')
        page.fill('#login-email', 'testuser')
        page.fill('#login-password', 'wrongpassword')
        page.click('text=Login')
        expect(page).to_have_url('http://localhost:8000/login')
        expect(page.locator('#error-message')).to_be_visible()
        browser.close()