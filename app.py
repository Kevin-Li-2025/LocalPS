from flask import Flask, request, render_template, send_file, jsonify
from flask_cors import CORS
from rembg import remove, new_session
from PIL import Image, ImageFilter, ImageEnhance
import io
import os
import uuid
import cv2
import numpy as np

app = Flask(__name__)
CORS(app)  # Enable CORS cross-domain support

# Configure upload folders
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 创建必要的文件夹
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    print("Received upload request")
    print("request.files:", request.files)
    print("request.method:", request.method)

    if 'file' not in request.files:
        print("No file in request.files")
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    print("Filename:", file.filename)

    if file.filename == '':
        print("Filename is empty")
        return jsonify({'error': 'No file selected'}), 400

    if file:
        # Generate unique filename
        filename = str(uuid.uuid4()) + '.png'
        original_filename = file.filename

        # Save original file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print("Saving file to:", file_path)
        file.save(file_path)

        try:
            # Read and preprocess image
            print("Starting image processing...")

            # Directly use the most accurate portrait-specific model, no additional processing
            with open(file_path, 'rb') as input_file:
                input_data = input_file.read()

            # Try multiple models, select the cleanest result
            models_to_try = ['u2net', 'u2net_human_seg', 'isnet-general-use']
            best_result = None

            for model_name in models_to_try:
                try:
                    print(f"Trying model: {model_name}")
                    session = new_session(model_name)
                    output_data = remove(input_data, session=session)
                    best_result = output_data
                    print(f"Successfully used model: {model_name}")
                    break
                except Exception as e:
                    print(f"Model {model_name} failed: {e}")
                    continue

            if best_result is None:
                print("All models failed, using default method")
                best_result = remove(input_data)
            
            # Perform high-quality cleanup on results
            processed_image = Image.open(io.BytesIO(best_result))
            processed_image = clean_background_advanced(processed_image)

            # Save processed image
            processed_filename = 'processed_' + filename
            processed_path = os.path.join(app.config['PROCESSED_FOLDER'], processed_filename)
            print("Saving processed image to:", processed_path)

            processed_image.save(processed_path, 'PNG')

            print("Processing completed, returning success response")
            # Return processing results
            return jsonify({
                'success': True,
                'original_filename': original_filename,
                'processed_filename': processed_filename,
                'message': 'Image background has been successfully removed!'
            })

        except Exception as e:
            print("Processing error:", str(e))
            return jsonify({'error': f'Error processing image: {str(e)}'}), 500

def clean_background_advanced(image):
    """
    Advanced background cleaning, remove residues but protect subject integrity
    """
    try:
        # Convert to RGBA mode
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        # Convert to numpy array for processing
        img_array = np.array(image)
        alpha = img_array[:, :, 3]

        # 1. Create stricter foreground mask
        # Use multi-layer threshold to separate foreground and background more cleanly

        # High threshold: determined foreground area
        high_threshold = 200
        certain_fg = alpha > high_threshold

        # Low threshold: determined background area
        low_threshold = 50
        certain_bg = alpha < low_threshold

        # Middle area needs special processing
        uncertain = ~(certain_fg | certain_bg)
        
        # 2. Perform connectivity analysis on uncertain areas
        # Only keep parts connected to determined foreground
        if np.any(certain_fg):
            # Dilate determined foreground area to include edges
            kernel = np.ones((5, 5), np.uint8)
            expanded_fg = cv2.dilate(certain_fg.astype(np.uint8), kernel, iterations=2)

            # In uncertain areas, only keep parts connected to expanded foreground
            uncertain_connected = uncertain & (expanded_fg > 0)

            # Final foreground = determined foreground + connected uncertain areas
            final_fg = certain_fg | uncertain_connected
        else:
            # If no determined foreground, use original mask
            final_fg = alpha > (low_threshold + high_threshold) // 2
        
        # 3. Clean small noise and isolated areas
        # Remove small background noise
        kernel_clean = np.ones((3, 3), np.uint8)
        final_fg = cv2.morphologyEx(final_fg.astype(np.uint8), cv2.MORPH_OPEN, kernel_clean, iterations=1)

        # Fill small holes inside foreground
        final_fg = cv2.morphologyEx(final_fg, cv2.MORPH_CLOSE, kernel_clean, iterations=2)

        # 4. Edge smoothing
        final_fg = cv2.GaussianBlur(final_fg.astype(np.float32), (3, 3), 1)
        
        # 5. Apply cleaned mask
        new_alpha = np.zeros_like(alpha)
        new_alpha = (final_fg * 255).astype(np.uint8)

        # 6. Apply based on original alpha, preserve original edge details
        # Only apply new mask in high confidence areas
        confident_mask = (final_fg > 0.7) | (alpha > 240)
        new_alpha[confident_mask] = np.maximum(new_alpha[confident_mask], alpha[confident_mask])

        # Recombine image
        img_array[:, :, 3] = new_alpha

        # Convert back to PIL image
        processed_image = Image.fromarray(img_array, 'RGBA')

        print("High-quality background cleaning completed")
        return processed_image

    except Exception as e:
        print(f"Advanced cleaning failed: {e}, returning original image")
        return image

@app.route('/download/<filename>')
def download_file(filename):
    processed_path = os.path.join(app.config['PROCESSED_FOLDER'], filename)
    if os.path.exists(processed_path):
        return send_file(processed_path, as_attachment=True, download_name='background_removed_result.png')
    else:
        return jsonify({'error': 'File does not exist'}), 404

@app.route('/processed/<filename>')
def get_processed_image(filename):
    processed_path = os.path.join(app.config['PROCESSED_FOLDER'], filename)
    if os.path.exists(processed_path):
        return send_file(processed_path, mimetype='image/png')
    else:
        return jsonify({'error': 'File does not exist'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
