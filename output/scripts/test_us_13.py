# US: US-13

from playwright.sync_api import sync_playwright, expect

def test_us_13_case_1():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000')
        
        # TC: TC-13-01 - Vérifier que la page d'accueil est correctement affichée
        expect(page).to_have_title('Accueil')
        expect(page.locator('#welcome-message')).to_have_text('Bienvenue sur notre site !')
        
        browser.close()

def test_us_13_case_2():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000')
        
        # TC: TC-13-02 - Vérifier que le bouton "Connexion" est présent
        expect(page.locator('#login-button')).to_be_visible()
        expect(page.locator('#login-button')).to_have_text('Connexion')
        
        browser.close()

def test_us_13_case_3():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000')
        
        # TC: TC-13-03 - Vérifier que le bouton "Inscription" est présent
        expect(page.locator('#signup-button')).to_be_visible()
        expect(page.locator('#signup-button')).to_have_text('Inscription')
        
        browser.close()

def test_us_13_case_4():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000')
        
        # TC: TC-13-04 - Vérifier que le menu de navigation est présent
        expect(page.locator('#nav-menu')).to_be_visible()
        expect(page.locator('#nav-menu a')).to_have_count(3)
        
        browser.close()