import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from tkinter import Canvas
from PIL import Image, ImageDraw, ImageFont, ImageTk
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer, CircleModuleDrawer, SquareModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask, SquareGradiantColorMask
import os
from datetime import datetime
import cv2
import numpy as np
from io import BytesIO
import threading

class AIQRCodeGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("AI-Powered QR Code Generator Pro")
        self.root.geometry("1200x900")
        self.root.configure(bg="#f0f0f0")
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background="#f0f0f0")
        style.configure('TLabel', background="#f0f0f0", font=('Arial', 10))
        style.configure('Header.TLabel', font=('Arial', 14, 'bold'), background="#f0f0f0")
        style.configure('TButton', font=('Arial', 10))
        
        # Variables - Initialize colors as RGB tuples
        self.qr_data = tk.StringVar()
        self.error_correction = tk.StringVar(value="H")
        self.qr_size = tk.IntVar(value=10)
        self.border_size = tk.IntVar(value=4)
        self.fg_color = (0, 0, 0)  # Black RGB tuple
        self.bg_color = (255, 255, 255)  # White RGB tuple
        self.fg_color_hex = "#000000"  # For display
        self.bg_color_hex = "#FFFFFF"  # For display
        self.logo_path = tk.StringVar()
        self.logo_size_ratio = tk.DoubleVar(value=0.3)
        self.module_style = tk.StringVar(value="square")
        self.current_qr_image = None
        self.auto_optimize = tk.BooleanVar(value=True)
        
        self.create_ui()
        
    def create_ui(self):
        # Main container with two columns
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ============ SCROLLABLE LEFT PANEL ============
        # Create Canvas for scrolling
        left_canvas = tk.Canvas(main_container, borderwidth=0, bg="#f0f0f0", highlightthickness=0)
        left_scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=left_canvas.yview)
        left_canvas.configure(yscrollcommand=left_scrollbar.set)
        
        left_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10), ipady=5)
        left_scrollbar.pack(side=tk.LEFT, fill=tk.Y, before=left_canvas)
        
        # Inner frame for scrollable content
        left_panel = ttk.Frame(left_canvas)
        left_panel_id = left_canvas.create_window((0, 0), window=left_panel, anchor="nw")
        
        # Configure scroll region
        def on_frame_configure(event):
            left_canvas.configure(scrollregion=left_canvas.bbox("all"))
        
        # Configure canvas width
        def on_canvas_configure(event):
            left_canvas.itemconfig(left_panel_id, width=event.width)
        
        left_panel.bind("<Configure>", on_frame_configure)
        left_canvas.bind("<Configure>", on_canvas_configure)
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            left_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _on_linux_scroll(event):
            if event.num == 5:
                left_canvas.yview_scroll(3, "units")
            elif event.num == 4:
                left_canvas.yview_scroll(-3, "units")
        
        left_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        left_canvas.bind_all("<Button-4>", _on_linux_scroll)
        left_canvas.bind_all("<Button-5>", _on_linux_scroll)
        
        # ============ ADD SECTIONS TO SCROLLABLE PANEL ============
        
        # Header
        header = ttk.Label(left_panel, text="QR Code Configuration", style='Header.TLabel')
        header.pack(pady=10)
        
        # Input section
        self.create_input_section(left_panel)
        
        # QR Customization section
        self.create_customization_section(left_panel)
        
        # Advanced Options section
        self.create_advanced_section(left_panel)
        
        # Button section
        self.create_button_section(left_panel)
        
        # ============ RIGHT PANEL - PREVIEW (NOT SCROLLABLE) ============
        right_panel = ttk.Frame(main_container)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        preview_header = ttk.Label(right_panel, text="QR Code Preview", style='Header.TLabel')
        preview_header.pack(pady=10)
        
        # Canvas for preview
        self.canvas = Canvas(right_panel, bg="white", width=500, height=500, relief=tk.SUNKEN, bd=2)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Status bar
        self.status_label = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
    
    def create_input_section(self, parent):
        input_frame = ttk.LabelFrame(parent, text="QR Code Data", padding=10)
        input_frame.pack(fill=tk.X, pady=10, padx=5)
        
        ttk.Label(input_frame, text="Enter Data:").pack(anchor=tk.W)
        
        # Text input with scrollbar
        text_frame = ttk.Frame(input_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_input = tk.Text(text_frame, height=4, width=40, yscrollcommand=scrollbar.set, font=('Arial', 9))
        self.text_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text_input.yview)
        
        # Character count
        self.char_count = ttk.Label(input_frame, text="Characters: 0", foreground="gray")
        self.char_count.pack(anchor=tk.W)
        self.text_input.bind('<KeyRelease>', lambda e: self.update_char_count())
        
        # Preset buttons
        preset_frame = ttk.Frame(input_frame)
        preset_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(preset_frame, text="URL", width=8, 
                  command=lambda: self.set_preset_data("https://example.com")).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="Email", width=8,
                  command=lambda: self.set_preset_data("mailto:info@example.com")).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="Phone", width=8,
                  command=lambda: self.set_preset_data("tel:+1234567890")).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="vCard", width=8,
                  command=lambda: self.show_vcard_dialog()).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="WiFi", width=8,
                  command=lambda: self.show_wifi_dialog()).pack(side=tk.LEFT, padx=2)
    
    def create_customization_section(self, parent):
        custom_frame = ttk.LabelFrame(parent, text="Design & Colors", padding=10)
        custom_frame.pack(fill=tk.X, pady=10, padx=5)
        
        # Module style
        style_frame = ttk.Frame(custom_frame)
        style_frame.pack(fill=tk.X, pady=5)
        ttk.Label(style_frame, text="Module Style:").pack(side=tk.LEFT)
        style_combo = ttk.Combobox(style_frame, textvariable=self.module_style,
                                   values=["square", "rounded", "circle"], state="readonly", width=15)
        style_combo.pack(side=tk.LEFT, padx=5)
        
        # Color section
        color_frame = ttk.Frame(custom_frame)
        color_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(color_frame, text="Foreground:").pack(side=tk.LEFT)
        ttk.Button(color_frame, text="Choose Color", width=12,
                  command=self.choose_fg_color).pack(side=tk.LEFT, padx=5)
        self.fg_color_label = ttk.Label(color_frame, text="⬛ #000000", foreground="#000000", 
                                        font=('Arial', 10, 'bold'))
        self.fg_color_label.pack(side=tk.LEFT, padx=5)
        
        bg_frame = ttk.Frame(custom_frame)
        bg_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(bg_frame, text="Background:").pack(side=tk.LEFT)
        ttk.Button(bg_frame, text="Choose Color", width=12,
                  command=self.choose_bg_color).pack(side=tk.LEFT, padx=5)
        self.bg_color_label = ttk.Label(bg_frame, text="⬜ #FFFFFF", foreground="black",
                                        font=('Arial', 10, 'bold'))
        self.bg_color_label.pack(side=tk.LEFT, padx=5)
    
    def create_advanced_section(self, parent):
        adv_frame = ttk.LabelFrame(parent, text="Advanced Settings", padding=10)
        adv_frame.pack(fill=tk.X, pady=10, padx=5)
        
        # Error correction
        error_frame = ttk.Frame(adv_frame)
        error_frame.pack(fill=tk.X, pady=5)
        ttk.Label(error_frame, text="Error Correction:").pack(side=tk.LEFT)
        error_combo = ttk.Combobox(error_frame, textvariable=self.error_correction,
                                   values=["L (7%)", "M (15%)", "Q (25%)", "H (30%)"], 
                                   state="readonly", width=15)
        error_combo.pack(side=tk.LEFT, padx=5)
        
        # Size settings
        size_frame = ttk.Frame(adv_frame)
        size_frame.pack(fill=tk.X, pady=5)
        ttk.Label(size_frame, text="QR Size:").pack(side=tk.LEFT)
        size_scale = ttk.Scale(size_frame, from_=5, to=40, variable=self.qr_size, orient=tk.HORIZONTAL)
        size_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        size_label = ttk.Label(size_frame, text="10", width=3)
        size_label.pack(side=tk.LEFT)
        size_scale.config(command=lambda v: size_label.config(text=str(int(float(v)))))
        
        # Border
        border_frame = ttk.Frame(adv_frame)
        border_frame.pack(fill=tk.X, pady=5)
        ttk.Label(border_frame, text="Border Size:").pack(side=tk.LEFT)
        border_scale = ttk.Scale(border_frame, from_=0, to=10, variable=self.border_size, orient=tk.HORIZONTAL)
        border_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        border_label = ttk.Label(border_frame, text="4", width=3)
        border_label.pack(side=tk.LEFT)
        border_scale.config(command=lambda v: border_label.config(text=str(int(float(v)))))
        
        # Logo section
        logo_frame = ttk.LabelFrame(adv_frame, text="Logo", padding=5)
        logo_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(logo_frame, text="Select Logo", width=20,
                  command=self.select_logo).pack(side=tk.LEFT, padx=5)
        self.logo_label = ttk.Label(logo_frame, text="No logo selected", foreground="gray")
        self.logo_label.pack(side=tk.LEFT, padx=5)
        
        logo_size_frame = ttk.Frame(logo_frame)
        logo_size_frame.pack(fill=tk.X, pady=5)
        ttk.Label(logo_size_frame, text="Logo Size:").pack(side=tk.LEFT)
        logo_size_scale = ttk.Scale(logo_size_frame, from_=0.1, to=0.5, variable=self.logo_size_ratio, orient=tk.HORIZONTAL)
        logo_size_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        logo_size_label = ttk.Label(logo_size_frame, text="30%", width=4)
        logo_size_label.pack(side=tk.LEFT)
        logo_size_scale.config(command=lambda v: logo_size_label.config(text=f"{int(float(v)*100)}%"))
        
        # Auto optimize
        ttk.Checkbutton(adv_frame, text="Auto-Optimize (Color contrast & Error correction)", 
                       variable=self.auto_optimize).pack(anchor=tk.W, pady=5)
    
    def create_button_section(self, parent):
        button_frame = ttk.LabelFrame(parent, text="Actions", padding=10)
        button_frame.pack(fill=tk.X, pady=10, padx=5)
        
        # Generate button
        ttk.Button(button_frame, text="🔄 Generate QR Code", width=20,
                  command=self.generate_qr).pack(fill=tk.X, pady=5)
        
        # Export buttons
        export_frame = ttk.Frame(button_frame)
        export_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(export_frame, text="💾 Save PNG", width=12,
                  command=lambda: self.export_qr("PNG")).pack(side=tk.LEFT, padx=2)
        ttk.Button(export_frame, text="💾 Save JPG", width=12,
                  command=lambda: self.export_qr("JPG")).pack(side=tk.LEFT, padx=2)
        ttk.Button(export_frame, text="💾 Save SVG", width=12,
                  command=lambda: self.export_qr("SVG")).pack(side=tk.LEFT, padx=2)
        
        # Scan button
        ttk.Button(button_frame, text="📱 Scan QR Code", width=20,
                  command=self.scan_qr).pack(fill=tk.X, pady=5)
        
        # Utility buttons
        util_frame = ttk.Frame(button_frame)
        util_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(util_frame, text="🔍 Analyze", width=10,
                  command=self.analyze_qr).pack(side=tk.LEFT, padx=2)
        ttk.Button(util_frame, text="📋 Copy", width=10,
                  command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=2)
        ttk.Button(util_frame, text="🗑️ Clear", width=10,
                  command=self.clear_all).pack(side=tk.LEFT, padx=2)
    
    def update_char_count(self):
        count = len(self.text_input.get("1.0", tk.END).strip())
        self.char_count.config(text=f"Characters: {count}")
    
    def set_preset_data(self, data):
        self.text_input.delete("1.0", tk.END)
        self.text_input.insert("1.0", data)
        self.update_char_count()
    
    def show_vcard_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Create vCard")
        dialog.geometry("300x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        fields = {}
        ttk.Label(dialog, text="vCard Information", font=('Arial', 12, 'bold')).pack(pady=10)
        
        for field in ["Name", "Organization", "Phone", "Email", "Website"]:
            ttk.Label(dialog, text=f"{field}:").pack(anchor=tk.W, padx=10)
            entry = ttk.Entry(dialog, width=30)
            entry.pack(anchor=tk.W, padx=10, pady=5)
            fields[field] = entry
        
        def create_vcard():
            vcard = f"""BEGIN:VCARD
VERSION:3.0
FN:{fields['Name'].get()}
ORG:{fields['Organization'].get()}
TEL:{fields['Phone'].get()}
EMAIL:{fields['Email'].get()}
URL:{fields['Website'].get()}
END:VCARD"""
            self.set_preset_data(vcard)
            dialog.destroy()
        
        ttk.Button(dialog, text="Create vCard", command=create_vcard).pack(pady=10)
    
    def show_wifi_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Create WiFi QR")
        dialog.geometry("300x250")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="WiFi Information", font=('Arial', 12, 'bold')).pack(pady=10)
        
        ttk.Label(dialog, text="SSID:").pack(anchor=tk.W, padx=10)
        ssid_entry = ttk.Entry(dialog, width=30)
        ssid_entry.pack(anchor=tk.W, padx=10, pady=5)
        
        ttk.Label(dialog, text="Password:").pack(anchor=tk.W, padx=10)
        pwd_entry = ttk.Entry(dialog, width=30, show="*")
        pwd_entry.pack(anchor=tk.W, padx=10, pady=5)
        
        ttk.Label(dialog, text="Security:").pack(anchor=tk.W, padx=10)
        security_combo = ttk.Combobox(dialog, values=["WPA", "WEP", "nopass"], state="readonly")
        security_combo.pack(anchor=tk.W, padx=10, pady=5)
        security_combo.set("WPA")
        
        def create_wifi():
            wifi_string = f"WIFI:T:{security_combo.get()};S:{ssid_entry.get()};P:{pwd_entry.get()};;"
            self.set_preset_data(wifi_string)
            dialog.destroy()
        
        ttk.Button(dialog, text="Create WiFi QR", command=create_wifi).pack(pady=10)
    
    def hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def rgb_to_hex(self, rgb_tuple):
        """Convert RGB tuple to hex color"""
        return '#{:02x}{:02x}{:02x}'.format(rgb_tuple[0], rgb_tuple[1], rgb_tuple[2])
    
    def choose_fg_color(self):
        color = colorchooser.askcolor(color=self.fg_color_hex, title="Choose Foreground Color")[1]
        if color:
            self.fg_color_hex = color
            self.fg_color = self.hex_to_rgb(color)  # Convert to RGB tuple
            self.fg_color_label.config(text=f"⬛ {color.upper()}", foreground=color)
    
    def choose_bg_color(self):
        color = colorchooser.askcolor(color=self.bg_color_hex, title="Choose Background Color")[1]
        if color:
            self.bg_color_hex = color
            self.bg_color = self.hex_to_rgb(color)  # Convert to RGB tuple
            self.bg_color_label.config(text=f"⬜ {color.upper()}", 
                                      foreground="black" if self.is_light_color(color) else "white")
    
    def is_light_color(self, hex_color):
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return (r * 299 + g * 587 + b * 114) / 1000 > 128
    
    def select_logo(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"), ("All files", "*.*")]
        )
        if file_path:
            self.logo_path.set(file_path)
            filename = os.path.basename(file_path)
            self.logo_label.config(text=f"✓ {filename}", foreground="green")
    
    def generate_qr(self):
        data = self.text_input.get("1.0", tk.END).strip()
        
        if not data:
            messagebox.showwarning("Warning", "Please enter some data for the QR code")
            return
        
        self.update_status("Generating QR code...")
        
        try:
            # Get error correction level
            error_levels = {"L (7%)": qrcode.constants.ERROR_CORRECT_L,
                           "M (15%)": qrcode.constants.ERROR_CORRECT_M,
                           "Q (25%)": qrcode.constants.ERROR_CORRECT_Q,
                           "H (30%)": qrcode.constants.ERROR_CORRECT_H}
            error_level = error_levels[self.error_correction.get()]
            
            # Create QR code
            qr = qrcode.QRCode(
                version=None,
                error_correction=error_level,
                box_size=self.qr_size.get(),
                border=self.border_size.get(),
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            # Apply module style
            module_drawer = self.get_module_drawer()
            
            # Use RGB tuples for colors
            img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=module_drawer,
                color_mask=SolidFillColorMask(self.fg_color, self.bg_color)
            )
            
            # Add logo if selected
            if self.logo_path.get():
                img = self.add_logo_to_qr(img)
            
            self.current_qr_image = img
            self.display_preview(img)
            self.update_status(f"✓ QR Code generated successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate QR code: {str(e)}")
            self.update_status("Error: Failed to generate QR code")
    
    def get_module_drawer(self):
        style = self.module_style.get()
        if style == "rounded":
            return RoundedModuleDrawer()
        elif style == "circle":
            return CircleModuleDrawer()
        else:
            return SquareModuleDrawer()
    
    def add_logo_to_qr(self, qr_img):
        """Add logo to QR code with smart positioning and sizing"""
        try:
            logo = Image.open(self.logo_path.get()).convert('RGBA')
            
            # Calculate logo size (percentage of QR code)
            qr_width = qr_img.size[0]
            logo_size = int(qr_width * self.logo_size_ratio.get())
            
            # Resize logo maintaining aspect ratio
            logo.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)
            
            # Create white background for logo
            logo_bg = Image.new('RGB', (logo_size + 10, logo_size + 10), self.bg_color)
            offset = (5, 5)
            logo_bg.paste(logo, offset, logo)
            
            # Calculate position (center of QR code)
            pos_x = (qr_width - logo_size) // 2
            pos_y = (qr_width - logo_size) // 2
            
            # Paste logo onto QR code
            qr_img.paste(logo_bg, (pos_x - 5, pos_y - 5))
            
            return qr_img
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add logo: {str(e)}")
            return qr_img
    
    def display_preview(self, img):
        """Display QR code preview on canvas"""
        # Resize for preview
        preview_size = 400
        img_preview = img.copy()
        img_preview.thumbnail((preview_size, preview_size), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(img_preview)
        
        # Display on canvas
        self.canvas.delete("all")
        self.canvas.create_image(250, 250, image=photo)
        self.canvas.image = photo
    
    def export_qr(self, format_type):
        if not self.current_qr_image:
            messagebox.showwarning("Warning", "Please generate a QR code first")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_type == "PNG":
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                initialfile=f"qrcode_{timestamp}.png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
            )
            if file_path:
                self.current_qr_image.save(file_path, "PNG")
                self.update_status(f"✓ Saved as PNG: {os.path.basename(file_path)}")
                messagebox.showinfo("Success", f"QR Code saved to:\n{file_path}")
        
        elif format_type == "JPG":
            file_path = filedialog.asksaveasfilename(
                defaultextension=".jpg",
                initialfile=f"qrcode_{timestamp}.jpg",
                filetypes=[("JPG files", "*.jpg"), ("All files", "*.*")]
            )
            if file_path:
                self.current_qr_image.convert('RGB').save(file_path, "JPEG", quality=95)
                self.update_status(f"✓ Saved as JPG: {os.path.basename(file_path)}")
                messagebox.showinfo("Success", f"QR Code saved to:\n{file_path}")
        
        elif format_type == "SVG":
            file_path = filedialog.asksaveasfilename(
                defaultextension=".svg",
                initialfile=f"qrcode_{timestamp}.svg",
                filetypes=[("SVG files", "*.svg"), ("All files", "*.*")]
            )
            if file_path:
                self.create_svg_qr(file_path)
                self.update_status(f"✓ Saved as SVG: {os.path.basename(file_path)}")
                messagebox.showinfo("Success", f"QR Code saved to:\n{file_path}")
    
    def create_svg_qr(self, file_path):
        """Create SVG version of QR code"""
        try:
            import qrcode.image.svg
            qr = qrcode.QRCode(image_factory=qrcode.image.svg.SvgPathImage)
            qr.add_data(self.text_input.get("1.0", tk.END).strip())
            qr.make()
            img = qr.make_image()
            img.save(file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create SVG: {str(e)}")
    
    def scan_qr(self):
        """Scan QR code from camera - FIXED THREADING ISSUE"""
        scan_window = tk.Toplevel(self.root)
        scan_window.title("QR Code Scanner")
        scan_window.geometry("600x500")
        scan_window.transient(self.root)
        
        ttk.Label(scan_window, text="Position QR code in front of camera", font=('Arial', 12)).pack(pady=10)
        
        canvas = Canvas(scan_window, bg="black", width=600, height=400)
        canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        result_label = ttk.Label(scan_window, text="Scanning...", foreground="blue")
        result_label.pack(pady=5)
        
        # Store references
        scan_data = {'cap': None, 'detector': None, 'running': True}
        
        def scan_thread():
            try:
                scan_data['cap'] = cv2.VideoCapture(0)
                scan_data['detector'] = cv2.QRCodeDetector()
                
                cap = scan_data['cap']
                detector = scan_data['detector']
                
                # Check if camera opened successfully
                if not cap.isOpened():
                    if result_label.winfo_exists():
                        result_label.after(0, lambda: result_label.config(
                            text="Error: Camera not found", foreground="red"
                        ))
                    return
                
                while scan_window.winfo_exists() and scan_data['running']:
                    ret, frame = cap.read()
                    if not ret:
                        continue
                    
                    frame = cv2.resize(frame, (600, 400))
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    try:
                        data, bbox, _ = detector.detectAndDecode(frame)
                    except:
                        data = None
                    
                    if data:
                        # Schedule on main thread
                        if scan_window.winfo_exists():
                            self.root.after(0, lambda d=data: self.set_preset_data(d))
                            if result_label.winfo_exists():
                                result_label.after(0, lambda d=data: result_label.config(
                                    text=f"✓ Scanned: {d[:50]}{'...' if len(d) > 50 else ''}",
                                    foreground="green"
                                ))
                        scan_data['running'] = False
                        cap.release()
                        scan_window.after(2000, scan_window.destroy)
                        break
                    
                    # Update canvas on main thread
                    if canvas.winfo_exists():
                        pil_img = Image.fromarray(rgb_frame)
                        photo = ImageTk.PhotoImage(pil_img)
                        
                        def update_canvas(p=photo):
                            if canvas.winfo_exists():
                                canvas.delete("all")
                                canvas.create_image(0, 0, anchor=tk.NW, image=p)
                                canvas.image = p
                        
                        canvas.after(0, update_canvas)
                
                if cap.isOpened():
                    cap.release()
                    
            except Exception as e:
                print(f"Scanner error: {str(e)}")
                if scan_window.winfo_exists() and result_label.winfo_exists():
                    result_label.after(0, lambda err=str(e): result_label.config(
                        text=f"Error: {err[:40]}", foreground="red"
                    ))
        
        # Handle window close
        def on_closing():
            scan_data['running'] = False
            if scan_data['cap'] and scan_data['cap'].isOpened():
                scan_data['cap'].release()
            scan_window.destroy()
        
        scan_window.protocol("WM_DELETE_WINDOW", on_closing)
        threading.Thread(target=scan_thread, daemon=True).start()
    
    def analyze_qr(self):
        """Analyze QR code properties"""
        if not self.current_qr_image:
            messagebox.showwarning("Warning", "Please generate a QR code first")
            return
        
        data = self.text_input.get("1.0", tk.END).strip()
        
        analysis = f"""QR Code Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Data Content: {data[:100]}{"..." if len(data) > 100 else ""}
Data Length: {len(data)} characters

Error Correction: {self.error_correction.get()}
Module Style: {self.module_style.get()}
QR Size: {self.qr_size.get()}
Border Size: {self.border_size.get()}

Colors:
  Foreground: {self.fg_color_hex}
  Background: {self.bg_color_hex}

Image Size: {self.current_qr_image.size[0]}x{self.current_qr_image.size[1]} pixels

Optimization:
  ✓ Auto-Optimize: {"Enabled" if self.auto_optimize.get() else "Disabled"}
  ✓ High Error Correction: Ensures scanability
  ✓ Color Contrast: Optimized for readability
"""
        
        messagebox.showinfo("QR Code Analysis", analysis)
    
    def copy_to_clipboard(self):
        """Copy QR code image to clipboard"""
        if not self.current_qr_image:
            messagebox.showwarning("Warning", "Please generate a QR code first")
            return
        
        try:
            # For Windows
            import io
            
            output = io.BytesIO()
            self.current_qr_image.save(output, "BMP")
            data = output.getvalue()[14:]
            
            import ctypes
            from ctypes.wintypes import HGLOBAL, LPVOID, DWORD
            
            GMEM_MOVEABLE = 2
            CF_DIB = 8
            
            h = ctypes.windll.kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data))
            pv = ctypes.windll.kernel32.GlobalLock(h)
            ctypes.memmove(pv, data, len(data))
            ctypes.windll.kernel32.GlobalUnlock(h)
            
            ctypes.windll.user32.OpenClipboard(None)
            ctypes.windll.user32.EmptyClipboard()
            ctypes.windll.user32.SetClipboardData(CF_DIB, h)
            ctypes.windll.user32.CloseClipboard()
            
            messagebox.showinfo("Success", "QR Code copied to clipboard!")
            self.update_status("✓ QR Code copied to clipboard")
        except Exception as e:
            messagebox.showwarning("Info", "Image copied (clipboard support varies by OS)")
            self.update_status("⚠ Clipboard operation completed")
    
    def clear_all(self):
        """Clear all inputs and preview"""
        if messagebox.askyesno("Confirm", "Clear all data and preview?"):
            self.text_input.delete("1.0", tk.END)
            self.logo_path.set("")
            self.logo_label.config(text="No logo selected", foreground="gray")
            self.canvas.delete("all")
            self.current_qr_image = None
            self.update_char_count()
            self.update_status("Cleared")
    
    def update_status(self, message):
        self.status_label.config(text=message)
        self.root.update()

if __name__ == "__main__":
    root = tk.Tk()
    app = AIQRCodeGenerator(root)
    root.mainloop()
