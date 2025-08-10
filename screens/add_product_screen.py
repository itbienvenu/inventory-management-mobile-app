from kivy.uix.screenmanager import Screen
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from datetime import datetime
import sqlite3
import shutil
import os

class AddProductScreen(Screen):
    selected_image_path = None

    def open_file_chooser(self):
        content = BoxLayout(orientation='vertical')
        filechooser = FileChooserListView(filters=['*.png', '*.jpg', '*.jpeg'], path=os.getcwd())
        btn_layout = BoxLayout(size_hint_y=None, height='48dp', spacing=10)

        select_btn = Button(text='Select', size_hint_x=0.5)
        cancel_btn = Button(text='Cancel', size_hint_x=0.5)
        btn_layout.add_widget(select_btn)
        btn_layout.add_widget(cancel_btn)

        content.add_widget(filechooser)
        content.add_widget(btn_layout)

        self.popup = Popup(title='Choose Product Image',
                           content=content,
                           size_hint=(0.9, 0.9))

        select_btn.bind(on_press=lambda x: self.select_image(filechooser.selection))
        cancel_btn.bind(on_press=lambda x: self.popup.dismiss())

        self.popup.open()

    def select_image(self, selection):
        if selection:
            self.selected_image_path = selection[0]
            self.ids.image_path_label.text = os.path.basename(self.selected_image_path)
        self.popup.dismiss()

    def add_product(self):
        name = self.ids.prod_name.text.strip()
        stock = self.ids.prod_stock.text.strip()
        category = self.ids.prod_category.text.strip()
        active = 1 if self.ids.prod_active.active else 0
        last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not name or not stock.isdigit() or not category:
            self.show_popup("Error", "Please fill all fields correctly.")
            return

        image_db_path = None
        if self.selected_image_path:
            images_dir = os.path.join(os.getcwd(), 'product_images')
            os.makedirs(images_dir, exist_ok=True)

            filename = f"{int(datetime.timestamp(datetime.now()))}_{os.path.basename(self.selected_image_path)}"
            dest_path = os.path.join(images_dir, filename)

            try:
                shutil.copy(self.selected_image_path, dest_path)
                image_db_path = dest_path
            except Exception as e:
                self.show_popup("Error", f"Failed to copy image: {e}")
                return

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO products (name, stock, category, active, last_updated, image_path) VALUES (?, ?, ?, ?, ?, ?)",
            (name, int(stock), category, active, last_updated, image_db_path)
        )
        conn.commit()
        conn.close()

        self.show_popup("Success", "Product added successfully!")
        self.clear_fields()
        self.manager.current = "products"

    def clear_fields(self):
        self.ids.prod_name.text = ""
        self.ids.prod_stock.text = ""
        self.ids.prod_category.text = ""
        self.ids.prod_active.active = False
        self.ids.image_path_label.text = "No image selected"
        self.selected_image_path = None

    def show_popup(self, title, message):
        popup = Popup(title=title,
                      content=Label(text=message),
                      size_hint=(None, None), size=(300, 200))
        popup.open()
