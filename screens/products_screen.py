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
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
import sqlite3
import os
from kivy.metrics import dp
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button

from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp


class ProductPopup(Popup):
    def __init__(self, name, category, last_updated, image_path, **kwargs):
        super().__init__(**kwargs)
        self.title = f"Details of {name}"
        self.size_hint = (0.8, 0.6)
        self.auto_dismiss = False

        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        info_layout = BoxLayout(orientation='horizontal', spacing=10)

        if image_path and os.path.isfile(image_path):
            img = Image(source=image_path, size_hint=(0.4, 1))
        else:
            img = Label(text='[No Image]', size_hint=(0.4, 1), halign='center', valign='middle')
            img.bind(size=img.setter('text_size'))

        text_layout = BoxLayout(orientation='vertical', spacing=5)
        text_layout.add_widget(Label(text=f"[b]Name:[/b] {name}", markup=True, font_size='18sp'))
        text_layout.add_widget(Label(text=f"[b]Category:[/b] {category}", markup=True, font_size='16sp'))
        text_layout.add_widget(Label(text=f"[b]Created:[/b] {last_updated}", markup=True, font_size='16sp'))

        info_layout.add_widget(img)
        info_layout.add_widget(text_layout)

        btn_layout = BoxLayout(size_hint=(1, 0.2), spacing=20)
        close_btn = Button(text='Close')
        close_btn.bind(on_release=self.dismiss)
        btn_layout.add_widget(close_btn)

        layout.add_widget(info_layout)
        layout.add_widget(btn_layout)

        self.content = layout


class ProductRow(BoxLayout):
    product_id = NumericProperty(0)
    name = StringProperty()
    category = StringProperty()
    image_path = StringProperty()
    index = NumericProperty()


class ProductsScreen(Screen):
    edit_dialog = None
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

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, category, last_updated, image_path FROM products WHERE id=?", (product_id,))
        product = cursor.fetchone()
        conn.close()

        if product is None:
            show_popup("Error", "Product not found.")
            return

        # product is a tuple: (id, name, category, image_path)
        popup = ProductPopup(name=product[1], category=product[2], last_updated=product[3], image_path=product[4])
        popup.open()

        print(product)


    def edit_product(self, product_id):
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name, category, image_path FROM products WHERE id=?", (product_id,))
        product = cursor.fetchone()
        conn.close()

        if not product:
            show_popup("Error", "Product not found!")
            return

        name, category, image_path = product

        
        content = MDBoxLayout(
        orientation='vertical', 
        spacing=dp(15), 
        size_hint_y=None,
        )
        content.bind(minimum_height=content.setter('height'))

        self.name_field = MDTextField(text=name, hint_text="Product Name", size_hint_x=1)
        self.category_field = MDTextField(text=category, hint_text="Category", size_hint_x=1)
        self.image_path_field = MDTextField(text=image_path if image_path else "", hint_text="Image Path", size_hint_x=1)

        content.add_widget(self.name_field)
        content.add_widget(self.category_field)
        content.add_widget(self.image_path_field)

        scroll = ScrollView(size_hint=(1, None), size=(dp(400), dp(500)))
        scroll.add_widget(content)

        # Create the dialog with Save and Cancel buttons
        self.dialog = MDDialog(
        title="Edit Product",
        type="custom",
        content_cls=scroll,
        size_hint=(None, None),
        size=(dp(420), dp(550)),
        buttons=[
            MDFlatButton(text="Cancel", on_release=lambda x: self.dialog.dismiss()),
            MDFlatButton(text="Save", on_release=self.save_product),
        ],
        )
        self.dialog.open()

    def save_product(self, product_id):
        name = self.name_field.text.strip()
        category = self.category_field.text.strip()
        image_path = self.image_path_field.text.strip()

        if not name or not category:
            show_popup("Error", "Name and Category cannot be empty!")
            return

        # Optional: check if image_path is valid file, else set to None or empty string
        if image_path and not os.path.isfile(image_path):
            show_popup("Warning", "Image path is invalid or file does not exist.")

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE products SET name=?, category=?, image_path=? WHERE id=?",
            (name, category, image_path, product_id)
        )
        conn.commit()
        conn.close()

        self.edit_dialog.dismiss()
        show_popup("Success", "Product updated successfully!")
        self.refresh_products()


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


