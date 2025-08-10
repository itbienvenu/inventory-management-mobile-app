from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
import json
import csv
from datetime import datetime

class SupplierManager:
    """Handles all supplier-related data operations"""
    
    def __init__(self):
        self.suppliers = [
            {
                'id': 'acme_supplies',
                'name': 'Acme Supplies Ltd.',
                'category': 'Industrial Equipment & Materials',
                'status': 'Active',
                'contact': '+1-555-0123',
                'email': 'acme@supplies.com',
                'rating': 4.2,
                'avatar': 'AS',
                'color': [0.27, 0.54, 0.96, 1],
                'address': '123 Industrial Ave, Manufacturing City',
                'date_added': '2024-01-15'
            },
            {
                'id': 'global_systems',
                'name': 'Global Systems Inc.',
                'category': 'Technology & Software Solutions',
                'status': 'Active',
                'contact': '+1-555-0456',
                'email': 'info@globalsystems.com',
                'rating': 4.8,
                'avatar': 'GS',
                'color': [0.64, 0.42, 0.89, 1],
                'address': '456 Tech Boulevard, Silicon Valley',
                'date_added': '2024-02-20'
            }
        ]
        
    def get_all_suppliers(self):
        return self.suppliers
    
    def get_supplier(self, supplier_id):
        return next((s for s in self.suppliers if s['id'] == supplier_id), None)
    
    def add_supplier(self, supplier_data):
        supplier_data['id'] = supplier_data['name'].lower().replace(' ', '_').replace('.', '')
        supplier_data['date_added'] = datetime.now().strftime('%Y-%m-%d')
        self.suppliers.append(supplier_data)
        return supplier_data['id']
    
    def update_supplier(self, supplier_id, updated_data):
        supplier = self.get_supplier(supplier_id)
        if supplier:
            supplier.update(updated_data)
            return True
        return False
    
    def delete_supplier(self, supplier_id):
        self.suppliers = [s for s in self.suppliers if s['id'] != supplier_id]
    
    def filter_suppliers(self, search_term):
        if not search_term:
            return self.suppliers
        
        search_term = search_term.lower()
        return [s for s in self.suppliers if 
                search_term in s['name'].lower() or 
                search_term in s['category'].lower() or
                search_term in s['email'].lower()]
    
    def export_to_csv(self, filename='suppliers_export.csv'):
        """Export suppliers to CSV file"""
        fieldnames = ['name', 'category', 'status', 'contact', 'email', 'rating', 'address', 'date_added']
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for supplier in self.suppliers:
                writer.writerow({k: supplier.get(k, '') for k in fieldnames})
        
        return filename

class AddSupplierDialog(Popup):
    """Dialog for adding new suppliers"""
    
    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.title = 'Add New Supplier'
        self.size_hint = (0.8, 0.9)
        
        # Create form layout
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Form fields
        form_grid = GridLayout(cols=2, spacing=15, size_hint_y=None)
        form_grid.bind(minimum_height=form_grid.setter('height'))
        
        self.fields = {}
        form_fields = [
            ('Company Name*', 'name'),
            ('Category*', 'category'),
            ('Contact Phone', 'contact'),
            ('Email*', 'email'),
            ('Address', 'address'),
            ('Initial Rating (1-5)', 'rating')
        ]
        
        for label_text, field_name in form_fields:
            # Label
            label = Label(
                text=label_text,
                size_hint_y=None,
                height='40dp',
                halign='left',
                valign='middle'
            )
            label.bind(size=label.setter('text_size'))
            form_grid.add_widget(label)
            
            # Input field
            input_field = TextInput(
                multiline=False,
                size_hint_y=None,
                height='40dp',
                font_size='14sp'
            )
            self.fields[field_name] = input_field
            form_grid.add_widget(input_field)
        
        content.add_widget(form_grid)
        
        # Buttons
        button_layout = BoxLayout(
            size_hint_y=None,
            height='50dp',
            spacing=15
        )
        
        cancel_btn = Button(
            text='Cancel',
            background_color=[0.5, 0.55, 0.65, 1],
            on_press=self.dismiss
        )
        
        save_btn = Button(
            text='Save Supplier',
            background_color=[0.3, 0.69, 0.49, 1],
            on_press=self.save_supplier
        )
        
        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(save_btn)
        content.add_widget(button_layout)
        
        self.content = content
    
    def save_supplier(self, instance):
        """Validate and save new supplier"""
        # Get form data
        data = {}
        for field_name, field_widget in self.fields.items():
            data[field_name] = field_widget.text.strip()
        
        # Basic validation
        required_fields = ['name', 'category', 'email']
        missing_fields = [f for f in required_fields if not data[f]]
        
        if missing_fields:
            self.show_validation_error(f"Please fill in: {', '.join(missing_fields)}")
            return
        
        # Additional data processing
        data['status'] = 'Active'
        data['avatar'] = ''.join([word[0].upper() for word in data['name'].split()[:2]])
        data['color'] = [0.27, 0.54, 0.96, 1]  # Default blue
        
        # Handle rating
        try:
            data['rating'] = float(data['rating']) if data['rating'] else 0.0
            if data['rating'] < 0 or data['rating'] > 5:
                data['rating'] = 0.0
        except ValueError:
            data['rating'] = 0.0
        
        # Save and close
        self.callback(data)
        self.dismiss()
    
    def show_validation_error(self, message):
        """Show validation error popup"""
        error_popup = Popup(
            title='Validation Error',
            content=Label(text=message),
            size_hint=(0.6, 0.3)
        )
        error_popup.open()

