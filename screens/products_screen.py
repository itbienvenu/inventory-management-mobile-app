from kivy.uix.accordion import StringProperty
from kivy.uix.accordion import NumericProperty
from kivymd.uix.pickers.datepicker.datepicker import date
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.properties import DictProperty, NumericProperty, StringProperty
import sqlite3
import os
from configs import show_popup


class ProductRow(BoxLayout):
    product_id = NumericProperty(0)
    name = StringProperty()
    category = StringProperty()
    image_path = StringProperty()
    index = NumericProperty()


class ProductsScreen(Screen):
    def on_enter(self):
        self.refresh_products()

    def refresh_products(self):
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, category, image_path FROM products ORDER BY last_updated DESC")
        products = cursor.fetchall()
        conn.close()

        data = []
        for idx, prod in enumerate(products):
            id_, name, category, image_path = prod
            print(image_path)
            if image_path and os.path.isfile(image_path):
                img = os.path.abspath(image_path).replace("\\", "/")
            else:
                img = os.path.abspath(os.path.join('product_images', 'default_img.png')).replace("\\", "/")
                # print(img)
            print(img)
            data.append({
                'product_id': id_,
                'name': name,
                'category': category,
                'image_path': img,
                'index': idx,
                'view_product': self.view_product,
                'edit_product': self.edit_product,
                'delete_product': self.delete_product,
            })
        self.ids.rv_products.data = data
 

    def view_product(self, product_id):
        # Implement a popup or navigation to detailed product view
        show_popup("View Product", f"Viewing details for product ID: {product_id}")

    def edit_product(self, product_id):
        # Navigate to edit screen, passing the product_id
        show_popup("View Product", f"Viewing details for product ID: {product_id}")
        app = App.get_running_app()
        app.root.current = 'edit_product'
        app.root.get_screen('edit_product').load_product(product_id)


    def delete_product(self, product_id):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text=f"Are you sure you want to delete product ID: {product_id}?"))
        btns = BoxLayout(spacing=10, size_hint_y=None, height='40dp')
        yes_btn = Button(text='Yes', background_color=(0.8,0.1,0.1,1))
        no_btn = Button(text='No', background_color=(0.3,0.3,0.3,1))
        btns.add_widget(yes_btn)
        btns.add_widget(no_btn)
        content.add_widget(btns)

        popup = Popup(title='Confirm Delete', content=content, size_hint=(None,None), size=(400,200))

        def confirm_delete(instance):
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
            conn.commit()
            conn.close()
            popup.dismiss()
            self.refresh_products()
            show_popup("Deleted", "Product deleted successfully!")

        yes_btn.bind(on_release=confirm_delete)
        no_btn.bind(on_release=popup.dismiss)
        popup.open()
    def filter_products(self):
        show_popup("Success", "Accessing the Filter product menu")


