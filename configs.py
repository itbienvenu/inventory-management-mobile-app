from kivy.uix.popup import Popup
from kivy.uix.label import Label


def show_popup(title, message):
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(None, None),
            size=(300, 200)
        )
        popup.open()