class SuppliersScreen(Screen):
    """Main suppliers management screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.supplier_manager = SupplierManager()
        self.filtered_suppliers = self.supplier_manager.get_all_suppliers()
        
    def on_enter(self):
        """Called when screen is entered"""
        self.refresh_suppliers_list()
        
    def refresh_suppliers_list(self):
        """Refresh the suppliers display"""
        suppliers_grid = self.ids.suppliers_grid
        suppliers_count = self.ids.suppliers_count
        
        # Clear existing supplier cards (keep only the sample ones for now)
        # In a real implementation, you would dynamically create supplier cards
        
        # Update count
        active_count = len([s for s in self.filtered_suppliers if s['status'] == 'Active'])
        suppliers_count.text = f"{active_count} Active Suppliers"
        
    def open_add_supplier_dialog(self):
        """Open dialog to add new supplier"""
        dialog = AddSupplierDialog(callback=self.add_supplier_callback)
        dialog.open()
        
    def add_supplier_callback(self, supplier_data):
        """Callback when new supplier is added"""
        supplier_id = self.supplier_manager.add_supplier(supplier_data)
        self.create_supplier_card(supplier_data)
        self.refresh_suppliers_list()
        self.show_success_message(f"Supplier '{supplier_data['name']}' added successfully!")
        
    def filter_suppliers(self, search_text):
        """Filter suppliers based on search text"""
        self.filtered_suppliers = self.supplier_manager.filter_suppliers(search_text)
        self.refresh_suppliers_list()
        
    def view_supplier(self, supplier_id):
        """View supplier details"""
        supplier = self.supplier_manager.get_supplier(supplier_id)
        if supplier:
            self.show_supplier_details(supplier)
            
    def edit_supplier(self, supplier_id):
        """Edit supplier information"""
        supplier = self.supplier_manager.get_supplier(supplier_id)
        if supplier:
            dialog = EditSupplierDialog(supplier, callback=self.edit_supplier_callback)
            dialog.open()
            
    def edit_supplier_callback(self, supplier_id, updated_data):
        """Callback when supplier is edited"""
        if self.supplier_manager.update_supplier(supplier_id, updated_data):
            self.refresh_suppliers_list()
            self.show_success_message("Supplier updated successfully!")
            
    def confirm_delete_supplier(self, supplier_id):
        """Show confirmation dialog before deleting supplier"""
        supplier = self.supplier_manager.get_supplier(supplier_id)
        if supplier:
            content = BoxLayout(orientation='vertical', padding=20, spacing=15)
            
            message = Label(
                text=f"Are you sure you want to delete '{supplier['name']}'?\nThis action cannot be undone.",
                halign='center',
                valign='middle'
            )
            message.bind(size=message.setter('text_size'))
            content.add_widget(message)
            
            buttons = BoxLayout(size_hint_y=None, height='50dp', spacing=15)
            
            cancel_btn = Button(
                text='Cancel',
                background_color=[0.5, 0.55, 0.65, 1]
            )
            
            delete_btn = Button(
                text='Delete',
                background_color=[0.96, 0.35, 0.35, 1]
            )
            
            buttons.add_widget(cancel_btn)
            buttons.add_widget(delete_btn)
            content.add_widget(buttons)
            
            popup = Popup(
                title='Confirm Delete',
                content=content,
                size_hint=(0.6, 0.4)
            )
            
            cancel_btn.bind(on_press=popup.dismiss)
            delete_btn.bind(on_press=lambda x: self.delete_supplier_confirmed(supplier_id, popup))
            
            popup.open()
            
    def delete_supplier_confirmed(self, supplier_id, popup):
        """Actually delete the supplier"""
        supplier = self.supplier_manager.get_supplier(supplier_id)
        supplier_name = supplier['name'] if supplier else 'Unknown'
        
        self.supplier_manager.delete_supplier(supplier_id)
        popup.dismiss()
        self.refresh_suppliers_list()
        self.show_success_message(f"Supplier '{supplier_name}' deleted successfully!")
        
    def export_suppliers(self):
        """Export suppliers to CSV"""
        try:
            filename = self.supplier_manager.export_to_csv()
            self.show_success_message(f"Suppliers exported to {filename}")
        except Exception as e:
            self.show_error_message(f"Export failed: {str(e)}")
            
    def create_supplier_card(self, supplier):
        """Dynamically create a supplier card widget"""
        # This would create a new supplier card widget and add it to the grid
        # Implementation depends on your specific UI framework requirements
        pass
        
    def show_supplier_details(self, supplier):
        """Show detailed supplier information"""
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Supplier header
        header = BoxLayout(size_hint_y=None, height='80dp', spacing=20)
        
        # Avatar
        avatar_label = Label(
            text=supplier['avatar'],
            font_size='24sp',
            bold=True,
            color=[1, 1, 1, 1],
            size_hint_x=None,
            width='80dp'
        )
        header.add_widget(avatar_label)
        
        # Basic info
        info_layout = BoxLayout(orientation='vertical')
        info_layout.add_widget(Label(
            text=supplier['name'],
            font_size='20sp',
            bold=True,
            halign='left'
        ))
        info_layout.add_widget(Label(
            text=supplier['category'],
            font_size='14sp',
            halign='left'
        ))
        header.add_widget(info_layout)
        
        content.add_widget(header)
        
        # Details
        details_grid = GridLayout(cols=2, spacing=10, size_hint_y=None)
        details_grid.bind(minimum_height=details_grid.setter('height'))
        
        details = [
            ('Status:', supplier['status']),
            ('Contact:', supplier['contact']),
            ('Email:', supplier['email']),
            ('Rating:', f"★★★★☆ {supplier['rating']}"),
            ('Address:', supplier.get('address', 'N/A')),
            ('Date Added:', supplier.get('date_added', 'N/A'))
        ]
        
        for label_text, value in details:
            details_grid.add_widget(Label(text=label_text, halign='left'))
            details_grid.add_widget(Label(text=str(value), halign='left'))
        
        content.add_widget(details_grid)
        
        # Close button
        close_btn = Button(
            text='Close',
            size_hint_y=None,
            height='50dp',
            background_color=[0.5, 0.55, 0.65, 1]
        )
        content.add_widget(close_btn)
        
        popup = Popup(
            title=f"Supplier Details - {supplier['name']}",
            content=content,
            size_hint=(0.8, 0.8)
        )
        
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
        
    def show_success_message(self, message):
        """Show success message popup"""
        popup = Popup(
            title='Success',
            content=Label(text=message),
            size_hint=(0.6, 0.3)
        )
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 2)  # Auto-close after 2 seconds
        
    def show_error_message(self, message):
        """Show error message popup"""
        popup = Popup(
            title='Error',
            content=Label(text=message),
            size_hint=(0.6, 0.3)
        )
        popup.open()

class EditSupplierDialog(Popup):
    """Dialog for editing existing suppliers"""
    
    def __init__(self, supplier, callback, **kwargs):
        super().__init__(**kwargs)
        self.supplier = supplier
        self.callback = callback
        self.title = f'Edit Supplier - {supplier["name"]}'
        self.size_hint = (0.8, 0.9)
        
        # Create form layout (similar to AddSupplierDialog)
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Form fields
        form_grid = GridLayout(cols=2, spacing=15, size_hint_y=None)
        form_grid.bind(minimum_height=form_grid.setter('height'))
        
        self.fields = {}
        form_fields = [
            ('Company Name*', 'name'),
            ('Category*', 'category'),
            ('Contact Phone', 'contact'),
            ('Email*', 'email'),
            ('Address', 'address'),
            ('Rating (1-5)', 'rating'),
            ('Status', 'status')
        ]
        
        for label_text, field_name in form_fields:
            # Label
            label = Label(
                text=label_text,
                size_hint_y=None,
                height='40dp',
                halign='left',
                valign='middle'
            )
            label.bind(size=label.setter('text_size'))
            form_grid.add_widget(label)
            
            # Input field
            if field_name == 'status':
                # Create status dropdown (simplified as TextInput for now)
                input_field = TextInput(
                    text=supplier.get(field_name, ''),
                    multiline=False,
                    size_hint_y=None,
                    height='40dp',
                    font_size='14sp'
                )
            else:
                input_field = TextInput(
                    text=str(supplier.get(field_name, '')),
                    multiline=False,
                    size_hint_y=None,
                    height='40dp',
                    font_size='14sp'
                )
            
            self.fields[field_name] = input_field
            form_grid.add_widget(input_field)
        
        content.add_widget(form_grid)
        
        # Buttons
        button_layout = BoxLayout(
            size_hint_y=None,
            height='50dp',
            spacing=15
        )
        
        cancel_btn = Button(
            text='Cancel',
            background_color=[0.5, 0.55, 0.65, 1],
            on_press=self.dismiss
        )
        
        save_btn = Button(
            text='Save Changes',
            background_color=[0.3, 0.69, 0.49, 1],
            on_press=self.save_changes
        )
        
        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(save_btn)
        content.add_widget(button_layout)
        
        self.content = content
    
    def save_changes(self, instance):
        """Validate and save changes"""
        # Get form data
        updated_data = {}
        for field_name, field_widget in self.fields.items():
            updated_data[field_name] = field_widget.text.strip()
        
        # Basic validation
        required_fields = ['name', 'category', 'email']
        missing_fields = [f for f in required_fields if not updated_data[f]]
        
        if missing_fields:
            self.show_validation_error(f"Please fill in: {', '.join(missing_fields)}")
            return
        
        # Handle rating
        try:
            updated_data['rating'] = float(updated_data['rating']) if updated_data['rating'] else 0.0
            if updated_data['rating'] < 0 or updated_data['rating'] > 5:
                updated_data['rating'] = 0.0
        except ValueError:
            updated_data['rating'] = 0.0
        
        # Update avatar if name changed
        if updated_data['name'] != self.supplier['name']:
            updated_data['avatar'] = ''.join([word[0].upper() for word in updated_data['name'].split()[:2]])
        
        # Save and close
        self.callback(self.supplier['id'], updated_data)
        self.dismiss()
    
    def show_validation_error(self, message):
        """Show validation error popup"""
        error_popup = Popup(
            title='Validation Error',
            content=Label(text=message),
            size_hint=(0.6, 0.3)
        )
        error_popup.open()

class SuppliersApp(App):
    """Main application class for testing"""
    
    def build(self):
        return SuppliersScreen(name='suppliers')
    
    # Methods that would be called from the KV file
    def open_add_supplier_dialog(self):
        screen = self.root.get_screen('suppliers') if hasattr(self.root, 'get_screen') else self.root
        screen.open_add_supplier_dialog()
        
    def filter_suppliers(self, search_text):
        screen = self.root.get_screen('suppliers') if hasattr(self.root, 'get_screen') else self.root
        screen.filter_suppliers(search_text)
        
    def export_suppliers(self):
        screen = self.root.get_screen('suppliers') if hasattr(self.root, 'get_screen') else self.root
        screen.export_suppliers()
        
    def view_supplier(self, supplier_id):
        screen = self.root.get_screen('suppliers') if hasattr(self.root, 'get_screen') else self.root
        screen.view_supplier(supplier_id)
        
    def edit_supplier(self, supplier_id):
        screen = self.root.get_screen('suppliers') if hasattr(self.root, 'get_screen') else self.root
        screen.edit_supplier(supplier_id)
        
    def confirm_delete_supplier(self, supplier_id):
        screen = self.root.get_screen('suppliers') if hasattr(self.root, 'get_screen') else self.root
        screen.confirm_delete_supplier(supplier_id)

if __name__ == '__main__':
    SuppliersApp().run()