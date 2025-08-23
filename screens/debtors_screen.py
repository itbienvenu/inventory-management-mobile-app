from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import OneLineAvatarIconListItem, IconRightWidget
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
from kivy.app import App
import sqlite3


class DebtorsScreen(Screen):
    def on_enter(self):
        self.refresh_clients()

    def refresh_clients(self):
        self.ids.clients_list.clear_widgets()
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.id, c.name, c.phone, IFNULL(SUM(d.amount), 0)
            FROM clients c
            LEFT JOIN debts d ON c.id = d.client_id
            GROUP BY c.id
        """)
        for client_id, name, phone, total_debt in cursor.fetchall():
            item = OneLineAvatarIconListItem(
                text=f"{name} ({phone or 'No phone'}) - Debt: ${total_debt:.2f}"
            )
            icon = IconRightWidget(icon="eye", on_release=lambda x, cid=client_id: self.open_manage_debts(cid))
            item.add_widget(icon)
            self.ids.clients_list.add_widget(item)
        conn.close()

    def open_add_client_dialog(self):
        self.client_name = MDTextField(hint_text="Client Name")
        self.client_phone = MDTextField(hint_text="Phone (optional)")

        self.add_client_dialog = MDDialog(
            title="Add Client",
            type="custom",
            content_cls=MDBoxLayout(
                self.client_name, self.client_phone,
                orientation="vertical", spacing=dp(10), size_hint_y=None, height=dp(150)
            ),
            buttons=[
                MDFlatButton(text="Cancel", on_release=lambda x: self.add_client_dialog.dismiss()),
                MDRaisedButton(text="Save", on_release=lambda x: self.save_client())
            ]
        )
        self.add_client_dialog.open()

    def save_client(self):
        name = self.client_name.text.strip()
        phone = self.client_phone.text.strip()

        if not name:
            return

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO clients (name, phone) VALUES (?, ?)", (name, phone or None))
        conn.commit()
        conn.close()

        self.add_client_dialog.dismiss()
        self.refresh_clients()

    def open_manage_debts(self, client_id):
        self.current_client_id = client_id
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM clients WHERE id=?", (client_id,))
        client_name = cursor.fetchone()[0]

        cursor.execute("SELECT id, product, amount FROM debts WHERE client_id=?", (client_id,))
        debts = cursor.fetchall()
        conn.close()

        self.debt_list_layout = MDBoxLayout(orientation="vertical", spacing=dp(5), size_hint_y=None)
        for debt_id, product, amount in debts:
            row = OneLineAvatarIconListItem(text=f"{product} - ${amount:.2f}")
            del_icon = IconRightWidget(icon="delete", on_release=lambda x, did=debt_id: self.delete_debt(did))
            row.add_widget(del_icon)
            self.debt_list_layout.add_widget(row)

        self.manage_debts_dialog = MDDialog(
            title=f"Debts - {client_name}",
            type="custom",
            content_cls=self.debt_list_layout,
            buttons=[
                MDFlatButton(text="Add Debt", on_release=lambda x: self.open_add_debt_dialog()),
                MDFlatButton(text="Close", on_release=lambda x: self.manage_debts_dialog.dismiss())
            ]
        )
        self.manage_debts_dialog.open()

    def open_add_debt_dialog(self):
        # Load products from DB
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM products")
        products = [p[0] for p in cursor.fetchall()]
        conn.close()

        self.product_field = MDTextField(hint_text="Product")
        self.amount_field = MDTextField(hint_text="Amount", input_filter="float")

        # Dropdown menu for products
        menu_items = [{"text": p, "on_release": lambda x=p: self.set_product(x)} for p in products]
        self.product_menu = MDDropdownMenu(caller=self.product_field, items=menu_items, width_mult=4)

        self.product_field.bind(on_focus=lambda inst, val: self.product_menu.open() if val else None)

        self.add_debt_dialog = MDDialog(
            title="Add Debt",
            type="custom",
            content_cls=MDBoxLayout(
                self.product_field, self.amount_field,
                orientation="vertical", spacing=dp(10), size_hint_y=None, height=dp(150)
            ),
            buttons=[
                MDFlatButton(text="Cancel", on_release=lambda x: self.add_debt_dialog.dismiss()),
                MDRaisedButton(text="Save", on_release=lambda x: self.save_debt())
            ]
        )
        self.add_debt_dialog.open()

    def set_product(self, product_name):
        self.product_field.text = product_name
        self.product_menu.dismiss()

    def save_debt(self):
        product = self.product_field.text.strip()
        try:
            amount = float(self.amount_field.text.strip())
        except ValueError:
            return

        if not product or amount <= 0:
            return

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO debts (client_id, product, amount) VALUES (?, ?, ?)",
                       (self.current_client_id, product, amount))
        conn.commit()
        conn.close()

        self.add_debt_dialog.dismiss()
        self.manage_debts_dialog.dismiss()
        self.open_manage_debts(self.current_client_id)

    def delete_debt(self, debt_id):
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM debts WHERE id=?", (debt_id,))
        conn.commit()
        conn.close()
        self.manage_debts_dialog.dismiss()
        self.open_manage_debts(self.current_client_id)
