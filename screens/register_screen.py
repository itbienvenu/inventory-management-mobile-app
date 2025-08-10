from configs import show_popup
import sqlite3
import db
from kivy.uix.screenmanager import Screen
from kivy.app import App

class RegisterScreen(Screen):
    def do_register(self):
        username = self.ids.reg_username.text
        email = self.ids.reg_email.text
        password = self.ids.reg_password.text

        if not username or not email or not password:
            show_popup("Error", "All fields required!")
            return

        try:
            db.add_user(username, email, password)
            show_popup("Success", "User registered successfully!")
            self.manager.current = "login"

            # Clear fields
            self.ids.reg_username.text = ""
            self.ids.reg_email.text = ""
            self.ids.reg_password.text = ""
        except sqlite3.IntegrityError:
            show_popup("Error", "Email already exists.")
