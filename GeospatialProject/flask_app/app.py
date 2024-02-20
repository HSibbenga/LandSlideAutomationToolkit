import sys
sys.path.append('/home/gis/tmp/LandSlideAutomationToolkit/GeospatialProject/flask_app')


import os
import logging  # For logging
from flask import Flask, request, render_template
import LSAT_process

app = Flask(__name__)

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to check if the uploaded file is allowed
def allowed_file(filename):
    return filename is not None and '.' in filename and filename.rsplit('.', 1)[1].lower() in {'tif', 'tiff', 'shp'}

# Define directories for different file types
UPLOAD_DIRECTORIES = {
    'global_tiff': 'global_tiff_files',
    'shapefile': 'shape_files',
    'higher_res': 'higher_res_files'
}

# Function to get existing files in a directory
def get_existing_files(directory, extensions):
    if os.path.exists(directory):
        return [file for file in os.listdir(directory) if file.endswith(extensions)]
    return []

# Function to get the upload directory based on file type
def get_upload_directory(file_type):
    directory = UPLOAD_DIRECTORIES.get(file_type, 'uploads')
    # Create directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

# Route to render the upload form
@app.route('/')
def upload_form():
    global_tiff_files = get_existing_files(get_upload_directory('global_tiff'), ('.tif', '.tiff'))
    shape_files = get_existing_files(get_upload_directory('shapefile'), '.shp')
    higher_res_files = get_existing_files(get_upload_directory('higher_res'), ('.tif', '.tiff'))
    return render_template('upload.html', global_tiff_files=global_tiff_files, shape_files=shape_files, higher_res_files=higher_res_files)


# Route to handle file upload
@app.route('/', methods=['POST'])
def process_files():

    higher_res_path = None

    try:
        global_tiff_upload = request.files.get('global_tiff_upload') # Get the uploaded global tiff file
        shp_admin_upload = request.files.get('shp_admin_upload') # Get the uploaded shapefile
        higher_res_upload = request.files.get('higher_res_upload') # Get the uploaded higher resolution file

        choice = request.form.get('analysisChoice')

        logging.info('User choice: %s', choice)

        # Check if the uploaded files are allowed
        if not allowed_file(global_tiff_upload.filename) if global_tiff_upload else False \
            or not allowed_file(shp_admin_upload.filename) if shp_admin_upload else False:
            raise Exception('Invalid file format. Allowed formats: .tif, .tiff, .shp')

        # Save the uploaded files to their respective directories
        if global_tiff_upload:
            global_tiff_upload.save(os.path.join(get_upload_directory('global_tiff'), global_tiff_upload.filename))
        if shp_admin_upload:
            shp_admin_upload.save(os.path.join(get_upload_directory('shapefile'), shp_admin_upload.filename))
        if higher_res_upload:
            higher_res_upload.save(os.path.join(get_upload_directory('higher_res'), higher_res_upload.filename))

        global_tiff_file = request.form['global_tiff'] if request.form.get('global_tiff') else None # Get the uploaded global tiff file
        shp_admin_file = request.form['shp_admin'] if request.form.get('shp_admin') else None # Get the uploaded shapefile
        higher_res_file = request.form.get('higher_res') # Get the uploaded higher resolution file

        if global_tiff_upload:
            global_tiff_path = os.path.join(get_upload_directory('global_tiff'), global_tiff_upload.filename)
        else:
            global_tiff_path = os.path.join(get_upload_directory('global_tiff'), global_tiff_file) if global_tiff_file else None

        if shp_admin_upload:
            shp_admin_path = os.path.join(get_upload_directory('shapefile'), shp_admin_upload.filename)
        else:
            shp_admin_path = os.path.join(get_upload_directory('shapefile'), shp_admin_file) if shp_admin_file else None

        if higher_res_file:
            if higher_res_upload:
                higher_res_path = os.path.join(get_upload_directory('higher_res'), higher_res_upload.filename)
            else:
                higher_res_path = os.path.join(get_upload_directory('higher_res'), higher_res_file)

        landslide_analysis_choice = True if choice == 'yes' else None
        
        return LSAT_process.process_files(global_tiff_path, shp_admin_path, higher_res_path, landslide_analysis_choice)
    except Exception as e:
        logging.error(f"An Error occurred: {e}")
        raise e

if __name__ == "__main__":
    app.run(debug=True)