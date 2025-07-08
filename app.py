from flask import Flask, render_template, request, send_file, jsonify
from rembg import remove
from PIL import Image
import os
import io
import zipfile
import random
import json
from datetime import datetime
from werkzeug.utils import secure_filename
import shutil

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
BACKGROUND_FOLDER = 'backgrounds'
RESULTS_FOLDER = 'results'
CONTENT_INDEX_FILE = 'content_index.json'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

# Create necessary directories
for folder in [UPLOAD_FOLDER, BACKGROUND_FOLDER, RESULTS_FOLDER]:
    os.makedirs(folder, exist_ok=True)

def load_content_index():
    """Load content index from file"""
    if os.path.exists(CONTENT_INDEX_FILE):
        try:
            with open(CONTENT_INDEX_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_content_index(index):
    """Save content index to file"""
    with open(CONTENT_INDEX_FILE, 'w') as f:
        json.dump(index, f, indent=2)

def generate_unique_content_id():
    """Generate a unique 6-digit content ID"""
    content_index = load_content_index()
    
    # Generate random 6-digit number
    while True:
        content_id = str(random.randint(100000, 999999))
        if content_id not in content_index:
            return content_id

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def remove_background(image_path):
    """Remove background from image using rembg"""
    with open(image_path, 'rb') as f:
        input_data = f.read()
    
    output_data = remove(input_data)
    
    # Convert to PIL Image
    subject_img = Image.open(io.BytesIO(output_data)).convert("RGBA")
    return subject_img

def get_background_images():
    """Get all background images from backgrounds folder with metadata"""
    backgrounds = []
    if os.path.exists(BACKGROUND_FOLDER):
        for filename in sorted(os.listdir(BACKGROUND_FOLDER)):
            if allowed_file(filename):
                file_path = os.path.join(BACKGROUND_FOLDER, filename)
                
                # Get file size
                file_size = os.path.getsize(file_path)
                
                # Get image dimensions
                try:
                    with Image.open(file_path) as img:
                        width, height = img.size
                except:
                    width, height = 0, 0
                
                backgrounds.append({
                    'filename': filename,
                    'path': file_path,
                    'size': file_size,
                    'dimensions': f"{width}x{height}",
                    'name': os.path.splitext(filename)[0]
                })
    return backgrounds

def get_specific_background(background_index):
    """Get a specific background image by index (1-based)"""
    background_list = get_background_images()
    
    if not background_list:
        raise Exception("No background images found in 'backgrounds' folder")
    
    # Convert to 0-based index
    index = background_index - 1
    
    if index < 0 or index >= len(background_list):
        raise Exception(f"Background index {background_index} is out of range. Available backgrounds: 1-{len(background_list)}")
    
    return background_list[index]['path']

def fit_subject_to_background(subject_img, background_size):
    """Fit subject image to background size while maintaining aspect ratio"""
    subject_ratio = subject_img.width / subject_img.height
    background_ratio = background_size[0] / background_size[1]
    
    if subject_ratio > background_ratio:
        # Subject is wider relative to background, fit by width
        new_width = background_size[0]
        new_height = int(new_width / subject_ratio)
    else:
        # Subject is taller relative to background, fit by height
        new_height = background_size[1]
        new_width = int(new_height * subject_ratio)
    
    return subject_img.resize((new_width, new_height), Image.Resampling.LANCZOS)

def process_with_backgrounds(subject_img, content_id):
    """Process subject with all background images"""
    background_list = get_background_images()
    result_files = []
    
    if not background_list:
        raise Exception("No background images found in 'backgrounds' folder")
    
    for i, bg_data in enumerate(background_list, 1):
        try:
            # Load background
            background = Image.open(bg_data['path']).convert("RGBA")
            
            # Fit subject to background while maintaining aspect ratio
            subject_fitted = fit_subject_to_background(subject_img, background.size)
            
            # Create a new image with background size
            result = Image.new("RGBA", background.size, (0, 0, 0, 0))
            
            # Paste background
            result.paste(background, (0, 0))
            
            # Calculate position to center the subject
            x = (background.size[0] - subject_fitted.size[0]) // 2
            y = (background.size[1] - subject_fitted.size[1]) // 2
            
            # Paste subject on top
            result.paste(subject_fitted, (x, y), subject_fitted)
            
            # Generate filename with content ID
            result_filename = f"{content_id}_bg{i:02d}_{bg_data['name']}.jpg"
            result_path = os.path.join(RESULTS_FOLDER, result_filename)
            
            # Save result
            result.convert("RGB").save(result_path, quality=95)
            result_files.append(result_filename)
            
            print(f"✅ Created: {result_filename}")
            
        except Exception as e:
            print(f"❌ Error processing background {bg_data['path']}: {str(e)}")
            continue
    
    return result_files

def process_with_specific_background(subject_img, content_id, background_index):
    """Process subject with a specific background image"""
    try:
        # Get the specific background
        bg_path = get_specific_background(background_index)
        
        # Load background
        background = Image.open(bg_path).convert("RGBA")
        
        # Fit subject to background while maintaining aspect ratio
        subject_fitted = fit_subject_to_background(subject_img, background.size)
        
        # Create a new image with background size
        result = Image.new("RGBA", background.size, (0, 0, 0, 0))
        
        # Paste background
        result.paste(background, (0, 0))
        
        # Calculate position to center the subject
        x = (background.size[0] - subject_fitted.size[0]) // 2
        y = (background.size[1] - subject_fitted.size[1]) // 2
        
        # Paste subject on top
        result.paste(subject_fitted, (x, y), subject_fitted)
        
        # Generate filename with content ID
        bg_filename = os.path.basename(bg_path)
        bg_name = os.path.splitext(bg_filename)[0]
        result_filename = f"{content_id}_bg{background_index:02d}_{bg_name}.jpg"
        result_path = os.path.join(RESULTS_FOLDER, result_filename)
        
        # Save result
        result.convert("RGB").save(result_path, quality=95)
        
        print(f"✅ Created: {result_filename}")
        
        return [result_filename]
        
    except Exception as e:
        print(f"❌ Error processing background {background_index}: {str(e)}")
        raise

@app.route('/')
def index():
    background_list = get_background_images()
    return render_template('index.html', background_count=len(background_list))

@app.route('/find')
def find_picture():
    """Route for find picture page"""
    return render_template('find.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file selected'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Use PNG, JPG, JPEG, GIF, or BMP'}), 400
        
        # Get background parameter (optional)
        background_param = request.form.get('background')
        
        # Generate unique content ID
        content_id = generate_unique_content_id()
        
        # Save uploaded file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Remove background
        subject_img = remove_background(filepath)
        
        # Process based on background parameter
        if background_param and background_param != 'all':
            try:
                background_index = int(background_param)
                result_files = process_with_specific_background(subject_img, content_id, background_index)
                message = f'Successfully generated image with background {background_index}'
                
                # For single background, return direct download link
                main_file = result_files[0]
                content_url = f"http://localhost:5000/download/{main_file}"
                
            except ValueError:
                return jsonify({'error': 'Background parameter must be a number'}), 400
        else:
            # Process with all backgrounds (when 'all' is selected or no background specified)
            result_files = process_with_backgrounds(subject_img, content_id)
            message = f'Successfully generated {len(result_files)} images with all backgrounds'
            
            # For multiple backgrounds, provide ZIP download link
            content_url = f"http://localhost:5000/download_all/{content_id}"
        
        # Save content information to index
        content_index = load_content_index()
        content_index[content_id] = {
            'files': result_files,
            'created_at': datetime.now().isoformat(),
            'original_filename': file.filename,
            'file_count': len(result_files)
        }
        save_content_index(content_index)
        
        # Clean up uploaded file
        os.remove(filepath)
        
        if not result_files:
            return jsonify({'error': 'No results generated'}), 500
        
        return jsonify({
            'content_id': content_id,
            'content_url': content_url,
            'message': message,
            'status': 200,
            'file_count': len(result_files),
            'files': result_files,
            'individual_urls': [f"http://localhost:5000/download/{filename}" for filename in result_files]
        })
        
    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.route('/upload_background', methods=['POST'])
def upload_background():
    """Upload a new background image"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file selected'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Use PNG, JPG, JPEG, GIF, or BMP'}), 400
        
        # Secure the filename
        filename = secure_filename(file.filename)
        
        # Add timestamp to avoid conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_filename = f"{timestamp}_{filename}"
        
        # Save to backgrounds folder
        filepath = os.path.join(BACKGROUND_FOLDER, final_filename)
        file.save(filepath)
        
        # Get image info
        try:
            with Image.open(filepath) as img:
                width, height = img.size
                dimensions = f"{width}x{height}"
        except:
            dimensions = "Unknown"
        
        return jsonify({
            'success': True,
            'message': f'Background "{filename}" uploaded successfully',
            'filename': final_filename,
            'dimensions': dimensions
        })
        
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/delete_background/<filename>', methods=['DELETE'])
def delete_background(filename):
    """Delete a background image"""
    try:
        # Secure the filename
        filename = secure_filename(filename)
        filepath = os.path.join(BACKGROUND_FOLDER, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'Background not found'}), 404
        
        # Delete the file
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'message': f'Background "{filename}" deleted successfully'
        })
        
    except Exception as e:
        return jsonify({'error': f'Delete failed: {str(e)}'}), 500

@app.route('/get_picture/<content_id>')
def get_picture(content_id):
    """Get picture information by content ID"""
    try:
        content_index = load_content_index()
        
        if content_id not in content_index:
            return jsonify({'error': 'Content ID not found'}), 404
        
        content_info = content_index[content_id]
        
        # Check if files still exist
        existing_files = []
        for filename in content_info['files']:
            if os.path.exists(os.path.join(RESULTS_FOLDER, filename)):
                existing_files.append(filename)
        
        if not existing_files:
            return jsonify({'error': 'Files no longer exist'}), 404
        
        # Determine download URL
        if len(existing_files) == 1:
            download_url = f"http://localhost:5000/download/{existing_files[0]}"
        else:
            download_url = f"http://localhost:5000/download_all/{content_id}"
        
        return jsonify({
            'content_id': content_id,
            'download_url': download_url,
            'file_count': len(existing_files),
            'files': existing_files,
            'created_at': content_info['created_at'],
            'original_filename': content_info['original_filename'],
            'individual_urls': [f"http://localhost:5000/download/{filename}" for filename in existing_files]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/list_backgrounds', methods=['GET'])
def list_backgrounds():
    """List all available background images with detailed information"""
    try:
        background_list = get_background_images()
        backgrounds = []
        
        for i, bg_data in enumerate(background_list, 1):
            backgrounds.append({
                'index': i,
                'filename': bg_data['filename'],
                'name': bg_data['name'],
                'size': bg_data['size'],
                'dimensions': bg_data['dimensions'],
                'preview_url': f"http://localhost:5000/background_preview/{bg_data['filename']}"
            })
        
        return jsonify({
            'backgrounds': backgrounds,
            'count': len(backgrounds)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/background_preview/<filename>')
def background_preview(filename):
    """Serve background image for preview"""
    try:
        filename = secure_filename(filename)
        return send_file(
            os.path.join(BACKGROUND_FOLDER, filename),
            as_attachment=False
        )
    except Exception as e:
        return jsonify({'error': f'Preview not found: {str(e)}'}), 404

@app.route('/download/<filename>')
def download_file(filename):
    try:
        return send_file(
            os.path.join(RESULTS_FOLDER, filename),
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': f'File not found: {str(e)}'}), 404

@app.route('/download_all/<content_id>')
def download_all(content_id):
    try:
        # Get content info
        content_index = load_content_index()
        if content_id not in content_index:
            return jsonify({'error': 'Content ID not found'}), 404
        
        content_info = content_index[content_id]
        
        # Create ZIP file
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for filename in content_info['files']:
                file_path = os.path.join(RESULTS_FOLDER, filename)
                if os.path.exists(file_path):
                    zip_file.write(file_path, filename)
        
        zip_buffer.seek(0)
        
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'{content_id}_all_backgrounds.zip'
        )
        
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

@app.route('/results')
def list_results():
    try:
        files = [f for f in os.listdir(RESULTS_FOLDER) if allowed_file(f)]
        return jsonify({'files': sorted(files, reverse=True)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/clear_results', methods=['POST'])
def clear_results():
    try:
        for filename in os.listdir(RESULTS_FOLDER):
            os.remove(os.path.join(RESULTS_FOLDER, filename))
        
        # Clear content index
        save_content_index({})
        
        return jsonify({'success': True, 'message': 'All results cleared'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/clear_backgrounds', methods=['POST'])
def clear_backgrounds():
    """Clear all background images"""
    try:
        for filename in os.listdir(BACKGROUND_FOLDER):
            if allowed_file(filename):
                os.remove(os.path.join(BACKGROUND_FOLDER, filename))
        
        return jsonify({'success': True, 'message': 'All backgrounds cleared'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Enhanced Background Replacement App...")
    print(f"📁 Add your background images to the '{BACKGROUND_FOLDER}' folder")
    print("📤 Upload new backgrounds through the web interface")
    print("🌐 App will be available at: http://localhost:5000")
    print("🔍 Find pictures at: http://localhost:5000/find")
    app.run(debug=True, host='0.0.0.0', port=5000)