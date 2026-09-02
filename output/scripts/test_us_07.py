# US: US-07

from playwright.sync_api import sync_playwright, expect

def test_us_07_case_1():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000')
        
        # TC: TC-07-01
        expect(page).to_have_title('Home Page')
        expect(page.locator('#welcome-message')).to_have_text('Welcome to the Home Page!')
        
        browser.close()

def test_us_07_case_2():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000/login')
        
        # TC: TC-07-02
        expect(page).to_have_title('Login Page')
        expect(page.locator('#login-form')).to_be_visible()
        
        browser.close()

def test_us_07_case_3():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000/register')
        
        # TC: TC-07-03
        expect(page).to_have_title('Register Page')
        expect(page.locator('#register-form')).to_be_visible()
        
        browser.close()