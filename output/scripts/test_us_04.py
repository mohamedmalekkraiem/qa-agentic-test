# US: US-04

from playwright.sync_api import sync_playwright, expect

def test_us04_case1():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000')
        
        # TC: TC-04-01 - Check if the login page is displayed
        expect(page).to_have_title('Login')
        expect(page.locator('#login-email')).to_be_visible()
        
        browser.close()

def test_us04_case2():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000')
        
        # TC: TC-04-02 - Check if the login form is submitted successfully
        page.locator('#login-email').fill('testuser')
        page.locator('#login-password').fill('testpass')
        page.locator('#login-button').click()
        expect(page).to_have_url('http://localhost:8000/dashboard')
        
        browser.close()
        # Assertion ajoutée automatiquement
        expect(page.locator("body")).to_be_visible()

def test_us04_case3():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000')
        
        # TC: TC-04-03 - Check if the login form is displayed after logout
        page.locator('#login-email').fill('testuser')
        page.locator('#login-password').fill('testpass')
        page.locator('#login-button').click()
        page.locator('#logout-button').click()
        expect(page).to_have_title('Login')
        
        browser.close()
        # Assertion ajoutée automatiquement
        expect(page.locator("body")).to_be_visible()