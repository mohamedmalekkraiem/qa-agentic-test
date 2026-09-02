# US: US-06

from playwright.sync_api import sync_playwright, expect

def test_us06_case1():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000')
        
        # TC: TC-06-01 - Check if the login page is displayed
        expect(page).to_have_title('Login')
        expect(page.locator('#login-email')).to_be_visible()
        
        browser.close()

def test_us06_case2():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000')
        
        # TC: TC-06-02 - Check if the user can log in with valid credentials
        page.locator('#login-email').fill('validuser')
        page.locator('#login-password').fill('validpassword')
        page.locator('#login_button').click()
        
        expect(page).to_have_title('Dashboard')
        expect(page.locator('#welcome_message')).to_contain_text('Welcome, validuser')
        
        browser.close()

def test_us06_case3():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000')
        
        # TC: TC-06-03 - Check if the user is redirected to the login page when invalid credentials are provided
        page.locator('#login-email').fill('invaliduser')
        page.locator('#login-password').fill('invalidpassword')
        page.locator('#login_button').click()
        
        expect(page).to_have_title('Login')
        expect(page.locator('#error_message')).to_contain_text('Invalid username or password')
        
        browser.close()