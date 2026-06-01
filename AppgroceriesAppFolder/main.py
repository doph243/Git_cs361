# ============================================================
# main.py — Groceries App  |  CS 361 Assignment 3 Sprint 1
# Inclusivity Heuristics implemented: IH#1 – IH#8
# Run:  python main.py
# ============================================================

import tkinter as tk
from app import GroceriesApp   # page router / central controller


def main():
    # ── Window setup ────────────────────────────────────────
    root = tk.Tk()
    root.title("Groceries App")
    root.geometry("420x720")      # portrait, mobile-like proportions
    root.resizable(False, False)  # fixed size keeps every layout stable

    # ── Launch app ──────────────────────────────────────────
    # GroceriesApp builds all pages and shows the Login screen first.
    # Navigation is handled internally via app.show() / app.login() / app.logout().
    GroceriesApp(root)

    # ── Hand control to tkinter event loop ──────────────────
    root.mainloop()


# Pages and their IH coverage (quick reference):
#   LoginPage     — IH#1 (app title/tagline), IH#2 (error msg), IH#4 (familiar form),
#                   IH#5 (back-arrow on Register), IH#7 (show/hide password)
#   RegisterPage  — IH#5 (back arrow), IH#4 (standard form)
#   HomePage      — IH#2 (remove confirm), IH#4 (nav bar, checkboxes),
#                   IH#5 (strikethrough, undo-via-uncheck), IH#6 (Add Item CTA),
#                   IH#7 (sort: Name/Category/Date), IH#8 (logout confirm)
#   AddItemPage   — IH#1 (ISBN benefit banner), IH#3 (ISBN + manual, optional fields),
#                   IH#5 (Cancel), IH#6 (2-step flow), IH#7 (ISBN vs manual)
#   PantryPage    — IH#2 (Low! warning, remove confirm), IH#3 (search),
#                   IH#4 (nav bar), IH#5 (edit cancel), IH#8 (edit freely)

if __name__ == "__main__":
    main()
