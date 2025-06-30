from flask import Flask, render_template, request, send_file, jsonify
from rembg import remove
from PIL import Image
import os
import io
import zipfile
from datetime import datetime

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
BACKGROUND_FOLDER = 'backgrounds'
RESULTS_FOLDER = 'results'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

# Create necessary directories
for folder in [UPLOAD_FOLDER, BACKGROUND_FOLDER, RESULTS_FOLDER]:
    os.makedirs(folder, exist_ok=True)

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
    """Get all background images from backgrounds folder"""
    backgrounds = []
    if os.path.exists(BACKGROUND_FOLDER):
        for filename in sorted(os.listdir(BACKGROUND_FOLDER)):
            if allowed_file(filename):
                backgrounds.append(os.path.join(BACKGROUND_FOLDER, filename))
    return backgrounds

def process_with_backgrounds(subject_img, output_prefix):
    """Process subject with all background images"""
    background_paths = get_background_images()
    result_files = []
    
    if not background_paths:
        raise Exception("No background images found in 'backgrounds' folder")
    
    for i, bg_path in enumerate(background_paths, 1):
        try:
            # Load background
            background = Image.open(bg_path).convert("RGBA")
            
            # Resize background to match subject
            background = background.resize(subject_img.size, Image.Resampling.LANCZOS)
            
            # Combine images
            result = Image.alpha_composite(background, subject_img)
            
            # Generate filename
            bg_filename = os.path.basename(bg_path)
            bg_name = os.path.splitext(bg_filename)[0]
            result_filename = f"{output_prefix}_bg{i:02d}_{bg_name}.jpg"
            result_path = os.path.join(RESULTS_FOLDER, result_filename)
            
            # Save result
            result.convert("RGB").save(result_path, quality=95)
            result_files.append(result_filename)
            
            print(f"✅ Created: {result_filename}")
            
        except Exception as e:
            print(f"❌ Error processing background {bg_path}: {str(e)}")
            continue
    
    return result_files

@app.route('/')
def index():
    background_count = len(get_background_images())
    return render_template('index.html', background_count=background_count)

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
        
        # Save uploaded file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Remove background
        subject_img = remove_background(filepath)
        
        # Process with all backgrounds
        output_prefix = f"{timestamp}_processed"
        result_files = process_with_backgrounds(subject_img, output_prefix)
        
        # Clean up uploaded file
        os.remove(filepath)
        
        if not result_files:
            return jsonify({'error': 'No results generated'}), 500
        
        return jsonify({
            'success': True,
            'message': f'Successfully generated {len(result_files)} images',
            'files': result_files,
            'download_url': f'/download_all/{output_prefix}'
        })
        
    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

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

@app.route('/download_all/<prefix>')
def download_all(prefix):
    try:
        # Create ZIP file
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for filename in os.listdir(RESULTS_FOLDER):
                if filename.startswith(prefix):
                    file_path = os.path.join(RESULTS_FOLDER, filename)
                    zip_file.write(file_path, filename)
        
        zip_buffer.seek(0)
        
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'{prefix}_all_backgrounds.zip'
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
        return jsonify({'success': True, 'message': 'All results cleared'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Background Replacement App...")
    print(f"📁 Make sure to add your background images to the '{BACKGROUND_FOLDER}' folder")
    print("🌐 App will be available at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
