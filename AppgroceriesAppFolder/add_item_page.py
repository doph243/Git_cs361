"""Add Item page — IH#1 (ISBN benefit banner), IH#3 (optional fields, ISBN vs manual),
IH#5 (Cancel backtrack), IH#6 (explicit 2-step path), IH#7 (two approaches side-by-side)."""
import tkinter as tk
import store

BG     = "#f5f5f5"
GREEN  = "#4CAF50"
BLUE   = "#2196F3"
ORANGE = "#FF9800"
RED    = "#F44336"

CATEGORIES = ["", "Produce", "Dairy", "Meat", "Seafood",
               "Bakery", "Dry Goods", "Frozen", "Beverages",
               "Snacks", "Oil", "Other"]


class AddItemPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app
        self.qty = tk.IntVar(value=1)
        self._build()

    def _build(self):
        # Header with back arrow (IH#5: explicit backtrack without losing home state)
        hdr = tk.Frame(self, bg=BG, pady=10)
        hdr.pack(fill="x", padx=10)
        tk.Button(hdr, text="←", font=("Arial", 16), bg=BG, relief="flat", fg=BLUE,
                  command=lambda: self.app.show("HomePage")).pack(side="left")
        tk.Label(hdr, text="Add Item", font=("Arial", 16, "bold"),
                 bg=BG).pack(side="left", padx=8)

        # Scrollable form container
        canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        sb = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        form = tk.Frame(canvas, bg=BG)
        canvas.create_window((0, 0), window=form, anchor="nw")
        form.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        px = 22   # uniform horizontal padding throughout form

        # ── ISBN search section ──────────────────────────────────────────────
        # IH#3: gather info via search; IH#7: first of two parallel approaches
        tk.Label(form, text="Search by ISBN  (optional)", bg=BG,
                 font=("Arial", 11, "bold")).pack(anchor="w", padx=px, pady=(14, 2))

        isbn_row = tk.Frame(form, bg=BG)
        isbn_row.pack(fill="x", padx=px, pady=2)
        self.isbn_var = tk.StringVar()
        tk.Entry(isbn_row, textvariable=self.isbn_var,
                 font=("Arial", 12)).pack(side="left", fill="x", expand=True)
        tk.Button(isbn_row, text="Search", bg=GREEN, fg="white", relief="flat",
                  font=("Arial", 11), padx=10,
                  command=self._isbn_search).pack(side="left", padx=(8, 0))

        # Status banner — hidden until search runs (IH#1: explains benefit of ISBN feature)
        self.banner_var = tk.StringVar()
        self.banner = tk.Label(form, textvariable=self.banner_var,
                               font=("Arial", 10, "bold"), fg="white", pady=5)

        # ── OR divider (IH#7: makes two approaches visually explicit) ───────
        tk.Frame(form, bg="#ccc", height=1).pack(fill="x", padx=px, pady=(12, 4))
        tk.Label(form, text="— OR fill in manually —",
                 fg="#888", bg=BG, font=("Arial", 9)).pack()
        tk.Frame(form, bg="#ccc", height=1).pack(fill="x", padx=px, pady=(4, 8))

        # ── Manual entry fields ───────────────────────────────────────────────
        # Name — required (IH#3: only this field is required; IH#6: step 1 of 2)
        tk.Label(form, text="Item name *  (required)", bg=BG,
                 font=("Arial", 11, "bold")).pack(anchor="w", padx=px, pady=(2, 2))
        self.name_var = tk.StringVar()
        self.name_entry = tk.Entry(form, textvariable=self.name_var,
                                   font=("Arial", 12))
        self.name_entry.pack(fill="x", padx=px, pady=2)
        # Validation error (IH#2: cost of submitting without required field)
        self.name_err = tk.Label(form, text="⚠  Item name is required.",
                                 fg=RED, bg=BG, font=("Arial", 10))

        # Category — optional (IH#3: users share only what they choose)
        tk.Label(form, text="Category  (optional)", bg=BG,
                 font=("Arial", 11)).pack(anchor="w", padx=px, pady=(12, 2))
        self.cat_var = tk.StringVar(value="")
        tk.OptionMenu(form, self.cat_var, *CATEGORIES).pack(
            fill="x", padx=px, pady=2)

        # Quantity stepper (IH#4: familiar mobile +/− pattern)
        tk.Label(form, text="Quantity", bg=BG,
                 font=("Arial", 11)).pack(anchor="w", padx=px, pady=(12, 2))
        qty_row = tk.Frame(form, bg=BG)
        qty_row.pack(anchor="w", padx=px, pady=2)
        tk.Button(qty_row, text="−", font=("Arial", 14, "bold"), width=3,
                  bg=BLUE, fg="white", relief="flat",
                  command=self._dec).pack(side="left")
        tk.Label(qty_row, textvariable=self.qty,
                 font=("Arial", 14), width=4, bg=BG).pack(side="left", padx=8)
        tk.Button(qty_row, text="+", font=("Arial", 14, "bold"), width=3,
                  bg=BLUE, fg="white", relief="flat",
                  command=self._inc).pack(side="left")

        # Notes — optional (IH#3: freely skipped)
        tk.Label(form, text="Note  (optional)", bg=BG,
                 font=("Arial", 11)).pack(anchor="w", padx=px, pady=(12, 2))
        self.notes_var = tk.StringVar()
        tk.Entry(form, textvariable=self.notes_var,
                 font=("Arial", 12)).pack(fill="x", padx=px, pady=2)

        # ── Action buttons (IH#5: Cancel always present; IH#6: Add Item is step 2) ──
        btn_row = tk.Frame(form, bg=BG)
        btn_row.pack(fill="x", padx=px, pady=22)
        tk.Button(btn_row, text="Add Item", font=("Arial", 13, "bold"),
                  bg=GREEN, fg="white", relief="flat", pady=10,
                  command=self._add_item).pack(side="left", fill="x", expand=True)
        tk.Button(btn_row, text="Cancel", font=("Arial", 13),
                  bg=BLUE, fg="white", relief="flat", pady=10,
                  command=self._cancel).pack(side="left", fill="x", expand=True,
                                             padx=(12, 0))

    # ── helpers ─────────────────────────────────────────────────────────────

    def _isbn_search(self):
        code = self.isbn_var.get().strip()
        if not code:
            self._show_banner("Enter an ISBN code first.", ORANGE)
            return
        result = store.isbn_lookup(code)
        if result:
            # IH#1: explain benefit — fields auto-populated so user saves effort
            self.name_var.set(result["name"])
            self.cat_var.set(result["category"])
            self._show_banner("Item found!  Fields have been auto-populated.", GREEN)
        else:
            # IH#1 + IH#7: no dead end — manual form is right below
            self._show_banner("Item not found.  Please fill in manually.", ORANGE)

    def _show_banner(self, msg, color):
        self.banner_var.set(msg)
        self.banner.config(bg=color)
        self.banner.pack(fill="x", padx=22, pady=4)

    def _inc(self):
        self.qty.set(self.qty.get() + 1)

    def _dec(self):
        if self.qty.get() > 1:   # minimum quantity is 1
            self.qty.set(self.qty.get() - 1)

    def _add_item(self):
        name = self.name_var.get().strip()
        if not name:
            self.name_err.pack(anchor="w", padx=22)
            return
        self.name_err.pack_forget()
        store.add_item(self.app.current_user, name,
                       self.cat_var.get(), self.qty.get(), self.notes_var.get())
        self.app.show("HomePage")  # IH#6: single clear endpoint

    def _cancel(self):
        # IH#5: discard all input, return to Shopping List safely
        self._reset()
        self.app.show("HomePage")

    def _reset(self):
        self.isbn_var.set("")
        self.name_var.set("")
        self.cat_var.set("")
        self.qty.set(1)
        self.notes_var.set("")
        self.banner.pack_forget()
        self.name_err.pack_forget()

    def refresh(self):
        self._reset()
