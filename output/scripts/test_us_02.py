# US: US-02

from playwright.sync_api import sync_playwright, expect

def test_us02_case1():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000')
        
        # TC: TC-02-01 - Check if the home page loads successfully
        expect(page).to_have_title('Home Page')
        expect(page.locator('text=Welcome to the Home Page')).to_be_visible()
        
        browser.close()

def test_us02_case2():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000/login')
        
        # TC: TC-02-02 - Check if the login page loads successfully
        expect(page).to_have_title('Login Page')
        expect(page.locator('text=Please enter your credentials')).to_be_visible()
        
        browser.close()

def test_us02_case3():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000/register')
        
        # TC: TC-02-03 - Check if the registration page loads successfully
        expect(page).to_have_title('Register Page')
        expect(page.locator('text=Please enter your details')).to_be_visible()
        
        browser.close()