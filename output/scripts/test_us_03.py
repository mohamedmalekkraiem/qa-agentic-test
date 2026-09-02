# US: US-03

from playwright.sync_api import sync_playwright, expect

def test_us03_01():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000')
        
        # TC: TC-03-01 - Vérifier que l'utilisateur est redirigé vers la page d'accueil
        expect(page).to_have_title('Accueil')
        expect(page.locator('#welcome-message')).to_have_text('Bienvenue sur notre site !')

        browser.close()

def test_us03_02():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000')
        
        # TC: TC-03-02 - Vérifier que l'utilisateur peut naviguer vers la page de contact
        page.click('a:has-text("Contact")')
        expect(page).to_have_url('http://localhost:8000/contact')
        expect(page.locator('#contact-title')).to_have_text('Nous contacter')

        browser.close()

def test_us03_03():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8000')
        
        # TC: TC-03-03 - Vérifier que l'utilisateur peut effectuer une recherche sur le site
        page.fill('input[name="search"]', 'produit')
        page.press('input[name="search"]', 'Enter')
        expect(page).to_have_url('http://localhost:8000/search?query=produit')
        expect(page.locator('#search-results')).to_have_count(1)

        browser.close()