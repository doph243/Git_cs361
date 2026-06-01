"""Register screen — IH#5 (back arrow to Login), IH#4 (familiar form)."""
import tkinter as tk
import store

BG    = "#f5f5f5"
GREEN = "#4CAF50"
BLUE  = "#2196F3"
RED   = "#F44336"


class RegisterPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app
        self._build()

    def _build(self):
        # Back arrow (IH#5: explicit backtrack to Login without losing anything)
        hdr = tk.Frame(self, bg=BG, pady=12)
        hdr.pack(fill="x", padx=10)
        tk.Button(hdr, text="← Back", bg=BG, relief="flat",
                  font=("Arial", 11), fg=BLUE,
                  command=lambda: self.app.show("LoginPage")).pack(side="left")
        tk.Label(hdr, text="Create Account", font=("Arial", 16, "bold"),
                 bg=BG).pack(side="left", padx=10)

        form = tk.Frame(self, bg=BG)
        form.pack(padx=44, pady=10, fill="x")

        tk.Label(form, text="Username", bg=BG, anchor="w").pack(fill="x")
        self.u_var = tk.StringVar()
        tk.Entry(form, textvariable=self.u_var,
                 font=("Arial", 12)).pack(fill="x", pady=(2, 12))

        tk.Label(form, text="Password", bg=BG, anchor="w").pack(fill="x")
        self.p_var = tk.StringVar()
        tk.Entry(form, textvariable=self.p_var, show="•",
                 font=("Arial", 12)).pack(fill="x", pady=(2, 6))

        # Feedback label (success green / error red)
        self.msg_var = tk.StringVar()
        self.msg_lbl = tk.Label(form, textvariable=self.msg_var,
                                font=("Arial", 10), wraplength=300)

        tk.Button(form, text="CREATE ACCOUNT", font=("Arial", 13, "bold"),
                  bg=GREEN, fg="white", relief="flat", pady=10,
                  command=self._register).pack(fill="x", pady=(14, 0))

    def _register(self):
        u, p = self.u_var.get().strip(), self.p_var.get()
        if not u or not p:
            self._show_msg("Please fill in all fields.", RED)
            return
        ok, msg = store.register(u, p)
        self._show_msg(msg, GREEN if ok else RED)

    def _show_msg(self, msg, color):
        self.msg_var.set(msg)
        self.msg_lbl.config(fg=color)
        self.msg_lbl.pack(fill="x", pady=(6, 0))

    def refresh(self):
        self.u_var.set("")
        self.p_var.set("")
        self.msg_lbl.pack_forget()
