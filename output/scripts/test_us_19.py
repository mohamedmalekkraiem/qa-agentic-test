# US: US-19

from playwright.sync_api import sync_playwright, expect

def test_us_19_case_1():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000')
        
        # TC: TC-19-01 - Vérifier que la page d'accueil est correctement chargée
        expect(page).to_have_title('Accueil')
        expect(page.locator('#header')).to_have_text('Bienvenue sur le site')

        browser.close()

def test_us_19_case_2():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000/login')

        # TC: TC-19-02 - Vérifier que la page de connexion est correctement chargée
        expect(page).to_have_title('Connexion')
        expect(page.locator('#login-form')).to_be_visible()

        browser.close()

def test_us_19_case_3():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000/register')

        # TC: TC-19-03 - Vérifier que la page d'inscription est correctement chargée
        expect(page).to_have_title('Inscription')
        expect(page.locator('#register-form')).to_be_visible()

        browser.close()