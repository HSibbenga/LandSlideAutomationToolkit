import sys
sys.path.append('/home/gis/LandSlideAutomationToolkit/GeospatialProject/flask_app')

import os
import logging  # For logging
from flask import Flask, request, render_template
import LSAT_process

app = Flask(__name__)

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to check if the uploaded file is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'tif', 'tiff', 'shp'}

# Route to render the upload form
@app.route('/')
def upload_form():
    return render_template('upload.html')

# Route to handle file upload
@app.route('/', methods=['POST'])
def process_files():
    try:
        global_tiff_path = request.form['global_tiff_path']
        shp_admin_path = request.form['shp_admin_path']
        higher_res_path = request.form.get('higher_res_path')

        choice = request.form.get('analysisChoice')

        logging.info('User choice: %s', choice)

        # Check if the provided file paths exist
        if not os.path.isfile(global_tiff_path):
            raise FileNotFoundError('Global TIFF file path does not exist')
        
        if not os.path.isfile(shp_admin_path):
            raise FileNotFoundError('Admin Shapefile path does not exist')

        # Optionally, check if the higher resolution path exists
        if higher_res_path and not os.path.isfile(higher_res_path):
            raise FileNotFoundError('Higher resolution TIFF file path does not exist')

        landslide_analysis_choice = True if choice == 'yes' else None
        
        return LSAT_process.process_files(global_tiff_path, shp_admin_path, higher_res_path, landslide_analysis_choice)
    except Exception as e:
        logging.error(f"An Error occurred: {e}")
        raise e

if __name__ == "__main__":
    app.run(debug=True)
