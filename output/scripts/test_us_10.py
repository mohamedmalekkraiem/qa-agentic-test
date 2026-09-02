# US: US-10

from playwright.sync_api import sync_playwright, expect

def test_us_10_case_1():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000')
        
        # TC: TC-10-01
        expect(page).to_have_title('Home Page')
        expect(page.locator('#header')).to_have_text('Welcome to the Home Page')
        
        browser.close()

def test_us_10_case_2():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000')
        
        # TC: TC-10-02
        page.click('text=Login')
        expect(page).to_have_url('http://localhost:8000/login')
        expect(page.locator('#login-form')).to_be_visible()
        
        browser.close()

def test_us_10_case_3():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000')
        
        # TC: TC-10-03
        page.click('text=Register')
        expect(page).to_have_url('http://localhost:8000/register')
        expect(page.locator('#register-form')).to_be_visible()
        
        browser.close()