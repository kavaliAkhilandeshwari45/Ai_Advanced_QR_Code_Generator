# 🤖 AI-Powered QR Code Generator Pro

A feature-rich desktop QR Code Generator built with **Python and Tkinter**. The application allows users to create highly customizable QR codes, add logos, scan QR codes using a webcam, analyze QR properties, and export generated QR codes in multiple formats.

## ✨ Features

* 🔗 Generate QR codes from custom text or data
* 🌐 URL QR Code preset
* 📧 Email QR Code preset
* 📞 Phone QR Code preset
* 👤 vCard QR Code generation
* 📶 WiFi QR Code generation
* 🎨 Customize QR module styles:

  * Square
  * Rounded
  * Circle
* 🖌️ Customize foreground and background colors
* 🛡️ Select error correction levels:

  * L – 7%
  * M – 15%
  * Q – 25%
  * H – 30%
* 📏 Adjustable QR size
* 🖼️ Adjustable border size
* 🏷️ Add a custom logo to the QR code
* 🔍 QR Code preview
* 📷 Scan QR codes using a webcam
* 📊 Analyze generated QR code properties
* 📋 Copy QR code image to clipboard
* 🧹 Clear input and preview
* 💾 Export QR codes as:

  * PNG
  * JPG
  * SVG

## 🛠️ Technologies Used

* **Python**
* **Tkinter** – Desktop GUI
* **Pillow (PIL)** – Image processing and logo handling
* **QRCode** – QR code generation
* **OpenCV** – Camera access and QR code scanning
* **NumPy** – Image/data processing
* **Threading** – Background QR scanning

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/AI-QRCode-Generator.git
cd AI-QRCode-Generator
```

### 2. Install Required Libraries

```bash
pip install pillow qrcode opencv-python numpy
```

### 3. Run the Application

```bash
python "Pasted code.py"
```

## 🖥️ Application Workflow

```text
                ┌─────────────────────┐
                │     Start App       │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │    Enter QR Data    │
                └──────────┬──────────┘
                           │
                           ▼
             ┌───────────────────────────┐
             │ Customize QR Code Design │
             │ Colors / Style / Size    │
             └─────────────┬─────────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │   Generate QR Code  │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │   Preview QR Code   │
                └──────────┬──────────┘
                           │
              ┌────────────┼─────────────┐
              ▼            ▼             ▼
           Analyze       Copy          Export
                                       PNG/JPG/SVG
```

## 📋 QR Code Presets

The application provides predefined formats for commonly used QR codes.

### URL

Creates a QR code containing a website URL.

### Email

Creates a `mailto:` QR code for email communication.

### Phone

Creates a `tel:` QR code containing a phone number.

### vCard

Allows users to enter:

* Name
* Organization
* Phone
* Email
* Website

and generates a contact QR code.

### WiFi

Allows users to enter:

* SSID
* Password
* Security type

and generates a WiFi connection QR code.

## 🎨 Customization

Users can customize the QR code using different module shapes and colors.

Supported module styles:

```text
Square
Rounded
Circle
```

Foreground and background colors can be selected using the built-in color picker.

## 🖼️ Logo Support

Users can select an image file and place it at the center of the QR code.

Supported image formats include:

```text
PNG
JPG
JPEG
GIF
BMP
```

The logo size can be adjusted between **10% and 50%** of the QR code size.

## 📷 QR Code Scanner

The application includes a webcam-based QR scanner using **OpenCV's QRCodeDetector**.

The scanner:

1. Opens the webcam.
2. Displays the live camera feed.
3. Detects QR codes.
4. Decodes the QR data.
5. Places the scanned data into the application.

## 📊 QR Code Analysis

The Analyze feature displays information such as:

* Data content
* Data length
* Error correction level
* Module style
* QR size
* Border size
* Foreground color
* Background color
* Image dimensions
* Optimization information

## 💾 Export Options

Generated QR codes can be saved in:

| Format | Description               |
| ------ | ------------------------- |
| PNG    | High-quality raster image |
| JPG    | Compressed image format   |
| SVG    | Scalable vector format    |

## 📁 Project Structure

```text
AI-QRCode-Generator/
│
├── Pasted code.py
├── README.md
└── requirements.txt
```

## 📄 requirements.txt

```text
Pillow
qrcode
opencv-python
numpy
```

## 🚀 Future Enhancements

* Add dark/light application themes
* Add QR code history
* Support batch QR generation
* Add more QR templates
* Add gradient QR colors
* Add drag-and-drop logo support
* Add QR code decoding from image files
* Add password-protected QR codes
* Add mobile/web version
* Improve automatic QR optimization
* Add downloadable project reports

## 🎯 Use Cases

This application can be used for:

* Personal websites
* Contact information
* WiFi sharing
* Business cards
* Product information
* Event registration
* Social media links
* Digital menus
* Payment-related information
* Educational projects

## 👩‍💻 Author

**Kavali Akhilandeshwari**

B.Tech – Artificial Intelligence & Machine Learning

---

⭐ If you find this project useful, consider giving it a star on GitHub!
