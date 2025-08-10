# screens/login_screen.py
from kivy.uix.screenmanager import Screen
import db
from configs import show_popup

class LoginScreen(Screen):
    def do_login(self):
        email = self.ids.login_email.text
        password = self.ids.login_password.text
        user = db.get_user_by_email(email)
        if user and user[3] == password:
            show_popup("Success","Login successful")
            self.manager.current = "dashboard"
        else:
            show_popup("Error","Invalid email password")
            pass
