# US: US-20
from playwright.sync_api import sync_playwright, expect

def test_us_20_case_1():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000')
        
        # TC: TC-01 - Vérifier que la page d'accueil est correctement chargée
        expect(page).to_have_title('Accueil')
        expect(page.locator('#header')).to_have_text('Bienvenue sur le site')

        browser.close()

def test_us_20_case_2():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000')

        # TC: TC-02 - Vérifier que le bouton "Connexion" est présent et cliquable
        expect(page.locator('#login-button')).to_be_visible()
        expect(page.locator('#login-button')).to_be_enabled()
        page.locator('#login-button').click()

        browser.close()

def test_us_20_case_3():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000')

        # TC: TC-03 - Vérifier que le formulaire de connexion est correctement affiché
        page.locator('#login-button').click()
        expect(page.locator('#login-form')).to_be_visible()
        expect(page.locator('#login-email-input')).to_be_visible()
        expect(page.locator('#login-password-input')).to_be_visible()
        expect(page.locator('#submit-login')).to_be_visible()

        browser.close()