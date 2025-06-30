# Background Replacement Tool

A Flask web application that automatically removes backgrounds from uploaded images and replaces them with your custom background collection.

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Create project directory
mkdir background-replacer
cd background-replacer

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Project Structure

Create the following directory structure:

```
background-replacer/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Web interface
├── backgrounds/          # Put your 4 background images here
├── uploads/             # Temporary upload folder (auto-created)
├── results/             # Generated images folder (auto-created)
└── README.md
```

### 3. Add Background Images

1. Create a `backgrounds` folder in your project directory
2. Add your 4 background images to this folder
3. Supported formats: PNG, JPG, JPEG, GIF, BMP
4. Name them clearly (e.g., `background1.jpg`, `nature.png`, etc.)

### 4. Create Templates Folder

```bash
mkdir templates
```

Save the HTML template as `templates/index.html`

### 5. Run the Application

```bash
python app.py
```

The app will start at: **http://localhost:5000**

## 📋 Features

- **Automatic Background Removal**: Uses AI to detect and remove backgrounds
- **Batch Processing**: Automatically processes your image with all background images
- **Sequential Processing**: Goes through background1, background2, background3, background4 in order
- **Web Interface**: Clean, modern UI with drag-and-drop upload
- **Download Options**: Download individual images or all at once as a ZIP file
- **Real-time Status**: Shows processing progress and system status

## 🎯 How It Works

1. **Upload**: Drag & drop or click to upload your main image
2. **AI Processing**: Background is automatically removed using rembg
3. **Background Replacement**: Your image is combined with each background in sequence
4. **Download**: Get individual files or download all as a ZIP

## 📁 File Organization

- **Input**: Your uploaded image (temporarily stored in `uploads/`)
- **Backgrounds**: Your collection of 4 background images in `backgrounds/`
- **Output**: Generated images saved in `results/` with naming format:
  - `timestamp_processed_bg01_backgroundname.jpg`
  - `timestamp_processed_bg02_backgroundname.jpg`
  - etc.

## 🔧 Advanced Configuration

### Custom Port
```bash
# Run on different port
export FLASK_RUN_PORT=8080
python app.py
```

### Background Quality
Edit `app.py` line with `quality=95` to adjust JPEG quality (1-100)

### Supported Image Formats
Currently supports: PNG, JPG, JPEG, GIF, BMP

## 🐛 Troubleshooting

### "No background images found"
- Make sure the `backgrounds` folder exists
- Add at least one image file to the `backgrounds` folder
- Check that image files have supported extensions

### "Processing failed"
- Ensure the uploaded image is a valid image file
- Check that you have enough disk space
- Verify all dependencies are installed correctly

### Slow Processing
- Large images take longer to process
- Consider resizing your background images to reasonable dimensions (e.g., 1920x1080)

## 🎨 Customization

### Adding More Backgrounds
Simply add more images to the `backgrounds` folder - the app will automatically process with all available backgrounds.

### UI Customization
Edit the CSS in `templates/index.html` to change colors, layout, or styling.

### Processing Options
Modify the `process_with_backgrounds()` function in `app.py` to:
- Change output format (PNG/JPG)
- Adjust image quality
- Add image effects or filters

## 📝 Notes

- The app creates necessary folders automatically
- Uploaded files are deleted after processing to save space
- Generated images remain in `results/` until manually cleared
- The app runs in debug mode by default (disable for production)

## 🚀 Production Deployment

For production use:
1. Set `debug=False` in `app.py`
2. Use a production WSGI server like Gunicorn
3. Configure proper file permissions
4. Set up reverse proxy with Nginx if needed

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Enjoy creating amazing composite images! 🎉
