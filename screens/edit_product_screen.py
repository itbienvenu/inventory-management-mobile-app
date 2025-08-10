from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from configs import show_popup


class EditProductScreen(Screen):
    def load_product(self, product_id):
        Popup()
        show_popup("Success", f"Viewing the Edit Product Screen {product_id}")
