"""Pantry inventory — IH#2 (Low! orange warning, remove confirm),
IH#3 (search bar), IH#4 (nav bar), IH#5 (cancel in edit dialog),
IH#8 (edit freely, confirm irreversible actions)."""
import tkinter as tk
from tkinter import messagebox
import store

BG      = "#f5f5f5"
GREEN   = "#4CAF50"
BLUE    = "#2196F3"
ORANGE  = "#FF9800"
RED     = "#F44336"
LOW_BG  = "#FFF3E0"   # soft orange background for low-stock rows


class PantryPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app
        self._build()

    def _build(self):
        # Nav bar — identical layout on every authenticated screen (IH#4)
        nav = tk.Frame(self, bg="#333", pady=8)
        nav.pack(fill="x")
        for label, cmd in [
            ("HOME",    lambda: self.app.show("HomePage")),
            ("PANTRY",  lambda: None),
            ("LOG OUT", self._confirm_logout),
        ]:
            tk.Button(nav, text=label, bg="#333", fg="white", relief="flat",
                      font=("Arial", 11, "bold"), padx=12,
                      command=cmd).pack(side="left")

        tk.Label(self, text="My Pantry",
                 font=("Arial", 18, "bold"), bg=BG).pack(pady=(14, 4))

        # Search bar (IH#3: query pantry to gather exactly the info needed)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._render())
        tk.Entry(self, textvariable=self.search_var,
                 font=("Arial", 11)).pack(fill="x", padx=16, pady=6)

        # Scrollable pantry list
        frame = tk.Frame(self, bg=BG)
        frame.pack(fill="both", expand=True, padx=16)
        self.canvas = tk.Canvas(frame, bg=BG, highlightthickness=0)
        sb = tk.Scrollbar(frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.list_frame = tk.Frame(self.canvas, bg=BG)
        win_id = self.canvas.create_window((0, 0), window=self.list_frame, anchor="nw")
        self.list_frame.bind("<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>",
            lambda e: self.canvas.itemconfig(win_id, width=e.width))

        # Add to Pantry button (IH#6: clear explicit path to add items)
        tk.Button(self, text="+ Add to Pantry", font=("Arial", 13, "bold"),
                  bg=GREEN, fg="white", relief="flat", pady=10,
                  command=self._add_dialog).pack(fill="x", padx=16, pady=10)

    def _render(self):
        """Rebuild pantry rows with current search filter."""
        for w in self.list_frame.winfo_children():
            w.destroy()

        if not self.app.current_user:
            return

        items  = store.get_pantry(self.app.current_user)
        query  = self.search_var.get().lower()
        visible = [(i, it) for i, it in enumerate(items)
                   if query in it["name"].lower()
                   or query in it.get("category", "").lower()]

        if not visible:
            tk.Label(self.list_frame, text="No pantry items yet.",
                     fg="#999", bg=BG, font=("Arial", 11)).pack(pady=24)
            return

        for orig_idx, item in visible:
            self._pantry_row(orig_idx, item)

    def _pantry_row(self, idx, item):
        qty    = item["quantity"]
        is_low = qty <= 1
        # IH#2: orange background + "(Low!)" communicates cost of running out
        row_bg = LOW_BG if is_low else "white"

        row = tk.Frame(self.list_frame, bg=row_bg, relief="solid", bd=1)
        row.pack(fill="x", pady=3)

        # Item info
        info = tk.Frame(row, bg=row_bg)
        info.pack(side="left", fill="both", expand=True, padx=10, pady=8)
        tk.Label(info, text=item["name"], font=("Arial", 13, "bold"),
                 bg=row_bg, anchor="w").pack(fill="x")

        qty_text = f"Qty: {qty}"
        if is_low:
            qty_text += "  (Low!)"   # IH#2: explicit cost label
        detail = f"{item.get('category', '')}    {qty_text}".strip()
        tk.Label(info, text=detail, font=("Arial", 10),
                 fg=ORANGE if is_low else "#555",
                 bg=row_bg, anchor="w").pack(fill="x")

        # Action buttons
        btns = tk.Frame(row, bg=row_bg)
        btns.pack(side="right", padx=8, pady=8)
        # Edit — always re-editable, no permanent consequence (IH#8)
        tk.Button(btns, text="Edit", bg=BLUE, fg="white", relief="flat",
                  command=lambda i=idx, it=item: self._edit_dialog(i, it)).pack(pady=2)
        # Remove — confirm first (IH#2 + IH#5 + IH#8)
        tk.Button(btns, text="Remove", bg=RED, fg="white", relief="flat",
                  command=lambda i=idx: self._remove(i)).pack(pady=2)

    # ── dialogs ─────────────────────────────────────────────────────────────

    def _add_dialog(self):
        dlg = _ItemDialog(self, "Add to Pantry")
        if dlg.result:
            name, cat, qty = dlg.result
            store.add_pantry_item(self.app.current_user, name, cat, qty)
            self._render()

    def _edit_dialog(self, idx, item):
        """Pre-filled dialog so tinkering is safe and easy (IH#8)."""
        dlg = _ItemDialog(self, "Edit Item", prefill=item)
        if dlg.result:
            name, cat, qty = dlg.result
            store.update_pantry_item(self.app.current_user, idx, name, cat, qty)
            self._render()

    def _remove(self, idx):
        # IH#2: explicit warning; IH#5: cancel available; IH#8: confirm irreversible
        if messagebox.askyesno("Remove", "Remove item from pantry?", icon="warning"):
            store.remove_pantry_item(self.app.current_user, idx)
            self._render()

    def _confirm_logout(self):
        if messagebox.askyesno("Log Out", "Are you sure you want to log out?"):
            self.app.logout()

    def refresh(self):
        self.search_var.set("")
        self._render()


class _ItemDialog(tk.Toplevel):
    """Reusable modal for add/edit pantry items — IH#5: Cancel discards safely."""

    def __init__(self, parent, title, prefill=None):
        super().__init__(parent)
        self.title(title)
        self.result = None
        self.resizable(False, False)
        self.grab_set()           # block interaction with parent window
        self.config(bg=BG)
        px = 20

        tk.Label(self, text="Item Name *", bg=BG).pack(anchor="w", padx=px, pady=(16, 2))
        self.name_var = tk.StringVar(value=prefill["name"] if prefill else "")
        tk.Entry(self, textvariable=self.name_var,
                 font=("Arial", 12)).pack(fill="x", padx=px)

        tk.Label(self, text="Category", bg=BG).pack(anchor="w", padx=px, pady=(10, 2))
        self.cat_var = tk.StringVar(value=prefill.get("category", "") if prefill else "")
        tk.Entry(self, textvariable=self.cat_var,
                 font=("Arial", 12)).pack(fill="x", padx=px)

        tk.Label(self, text="Quantity", bg=BG).pack(anchor="w", padx=px, pady=(10, 2))
        self.qty_var = tk.IntVar(value=prefill["quantity"] if prefill else 1)
        qty_row = tk.Frame(self, bg=BG)
        qty_row.pack(anchor="w", padx=px, pady=2)
        tk.Button(qty_row, text="−", command=self._dec).pack(side="left")
        tk.Label(qty_row, textvariable=self.qty_var,
                 font=("Arial", 12), width=4).pack(side="left")
        tk.Button(qty_row, text="+", command=self._inc).pack(side="left")

        self.err_lbl = tk.Label(self, text="Name is required.", fg=RED, bg=BG)

        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=px, pady=16)
        tk.Button(btn_row, text="Save", bg=GREEN, fg="white", relief="flat",
                  command=self._save).pack(side="left", fill="x", expand=True)
        # Cancel discards changes without saving (IH#5)
        tk.Button(btn_row, text="Cancel", bg=BLUE, fg="white", relief="flat",
                  command=self.destroy).pack(side="left", fill="x", expand=True,
                                            padx=(10, 0))
        self.wait_window()

    def _inc(self):
        self.qty_var.set(self.qty_var.get() + 1)

    def _dec(self):
        if self.qty_var.get() > 1:
            self.qty_var.set(self.qty_var.get() - 1)

    def _save(self):
        name = self.name_var.get().strip()
        if not name:
            self.err_lbl.pack(anchor="w", padx=20)
            return
        self.result = (name, self.cat_var.get().strip(), self.qty_var.get())
        self.destroy()
