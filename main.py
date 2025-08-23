from kivymd.app import MDApp
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
import sqlite3
from configs import show_popup


# ===== SCREEN CLASSES =====
from screens.login_screen import LoginScreen
from screens.register_screen import RegisterScreen
from screens.dashboard_screen import DashboardScreen
from screens.products_screen import ProductsScreen
from screens.stores_screen import StoresScreen
from screens.orders_screen import OrdersScreen
from screens.suppliers_screen import SuppliersScreen
from screens.reports_screen import ReportsScreen
from screens.settings_screen import SettingsScreen
from screens.add_product_screen import AddProductScreen
from screens.edit_product_screen import EditProductScreen
from screens.debtors_screen import DebtorsScreen
from db import create_tables


class MyScreenManager(ScreenManager):
    pass

# ===== MAIN APP =====
class MyApp(MDApp):
    def build(self):
        create_tables()
        Builder.load_file("kv/login.kv")
        Builder.load_file("kv/dashboard.kv")
        Builder.load_file("kv/products.kv")
        Builder.load_file("kv/stores.kv")
        Builder.load_file("kv/orders.kv")
        Builder.load_file("kv/suppliers.kv")
        Builder.load_file("kv/reports.kv")
        Builder.load_file("kv/settings.kv")
        Builder.load_file("kv/add_product.kv")
        Builder.load_file("kv/edit_product.kv")
        Builder.load_file("kv/debtors.kv")


        self.load_sample_data()
        sm = MyScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(RegisterScreen(name="register"))
        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.add_widget(ProductsScreen(name="products"))
        sm.add_widget(StoresScreen(name="stores"))
        sm.add_widget(OrdersScreen(name="orders"))
        sm.add_widget(SuppliersScreen(name="suppliers"))
        sm.add_widget(ReportsScreen(name="reports"))
        sm.add_widget(SettingsScreen(name="settings"))
        sm.add_widget(AddProductScreen(name="add_product"))
        sm.add_widget(EditProductScreen(name="edit_product"))
        sm.add_widget(DebtorsScreen(name="debtors"))

        Builder.load_file("my.kv")

        return sm

    def load_sample_data(self):
        pass

    def logout(self):
        self.root.current = "login"
        screen = self.root.get_screen("login")
        screen.ids.email_input.text = ""
        screen.ids.password_input.text = ""

if __name__ == "__main__":
    MyApp().run()
