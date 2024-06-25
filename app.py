from flask import Flask, request, render_template, redirect, url_for, session
from PIL import Image
import cv2
import numpy as np
import os
from werkzeug.utils import secure_filename
import glob  # Added for efficient folder cleaning

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.secret_key = 'supersecretkey'  # Required for using session

def convert_to_watercolor_sketch(inp_img):
    img_1 = cv2.edgePreservingFilter(inp_img, flags=2, sigma_s=50, sigma_r=0.8)
    img_water_color = cv2.stylization(img_1, sigma_s=100, sigma_r=0.5)
    return img_water_color

def pencil_sketch(inp_img):
    img_pencil_sketch, pencil_color_sketch = cv2.pencilSketch(
        inp_img, sigma_s=50, sigma_r=0.07, shade_factor=0.0825)
    return img_pencil_sketch

def load_image(image_path):
    return Image.open(image_path)

def delete_old_image(image_path):
    """Safely deletes the image at the given path, handling errors."""
    if image_path and os.path.exists(image_path):
        try:
            os.remove(image_path)
        except OSError as e:
            print(f"Error deleting old image: {e}")

def resize_image(image_path):
    img = Image.open(image_path)
    img = img.resize((400, 300), Image.LANCZOS)  # Resize using LANCZOS filter
    img.save(image_path)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Resize the image
            resize_image(file_path)
            
            session['original_image'] = file_path  # Save image path in session
            return render_template('index.html', original_image=session.get('original_image'))
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    if 'convert_option' in request.form and session['original_image']:
        option = request.form['convert_option']
        image_path = session['original_image']
        image = np.array(load_image(image_path))

        if option == 'Watercolor Sketch':
            final_sketch = convert_to_watercolor_sketch(image)
        elif option == 'Pencil Sketch':
            final_sketch = pencil_sketch(image)

        sketch_pil = Image.fromarray(final_sketch)
        sketch_path = os.path.join(app.config['UPLOAD_FOLDER'], 'sketch.png')
        sketch_pil.save(sketch_path)

        return render_template('index.html', original_image=image_path, sketch_path=sketch_path)

    return redirect(url_for('upload_file'))

if __name__ == '__main__':
    app.run(debug=True)
