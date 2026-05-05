"""Central app controller — owns all pages and handles navigation."""
import tkinter as tk
from pages.login_page    import LoginPage
from pages.register_page import RegisterPage
from pages.home_page     import HomePage
from pages.add_item_page import AddItemPage
from pages.pantry_page   import PantryPage


class GroceriesApp:
    def __init__(self, root):
        self.root = root
        self.current_user = None          # set after successful login

        # Single container; all pages stack inside it
        container = tk.Frame(root)
        container.pack(fill="both", expand=True)

        # Build every page once and stack them (place keeps size fixed)
        self.pages = {}
        for PageClass in (LoginPage, RegisterPage, HomePage, AddItemPage, PantryPage):
            page = PageClass(container, self)
            self.pages[PageClass.__name__] = page
            page.place(relwidth=1, relheight=1)

        self.show("LoginPage")

    def show(self, name):
        """Refresh the named page and bring it to the front."""
        page = self.pages[name]
        page.refresh()
        page.tkraise()

    def login(self, username):
        """Called after credentials are verified."""
        self.current_user = username
        self.show("HomePage")

    def logout(self):
        self.current_user = None
        self.show("LoginPage")
