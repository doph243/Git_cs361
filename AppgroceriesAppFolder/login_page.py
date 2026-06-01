"""Login screen — IH#1 (app title explains purpose), IH#2 (error message),
IH#4 (familiar form), IH#5 (register back-arrow), IH#7 (show/hide password)."""
import tkinter as tk
import store

BG     = "#f5f5f5"
GREEN  = "#4CAF50"
RED    = "#F44336"
BLUE   = "#2196F3"


class LoginPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app
        self._build()

    def _build(self):
        # App logo + tagline (IH#1: tells users what the app does before they log in)
        tk.Label(self, text="🛒", font=("Arial", 56), bg=BG).pack(pady=(50, 4))
        tk.Label(self, text="Groceries App", font=("Arial", 22, "bold"), bg=BG).pack()
        tk.Label(self, text="Your personal shopping & pantry manager",
                 font=("Arial", 10), fg="#888", bg=BG).pack(pady=(2, 28))

        form = tk.Frame(self, bg=BG)
        form.pack(padx=44, fill="x")

        # Username (IH#4: standard web/app login convention)
        tk.Label(form, text="Username", bg=BG, anchor="w").pack(fill="x")
        self.u_var = tk.StringVar()
        tk.Entry(form, textvariable=self.u_var,
                 font=("Arial", 12)).pack(fill="x", pady=(2, 12))

        # Password + show/hide toggle (IH#7: let user try visible input)
        tk.Label(form, text="Password", bg=BG, anchor="w").pack(fill="x")
        pw_row = tk.Frame(form, bg=BG)
        pw_row.pack(fill="x", pady=(2, 6))
        self.p_var = tk.StringVar()
        self.pw_entry = tk.Entry(pw_row, textvariable=self.p_var,
                                 show="•", font=("Arial", 12))
        self.pw_entry.pack(side="left", fill="x", expand=True)
        self._show_pw = False
        self.toggle_btn = tk.Button(pw_row, text="Show", width=6,
                                    command=self._toggle_pw)
        self.toggle_btn.pack(side="left", padx=(6, 0))

        # Inline error area (IH#2: cost of wrong credentials made explicit)
        self.err_var = tk.StringVar()
        self.err_lbl = tk.Label(form, textvariable=self.err_var,
                                fg="white", bg=RED, font=("Arial", 10),
                                wraplength=300, pady=4)

        # Login button — single prominent CTA (IH#4: familiar pattern)
        tk.Button(form, text="LOG IN", font=("Arial", 13, "bold"),
                  bg=GREEN, fg="white", relief="flat", pady=10,
                  command=self._login).pack(fill="x", pady=(10, 6))

        # Register link (IH#5: register page has a back-arrow to return here)
        tk.Button(form, text="Create account", font=("Arial", 10),
                  bg=BG, relief="flat", fg=BLUE,
                  command=lambda: self.app.show("RegisterPage")).pack()

    def _toggle_pw(self):
        """Show/hide password — IH#7."""
        self._show_pw = not self._show_pw
        self.pw_entry.config(show="" if self._show_pw else "•")
        self.toggle_btn.config(text="Hide" if self._show_pw else "Show")

    def _login(self):
        u, p = self.u_var.get().strip(), self.p_var.get()
        if not u or not p:
            self._show_err("Please enter username and password.")
            return
        if store.authenticate(u, p):
            self.err_lbl.pack_forget()
            self.app.login(u)
        else:
            # IH#2: explicit error so user understands the cost/consequence
            self._show_err("Invalid username or password. Please try again.")

    def _show_err(self, msg):
        self.err_var.set(msg)
        self.err_lbl.pack(fill="x", pady=(4, 0))

    def refresh(self):
        """Reset fields every time this page is shown."""
        self.u_var.set("")
        self.p_var.set("")
        self._show_pw = False
        self.pw_entry.config(show="•")
        self.toggle_btn.config(text="Show")
        self.err_lbl.pack_forget()
