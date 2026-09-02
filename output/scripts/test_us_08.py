# US: US-08

from playwright.sync_api import sync_playwright, expect

def test_us_08_01():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000')
        # TC: TC-08-01: Vérifier que l'utilisateur est redirigé vers la page d'accueil
        expect(page).to_have_title('Accueil')
        expect(page.locator('#welcome-message')).to_have_text('Bienvenue sur notre site !')
        browser.close()

def test_us_08_02():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000')
        # TC: TC-08-02: Vérifier que le menu de navigation est présent
        expect(page.locator('#nav-menu')).to_be_visible()
        expect(page.locator('#nav-menu a')).to_have_count(3)
        browser.close()

def test_us_08_03():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000')
        # TC: TC-08-03: Vérifier que le bouton de connexion est présent et cliquable
        expect(page.locator('#login-button')).to_be_visible()
        page.locator('#login-button').click()
        expect(page).to_have_url('http://localhost:8000/login')
        browser.close()