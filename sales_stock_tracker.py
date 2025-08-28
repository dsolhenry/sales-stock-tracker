from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.spinner import Spinner
from kivy.metrics import dp
from datetime import datetime
import json
import os

class SalesStockApp(App):
    def __init__(self):
        super().__init__()
        self.sales_data = []
        self.stock_data = {}
        self.customers = {}  # Store customer credit balances
        self.data_file = 'sales_stock_data.json'
        self.load_data()

    def build(self):
        # Main layout with tabs
        tab_panel = TabbedPanel()
        tab_panel.tab_height = dp(50)
        tab_panel.tab_width = dp(150)
        
        # Sales Tab
        sales_tab = TabbedPanelItem(text='Credit Sales')
        sales_tab.add_widget(self.create_sales_layout())
        tab_panel.add_widget(sales_tab)
        
        # Stock Tab
        stock_tab = TabbedPanelItem(text='Stock Management')
        stock_tab.add_widget(self.create_stock_layout())
        tab_panel.add_widget(stock_tab)
        
        # Reports Tab
        reports_tab = TabbedPanelItem(text='Reports')
        reports_tab.add_widget(self.create_reports_layout())
        tab_panel.add_widget(reports_tab)
        
        return tab_panel

    def create_sales_layout(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Balance display
        self.balance_label = Label(
            text=f'Total Outstanding Credit: ${self.get_total_outstanding():.2f}',
            size_hint_y=None,
            height=dp(40),
            font_size=dp(18),
            bold=True
        )
        main_layout.add_widget(self.balance_label)
        
        # Input form
        form_layout = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(240))
        
        # Customer selection/addition
        form_layout.add_widget(Label(text='Customer:', size_hint_y=None, height=dp(40)))
        customer_container = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80))
        
        self.customer_spinner = Spinner(
            text='Select Customer',
            values=['Add New Customer'] + list(self.customers.keys()),
            size_hint_y=None,
            height=dp(40)
        )
        self.customer_spinner.bind(text=self.on_customer_selected)
        customer_container.add_widget(self.customer_spinner)
        
        self.new_customer_input = TextInput(
            hint_text='Enter new customer name',
            size_hint_y=None,
            height=dp(40),
            opacity=0,
            disabled=True
        )
        customer_container.add_widget(self.new_customer_input)
        form_layout.add_widget(customer_container)
        
        form_layout.add_widget(Label(text='Product:', size_hint_y=None, height=dp(40)))
        self.product_spinner = Spinner(
            text='Select Product',
            values=list(self.stock_data.keys()) if self.stock_data else ['No products available'],
            size_hint_y=None,
            height=dp(40)
        )
        form_layout.add_widget(self.product_spinner)
        
        form_layout.add_widget(Label(text='Quantity:', size_hint_y=None, height=dp(40)))
        self.quantity_input = TextInput(input_filter='float', size_hint_y=None, height=dp(40))
        form_layout.add_widget(self.quantity_input)
        
        form_layout.add_widget(Label(text='Unit Price:', size_hint_y=None, height=dp(40)))
        self.price_spinner = Spinner(
            text='Select Price',
            values=['500', '1000'],
            size_hint_y=None,
            height=dp(40)
        )
        form_layout.add_widget(self.price_spinner)
        
        main_layout.add_widget(form_layout)
        
        # Evenly spaced buttons
        button_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(5))
        
        add_sale_btn = Button(text='Record Credit Sale', size_hint_x=1)
        add_sale_btn.bind(on_press=self.add_credit_sale)
        button_layout.add_widget(add_sale_btn)
        
        payment_btn = Button(text='Record Payment', size_hint_x=1)
        payment_btn.bind(on_press=self.record_payment)
        button_layout.add_widget(payment_btn)
        
        clear_btn = Button(text='Clear Form', size_hint_x=1)
        clear_btn.bind(on_press=self.clear_form)
        button_layout.add_widget(clear_btn)
        
        main_layout.add_widget(button_layout)
        
        # Recent sales list
        main_layout.add_widget(Label(text='Recent Credit Sales:', size_hint_y=None, height=dp(30)))
        
        self.sales_scroll = ScrollView()
        self.sales_list = BoxLayout(orientation='vertical', size_hint_y=None)
        self.sales_list.bind(minimum_height=self.sales_list.setter('height'))
        self.sales_scroll.add_widget(self.sales_list)
        main_layout.add_widget(self.sales_scroll)
        
        self.update_sales_display()
        
        return main_layout

    def create_stock_layout(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Add new product form
        main_layout.add_widget(Label(text='Add New Product:', size_hint_y=None, height=dp(30), bold=True))
        
        form_layout = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(120))
        
        form_layout.add_widget(Label(text='Product Name:', size_hint_y=None, height=dp(40)))
        self.new_product_input = TextInput(size_hint_y=None, height=dp(40))
        form_layout.add_widget(self.new_product_input)
        
        form_layout.add_widget(Label(text='Initial Stock:', size_hint_y=None, height=dp(40)))
        self.initial_stock_input = TextInput(input_filter='float', size_hint_y=None, height=dp(40))
        form_layout.add_widget(self.initial_stock_input)
        
        main_layout.add_widget(form_layout)
        
        # Evenly spaced buttons for stock management
        stock_button_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(5))
        
        add_product_btn = Button(text='Add Product', size_hint_x=1)
        add_product_btn.bind(on_press=self.add_product)
        stock_button_layout.add_widget(add_product_btn)
        
        clear_stock_btn = Button(text='Clear Form', size_hint_x=1)
        clear_stock_btn.bind(on_press=self.clear_stock_form)
        stock_button_layout.add_widget(clear_stock_btn)
        
        main_layout.add_widget(stock_button_layout)
        
        # Stock adjustment form
        main_layout.add_widget(Label(text='Adjust Stock:', size_hint_y=None, height=dp(30), bold=True))
        
        adjust_layout = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(120))
        
        adjust_layout.add_widget(Label(text='Product:', size_hint_y=None, height=dp(40)))
        self.adjust_product_spinner = Spinner(
            text='Select Product',
            values=list(self.stock_data.keys()) if self.stock_data else ['No products available'],
            size_hint_y=None,
            height=dp(40)
        )
        adjust_layout.add_widget(self.adjust_product_spinner)
        
        adjust_layout.add_widget(Label(text='Adjustment (+/-):', size_hint_y=None, height=dp(40)))
        self.adjustment_input = TextInput(input_filter='float', size_hint_y=None, height=dp(40))
        adjust_layout.add_widget(self.adjustment_input)
        
        main_layout.add_widget(adjust_layout)
        
        # Evenly spaced buttons for adjustment
        adjust_button_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(5))
        
        adjust_btn = Button(text='Adjust Stock', size_hint_x=1)
        adjust_btn.bind(on_press=self.adjust_stock)
        adjust_button_layout.add_widget(adjust_btn)
        
        clear_adjust_btn = Button(text='Clear Form', size_hint_x=1)
        clear_adjust_btn.bind(on_press=self.clear_adjust_form)
        adjust_button_layout.add_widget(clear_adjust_btn)
        
        main_layout.add_widget(adjust_button_layout)
        
        # Current stock display
        main_layout.add_widget(Label(text='Current Stock:', size_hint_y=None, height=dp(30), bold=True))
        
        self.stock_scroll = ScrollView()
        self.stock_list = BoxLayout(orientation='vertical', size_hint_y=None)
        self.stock_list.bind(minimum_height=self.stock_list.setter('height'))
        self.stock_scroll.add_widget(self.stock_list)
        main_layout.add_widget(self.stock_scroll)
        
        self.update_stock_display()
        
        return main_layout

    def create_reports_layout(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Summary section
        self.summary_label = Label(
            text='',
            size_hint_y=None,
            height=dp(120),
            text_size=(None, None),
            valign='top'
        )
        main_layout.add_widget(self.summary_label)
        
        # Evenly spaced buttons for reports
        report_button_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(5))
        
        refresh_btn = Button(text='Refresh Reports', size_hint_x=1)
        refresh_btn.bind(on_press=self.update_reports)
        report_button_layout.add_widget(refresh_btn)
        
        export_btn = Button(text='Export Data', size_hint_x=1)
        export_btn.bind(on_press=self.export_data)
        report_button_layout.add_widget(export_btn)
        
        main_layout.add_widget(report_button_layout)
        
        # Detailed report
        self.report_scroll = ScrollView()
        self.report_list = BoxLayout(orientation='vertical', size_hint_y=None)
        self.report_list.bind(minimum_height=self.report_list.setter('height'))
        self.report_scroll.add_widget(self.report_list)
        main_layout.add_widget(self.report_scroll)
        
        self.update_reports()
        
        return main_layout

    def on_customer_selected(self, spinner, text):
        """Handle customer selection - show input field for new customer"""
        if text == 'Add New Customer':
            self.new_customer_input.opacity = 1
            self.new_customer_input.disabled = False
        else:
            self.new_customer_input.opacity = 0
            self.new_customer_input.disabled = True
            self.new_customer_input.text = ''

    def get_selected_customer(self):
        """Get the currently selected or entered customer name"""
        if self.customer_spinner.text == 'Add New Customer':
            return self.new_customer_input.text.strip()
        elif self.customer_spinner.text != 'Select Customer':
            return self.customer_spinner.text
        return None

    def add_credit_sale(self, instance):
        try:
            customer = self.get_selected_customer()
            product = self.product_spinner.text
            quantity = float(self.quantity_input.text or 0)
            unit_price = float(self.price_spinner.text) if self.price_spinner.text != 'Select Price' else 0
            
            if not customer or product == 'Select Product' or quantity <= 0 or unit_price <= 0:
                self.show_popup('Error', 'Please fill all fields with valid values')
                return
            
            # Check stock availability
            if product not in self.stock_data or self.stock_data[product] < quantity:
                self.show_popup('Error', f'Insufficient stock for {product}')
                return
            
            total_amount = quantity * unit_price
            
            # Record the sale
            sale = {
                'id': len(self.sales_data) + 1,
                'customer': customer,
                'product': product,
                'quantity': quantity,
                'unit_price': unit_price,
                'total_amount': total_amount,
                'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'status': 'credit',
                'paid_amount': 0.0
            }
            
            self.sales_data.append(sale)
            
            # Update or add customer
            if customer not in self.customers:
                self.customers[customer] = 0.0
            self.customers[customer] += total_amount
            
            # Update stock
            self.stock_data[product] -= quantity
            
            # Update customer spinner values if new customer was added
            if customer not in self.customer_spinner.values:
                self.customer_spinner.values = ['Add New Customer'] + list(self.customers.keys())
            
            # Clear form
            self.clear_form(None)
            
            # Update displays
            self.update_balance_display()
            self.update_sales_display()
            self.update_stock_display()
            
            # Save data
            self.save_data()
            
            self.show_popup('Success', f'Credit sale recorded: ${total_amount:.2f} for {customer}')
            
        except ValueError:
            self.show_popup('Error', 'Please enter valid numbers for quantity and select a valid price')

    def record_payment(self, instance):
        if not self.customers:
            self.show_popup('Error', 'No customers with credit found')
            return
        
        # Create payment popup
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        # Customer selection with current balance display
        content.add_widget(Label(text='Select Customer:', size_hint_y=None, height=dp(30)))
        
        customer_spinner = Spinner(
            text='Select Customer',
            values=[f"{customer} (${balance:.2f})" for customer, balance in self.customers.items() if balance > 0],
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(customer_spinner)
        
        content.add_widget(Label(text='Payment Amount:', size_hint_y=None, height=dp(30)))
        amount_input = TextInput(
            hint_text='Enter payment amount',
            input_filter='float',
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(amount_input)
        
        # Evenly spaced buttons in popup
        button_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(5))
        
        def process_payment(instance):
            try:
                customer_text = customer_spinner.text
                if customer_text == 'Select Customer':
                    self.show_popup('Error', 'Please select a customer')
                    return
                
                # Extract customer name from "Customer ($balance)" format
                customer = customer_text.split(' (')[0]
                amount = float(amount_input.text or 0)
                
                if amount <= 0:
                    self.show_popup('Error', 'Please enter a valid payment amount')
                    return
                
                if amount > self.customers[customer]:
                    self.show_popup('Error', 'Payment amount exceeds customer balance')
                    return
                
                # Update customer balance
                self.customers[customer] -= amount
                
                # Update sales records
                remaining_payment = amount
                for sale in self.sales_data:
                    if sale['customer'] == customer and sale['status'] == 'credit':
                        unpaid = sale['total_amount'] - sale['paid_amount']
                        if unpaid > 0 and remaining_payment > 0:
                            payment_applied = min(remaining_payment, unpaid)
                            sale['paid_amount'] += payment_applied
                            remaining_payment -= payment_applied
                            
                            if sale['paid_amount'] >= sale['total_amount']:
                                sale['status'] = 'paid'
                
                # Remove customer if balance is zero
                if self.customers[customer] <= 0.01:  # Account for floating point precision
                    del self.customers[customer]
                
                # Update customer spinner values
                self.customer_spinner.values = ['Add New Customer'] + list(self.customers.keys())
                
                self.update_balance_display()
                self.update_sales_display()
                self.save_data()
                popup.dismiss()
                self.show_popup('Success', f'Payment of ${amount:.2f} recorded for {customer}')
                
            except ValueError:
                self.show_popup('Error', 'Please enter valid numbers')
        
        pay_btn = Button(text='Record Payment', size_hint_x=1)
        pay_btn.bind(on_press=process_payment)
        button_layout.add_widget(pay_btn)
        
        cancel_btn = Button(text='Cancel', size_hint_x=1)
        button_layout.add_widget(cancel_btn)
        
        content.add_widget(button_layout)
        
        popup = Popup(title='Record Payment', content=content, size_hint=(0.9, 0.7))
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()

    def add_product(self, instance):
        try:
            product_name = self.new_product_input.text.strip()
            initial_stock = float(self.initial_stock_input.text or 0)
            
            if not product_name or initial_stock < 0:
                self.show_popup('Error', 'Please enter valid product name and stock')
                return
            
            if product_name in self.stock_data:
                self.show_popup('Error', 'Product already exists')
                return
            
            self.stock_data[product_name] = initial_stock
            
            # Update spinners
            self.product_spinner.values = list(self.stock_data.keys())
            self.adjust_product_spinner.values = list(self.stock_data.keys())
            
            # Clear inputs
            self.clear_stock_form(None)
            
            # Update display
            self.update_stock_display()
            self.save_data()
            
            self.show_popup('Success', f'Product "{product_name}" added successfully')
            
        except ValueError:
            self.show_popup('Error', 'Please enter valid numbers')

    def adjust_stock(self, instance):
        try:
            product = self.adjust_product_spinner.text
            adjustment = float(self.adjustment_input.text or 0)
            
            if product == 'Select Product':
                self.show_popup('Error', 'Please select a product')
                return
            
            new_stock = self.stock_data[product] + adjustment
            if new_stock < 0:
                self.show_popup('Error', 'Stock cannot be negative')
                return
            
            self.stock_data[product] = new_stock
            
            # Clear input
            self.clear_adjust_form(None)
            
            # Update display
            self.update_stock_display()
            self.save_data()
            
            self.show_popup('Success', f'Stock adjusted for {product}')
            
        except ValueError:
            self.show_popup('Error', 'Please enter valid numbers')

    def get_total_outstanding(self):
        """Calculate total outstanding credit across all customers"""
        return sum(self.customers.values())

    def clear_form(self, instance):
        """Clear the sales form"""
        self.customer_spinner.text = 'Select Customer'
        self.new_customer_input.text = ''
        self.new_customer_input.opacity = 0
        self.new_customer_input.disabled = True
        self.product_spinner.text = 'Select Product'
        self.quantity_input.text = ''
        self.price_spinner.text = 'Select Price'

    def clear_stock_form(self, instance):
        """Clear the add product form"""
        self.new_product_input.text = ''
        self.initial_stock_input.text = ''

    def clear_adjust_form(self, instance):
        """Clear the stock adjustment form"""
        self.adjust_product_spinner.text = 'Select Product'
        self.adjustment_input.text = ''

    def update_balance_display(self):
        total_outstanding = self.get_total_outstanding()
        self.balance_label.text = f'Total Outstanding Credit: ${total_outstanding:.2f}'

    def update_sales_display(self):
        self.sales_list.clear_widgets()
        
        recent_sales = sorted(self.sales_data, key=lambda x: x['date'], reverse=True)[:15]
        
        for sale in recent_sales:
            sale_info = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(70))
            
            info_text = f"{sale['customer']} - {sale['product']} x{sale['quantity']}\n"
            info_text += f"${sale['total_amount']:.2f} ({sale['status']}) - {sale['date']}"
            
            if sale['status'] == 'credit':
                remaining = sale['total_amount'] - sale['paid_amount']
                info_text += f"\nRemaining: ${remaining:.2f}"
            
            label = Label(
                text=info_text,
                text_size=(dp(350), None),
                size_hint_x=1,
                valign='middle',
                halign='left'
            )
            sale_info.add_widget(label)
            
            self.sales_list.add_widget(sale_info)

    def update_stock_display(self):
        self.stock_list.clear_widgets()
        
        for product, quantity in sorted(self.stock_data.items()):
            stock_info = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
            
            color = [1, 0.3, 0.3, 1] if quantity < 10 else [1, 1, 1, 1]  # Red for low stock
            
            label = Label(
                text=f"{product}: {quantity}",
                color=color,
                size_hint_x=1,
                halign='left',
                text_size=(dp(300), None)
            )
            stock_info.add_widget(label)
            
            self.stock_list.add_widget(stock_info)

    def update_reports(self, instance=None):
        total_outstanding = self.get_total_outstanding()
        total_sales = sum(sale['total_amount'] for sale in self.sales_data)
        total_paid = sum(sale['paid_amount'] for sale in self.sales_data)
        num_customers = len(self.customers)
        
        summary_text = f"Total Outstanding Credit: ${total_outstanding:.2f}\n"
        summary_text += f"Total Sales: ${total_sales:.2f}\n"
        summary_text += f"Total Payments Received: ${total_paid:.2f}\n"
        summary_text += f"Active Customers: {num_customers}\n"
        summary_text += f"Products in Stock: {len(self.stock_data)}"
        
        self.summary_label.text = summary_text
        self.summary_label.text_size = (dp(350), None)
        
        # Update detailed report
        self.report_list.clear_widgets()
        
        if self.customers:
            self.report_list.add_widget(Label(
                text='Customers with Outstanding Credit:',
                size_hint_y=None,
                height=dp(40),
                bold=True
            ))
            
            for customer, amount in sorted(self.customers.items(), key=lambda x: x[1], reverse=True):
                if amount > 0:
                    label = Label(
                        text=f"{customer}: ${amount:.2f}",
                        size_hint_y=None,
                        height=dp(35),
                        halign='left',
                        text_size=(dp(300), None)
                    )
                    self.report_list.add_widget(label)

    def export_data(self, instance):
        """Export data functionality placeholder"""
        self.show_popup('Export', 'Data export functionality would be implemented here')

    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', padding=dp(10))
        content.add_widget(Label(text=message, text_size=(dp(250), None), halign='center'))
        
        close_btn = Button(text='Close', size_hint_y=None, height=dp(40))
        content.add_widget(close_btn)
        
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.5))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def save_data(self):
        data = {
            'sales_data': self.sales_data,
            'stock_data': self.stock_data,
            'customers': self.customers
        }
        try:
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")

    def load_data(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.sales_data = data.get('sales_data', [])
                    self.stock_data = data.get('stock_data', {})
                    self.customers = data.get('customers', {})
        except Exception as e:
            print(f"Error loading data: {e}")
            self.sales_data = []
            self.stock_data = {}
            self.customers = {}

if __name__ == '__main__':
    SalesStockApp().run()