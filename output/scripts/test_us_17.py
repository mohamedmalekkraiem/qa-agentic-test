# US: US-17

from playwright.sync_api import sync_playwright, expect

# TC: Case 1
def test_case_1():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000')
        expect(page).to_have_title('Home Page')
        expect(page.locator('#header')).to_have_text('Welcome to the Home Page')
        browser.close()

# TC: Case 2
def test_case_2():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000')
        page.click('text=Login')
        expect(page).to_have_url('http://localhost:8000/login')
        expect(page.locator('#login-form')).to_be_visible()
        browser.close()

# TC: Case 3
def test_case_3():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000')
        page.click('text=Register')
        expect(page).to_have_url('http://localhost:8000/register')
        expect(page.locator('#register-form')).to_be_visible()
        browser.close()

# TC: Case 4
def test_case_4():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000')
        page.click('text=About')
        expect(page).to_have_url('http://localhost:8000/about')
        expect(page.locator('#about-content')).to_have_text('This is the About page content')
        browser.close()