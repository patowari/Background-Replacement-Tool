# Background Replacement Tool

A Flask web application that automatically removes backgrounds from uploaded images and replaces them with your custom background collection.

## 🚀 Quick Start
![6ffc5183-090a-46b0-a82a-89d4d78ada62](https://github.com/user-attachments/assets/5176c96e-bb4e-4afb-aa63-eeccc1cc137b)

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


# 🚀 Complete Postman API Guide - Background Replacement Tool

## 📋 Base Configuration

**Base URL:** `http://localhost:5000`

**Prerequisites:**
1. Flask app running on localhost:5000
2. Postman installed
3. Sample images ready for testing

---

## 🎯 API Endpoints Overview

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/list_backgrounds` | List all available backgrounds |
| POST | `/upload_background` | Upload new background image |
| DELETE | `/delete_background/<filename>` | Delete specific background |
| POST | `/upload` | Process image with backgrounds |
| GET | `/get_picture/<content_id>` | Retrieve processed images |
| GET | `/download/<filename>` | Download specific file |
| GET | `/download_all/<content_id>` | Download all files as ZIP |
| GET | `/results` | List all result files |
| POST | `/clear_results` | Clear all results |
| POST | `/clear_backgrounds` | Clear all backgrounds |

---

## 🔧 Detailed API Testing

### 1. 📁 List Available Backgrounds

**GET** `/list_backgrounds`

```http
GET http://localhost:5000/list_backgrounds
```

**Response Example:**
```json
{
  "backgrounds": [
    {
      "index": 1,
      "filename": "20241208_143022_sunset.jpg",
      "name": "sunset",
      "size": 245760,
      "dimensions": "1920x1080",
      "preview_url": "http://localhost:5000/background_preview/20241208_143022_sunset.jpg"
    },
    {
      "index": 2,
      "filename": "20241208_143045_office.jpg",
      "name": "office",
      "size": 189440,
      "dimensions": "1280x720",
      "preview_url": "http://localhost:5000/background_preview/20241208_143045_office.jpg"
    }
  ],
  "count": 2
}
```

---

### 2. 📤 Upload Background Image

**POST** `/upload_background`

**Headers:**
- Content-Type: `multipart/form-data`

**Body (form-data):**
- Key: `file`
- Type: File
- Value: Select your background image file

```http
POST http://localhost:5000/upload_background
Content-Type: multipart/form-data

file: [SELECT_IMAGE_FILE]
```

**Response Example:**
```json
{
  "success": true,
  "message": "Background \"beach.jpg\" uploaded successfully",
  "filename": "20241208_143156_beach.jpg",
  "dimensions": "1920x1080"
}
```

---

### 3. 🗑️ Delete Background

**DELETE** `/delete_background/<filename>`

```http
DELETE http://localhost:5000/delete_background/20241208_143156_beach.jpg
```

**Response Example:**
```json
{
  "success": true,
  "message": "Background \"20241208_143156_beach.jpg\" deleted successfully"
}
```

---

### 4. 🎨 Process Image (Main Function)

**POST** `/upload`

**Headers:**
- Content-Type: `multipart/form-data`

**Body (form-data):**
- Key: `file` (File) - Your subject image
- Key: `background` (Text) - Background selection

**Options for `background` parameter:**
- `all` - Process with all backgrounds
- `1`, `2`, `3`, etc. - Process with specific background index

#### Example 1: Process with All Backgrounds
```http
POST http://localhost:5000/upload
Content-Type: multipart/form-data

file: [SELECT_SUBJECT_IMAGE]
background: all
```

#### Example 2: Process with Specific Background
```http
POST http://localhost:5000/upload
Content-Type: multipart/form-data

file: [SELECT_SUBJECT_IMAGE]
background: 2
```

**Response Example (Multiple Backgrounds):**
```json
{
  "content_id": "234567",
  "content_url": "http://localhost:5000/download_all/234567",
  "message": "Successfully generated 3 images with all backgrounds",
  "status": 200,
  "file_count": 3,
  "files": [
    "234567_bg01_sunset.jpg",
    "234567_bg02_office.jpg",
    "234567_bg03_beach.jpg"
  ],
  "individual_urls": [
    "http://localhost:5000/download/234567_bg01_sunset.jpg",
    "http://localhost:5000/download/234567_bg02_office.jpg",
    "http://localhost:5000/download/234567_bg03_beach.jpg"
  ]
}
```

**Response Example (Single Background):**
```json
{
  "content_id": "345678",
  "content_url": "http://localhost:5000/download/345678_bg02_office.jpg",
  "message": "Successfully generated image with background 2",
  "status": 200,
  "file_count": 1,
  "files": ["345678_bg02_office.jpg"],
  "individual_urls": ["http://localhost:5000/download/345678_bg02_office.jpg"]
}
```

---

### 5. 🔍 Retrieve Processed Images

**GET** `/get_picture/<content_id>`

```http
GET http://localhost:5000/get_picture/234567
```

**Response Example:**
```json
{
  "content_id": "234567",
  "download_url": "http://localhost:5000/download_all/234567",
  "file_count": 3,
  "files": [
    "234567_bg01_sunset.jpg",
    "234567_bg02_office.jpg",
    "234567_bg03_beach.jpg"
  ],
  "created_at": "2024-12-08T14:35:22.123456",
  "original_filename": "person.jpg",
  "individual_urls": [
    "http://localhost:5000/download/234567_bg01_sunset.jpg",
    "http://localhost:5000/download/234567_bg02_office.jpg",
    "http://localhost:5000/download/234567_bg03_beach.jpg"
  ]
}
```

---

### 6. 📥 Download Individual File

**GET** `/download/<filename>`

```http
GET http://localhost:5000/download/234567_bg01_sunset.jpg
```

**Response:** Binary file download (JPEG image)

---

### 7. 📦 Download All Files as ZIP

**GET** `/download_all/<content_id>`

```http
GET http://localhost:5000/download_all/234567
```

**Response:** Binary file download (ZIP archive)

---

### 8. 📋 List All Results

**GET** `/results`

```http
GET http://localhost:5000/results
```

**Response Example:**
```json
{
  "files": [
    "234567_bg01_sunset.jpg",
    "234567_bg02_office.jpg",
    "234567_bg03_beach.jpg",
    "345678_bg02_office.jpg"
  ]
}
```

---

### 9. 🧹 Clear All Results

**POST** `/clear_results`

```http
POST http://localhost:5000/clear_results
```

**Response Example:**
```json
{
  "success": true,
  "message": "All results cleared"
}
```

---

### 10. 🗑️ Clear All Backgrounds

**POST** `/clear_backgrounds`

```http
POST http://localhost:5000/clear_backgrounds
```

**Response Example:**
```json
{
  "success": true,
  "message": "All backgrounds cleared"
}
```

---

## 🎯 Complete Workflow Example

### Step 1: Setup Backgrounds
1. **Upload Background 1:**
   ```http
   POST /upload_background
   file: sunset.jpg
   ```

2. **Upload Background 2:**
   ```http
   POST /upload_background
   file: office.jpg
   ```

3. **Verify Backgrounds:**
   ```http
   GET /list_backgrounds
   ```

### Step 2: Process Image
```http
POST /upload
file: person.jpg
background: all
```

**Save the `content_id` from response (e.g., "234567")**

### Step 3: Retrieve Results
```http
GET /get_picture/234567
```

### Step 4: Download Files
```http
GET /download_all/234567
```

---

## 🛠️ Postman Collection Setup

### Create Collection
1. Open Postman
2. Create new Collection: "Background Replacement API"
3. Add environment variable: `baseURL` = `http://localhost:5000`

### Environment Variables
```json
{
  "baseURL": "http://localhost:5000",
  "content_id": "{{content_id}}"
}
```

### Pre-request Script (for upload endpoints)
```javascript
// Auto-generate content ID variable from response
pm.test("Save content_id", function () {
    var jsonData = pm.response.json();
    if (jsonData.content_id) {
        pm.environment.set("content_id", jsonData.content_id);
    }
});
```

---

## 🚨 Error Handling

### Common Error Responses

**400 Bad Request:**
```json
{
  "error": "No file selected"
}
```

**404 Not Found:**
```json
{
  "error": "Content ID not found"
}
```

**500 Internal Server Error:**
```json
{
  "error": "Processing failed: [error details]"
}
```

---

## 🧪 Testing Scenarios

### 1. Happy Path Testing
1. Upload backgrounds
2. Process image with all backgrounds
3. Retrieve results
4. Download files

### 2. Edge Case Testing
1. Upload invalid file format
2. Search for non-existent content ID
3. Process image with no backgrounds
4. Delete non-existent background

### 3. Error Testing
1. Upload without file
2. Invalid background parameter
3. Malformed content ID
4. Network interruption during upload

---

## 📊 Response Time Expectations

| Endpoint | Expected Time |
|----------|---------------|
| `/list_backgrounds` | < 100ms |
| `/upload_background` | 1-3 seconds |
| `/upload` (single bg) | 10-30 seconds |
| `/upload` (all bgs) | 30-120 seconds |
| `/get_picture` | < 100ms |
| `/download` | 1-5 seconds |

---

## 🔍 Debugging Tips

1. **Check Flask app logs** for detailed error messages
2. **Verify file permissions** in upload/background folders
3. **Monitor disk space** for large image processing
4. **Use Postman Console** to view request/response details
5. **Test with small images first** to ensure pipeline works

---

## 📝 Notes

- All image uploads should be in supported formats: PNG, JPG, JPEG, GIF, BMP
- Content IDs are 6-digit numbers (100000-999999)
- Files are stored temporarily and may be cleaned up periodically
- Large images may take longer to process
- ZIP downloads include all images for a content ID
