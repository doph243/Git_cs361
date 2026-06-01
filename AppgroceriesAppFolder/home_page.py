"""Shopping List home — IH#2 (remove confirm), IH#4 (nav bar, checkboxes),
IH#5 (strikethrough, confirm), IH#6 (Add Item CTA), IH#7 (sort),
IH#8 (sort/search safe, confirm logout)."""
import tkinter as tk
from tkinter import messagebox
import store

BG    = "#f5f5f5"
GREEN = "#4CAF50"
BLUE  = "#2196F3"
RED   = "#F44336"


class HomePage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app
        self._check_vars = []   # keep BooleanVars alive (prevents GC)
        self._build()

    def _build(self):
        # Nav bar — same on every authenticated screen (IH#4: familiar navigation)
        nav = tk.Frame(self, bg="#333", pady=8)
        nav.pack(fill="x")
        for label, cmd in [
            ("HOME",    lambda: None),
            ("PANTRY",  lambda: self.app.show("PantryPage")),
            ("LOG OUT", self._confirm_logout),
        ]:
            tk.Button(nav, text=label, bg="#333", fg="white", relief="flat",
                      font=("Arial", 11, "bold"), padx=12,
                      command=cmd).pack(side="left")

        tk.Label(self, text="My Shopping List",
                 font=("Arial", 18, "bold"), bg=BG).pack(pady=(14, 4))

        # Controls row: sort dropdown + search bar
        ctrl = tk.Frame(self, bg=BG)
        ctrl.pack(fill="x", padx=16, pady=4)

        # Sort dropdown (IH#7: try different orderings; IH#8: no destructive effect)
        tk.Label(ctrl, text="Sort:", bg=BG).pack(side="left")
        self.sort_var = tk.StringVar(value="Date Added")
        tk.OptionMenu(ctrl, self.sort_var, "Date Added", "Name", "Category",
                      command=lambda _: self._render()).pack(side="left", padx=6)

        # Search bar (IH#3: let users query their list)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._render())
        tk.Entry(ctrl, textvariable=self.search_var,
                 font=("Arial", 11)).pack(side="left", fill="x", expand=True, padx=(10, 0))

        # Scrollable item list
        frame = tk.Frame(self, bg=BG)
        frame.pack(fill="both", expand=True, padx=16, pady=4)
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

        # Add Item button — prominent CTA (IH#6: single clear path to add)
        tk.Button(self, text="+ Add Item", font=("Arial", 13, "bold"),
                  bg=GREEN, fg="white", relief="flat", pady=10,
                  command=lambda: self.app.show("AddItemPage")).pack(
                  fill="x", padx=16, pady=10)

    def _render(self):
        """Rebuild the item list according to current search + sort."""
        for w in self.list_frame.winfo_children():
            w.destroy()
        self._check_vars.clear()

        if not self.app.current_user:
            return

        items   = store.get_list(self.app.current_user)
        query   = self.search_var.get().lower()

        # Filter (IH#3: search lets users gather exactly what they need)
        visible = [(i, it) for i, it in enumerate(items)
                   if query in it["name"].lower()
                   or query in it.get("category", "").lower()]

        # Sort (IH#7: three approaches)
        key = self.sort_var.get()
        if key == "Name":
            visible.sort(key=lambda x: x[1]["name"].lower())
        elif key == "Category":
            visible.sort(key=lambda x: x[1].get("category", "").lower())
        # "Date Added" keeps the original insertion order

        if not visible:
            tk.Label(self.list_frame,
                     text="No items found. Tap '+ Add Item' to get started.",
                     fg="#999", bg=BG, font=("Arial", 11),
                     wraplength=340).pack(pady=24)
            return

        for orig_idx, item in visible:
            self._item_row(orig_idx, item)

    def _item_row(self, idx, item):
        row = tk.Frame(self.list_frame, bg="white", relief="solid", bd=1)
        row.pack(fill="x", pady=3)

        # Checkbox (IH#4: universally recognised; IH#5: checked stays visible with strikethrough)
        var = tk.BooleanVar(value=item["checked"])
        self._check_vars.append(var)   # prevent garbage collection
        def on_check(i=idx, v=var):
            store.toggle_item(self.app.current_user, i)
            self._render()
        tk.Checkbutton(row, variable=var, bg="white", command=on_check).pack(
            side="left", padx=6)

        # Strikethrough for checked items (IH#5: can review before clearing)
        font = ("Arial", 12, "overstrike") if item["checked"] else ("Arial", 12)
        label = f"{item['name']}  —  Qty: {item['quantity']}"
        if item.get("category"):
            label += f"  [{item['category']}]"
        tk.Label(row, text=label, font=font, bg="white", anchor="w").pack(
            side="left", fill="x", expand=True, padx=6, pady=8)

        # Remove button (IH#2: cost made explicit via confirm; IH#5 + IH#8: backtrack available)
        tk.Button(row, text="Remove", bg=RED, fg="white", relief="flat",
                  command=lambda i=idx: self._remove(i)).pack(
                  side="right", padx=6, pady=6)

    def _remove(self, idx):
        # IH#2: tell user this is permanent; IH#5: give Yes/No backtrack
        if messagebox.askyesno("Remove Item",
                               "Remove item from list?\nThis cannot be undone.",
                               icon="warning"):
            store.remove_item(self.app.current_user, idx)
            self._render()

    def _confirm_logout(self):
        # IH#8: irreversible actions require confirmation
        if messagebox.askyesno("Log Out", "Are you sure you want to log out?"):
            self.app.logout()

    def refresh(self):
        self.search_var.set("")
        self.sort_var.set("Date Added")
        self._render()
