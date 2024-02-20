# Geospatial Analysis Project
<!-- Title of the project -->

## Description
<!-- A brief introduction and overview of the project -->
This project is designed to analyse geospatial data related to landslide risk and population impact. Utilising raster data processing techniques, it offers tools for masking, upsampling raster images, and performing landslide population analysis.

## Installation
<!-- Instructions on how to get the project set up for use -->

### Prerequisites
<!-- List of prerequisites like software, libraries, and tools with their versions -->
- Python version 3.x
- Required libraries: `rasterio`, `geopandas`, `numpy`, `pandas`,`GDAL`, `Flask`
- Landslide risk index global raster : preferable stored data/input
- Shapefile with adm level boundaries : preferable stored data/input
- Population raster dataset : preferable stored data/input

### Setup
<!-- Step-by-step instructions to install and set up the project -->
1. Clone the repository to your local machine:
   
2. Navigate to the project directory:

3. Set up a Python virtual enviroment (reccomended)

    For Windows: python -m venv venv
    .\venv\Scripts\activate
    For macOS/Linux: python3 -m venv venv
    source venv/bin/activate
 
4. Install the required Python packages:
 
    pip install -r requirements.txt

## Usage
<!-- Guide on how to use the project, including commands and example workflows -->
- Enter the flask_app directory:

- Run the Flask app:
  - python app.py

Open your web browser and go to http://localhost:5000 to view the app.

## Contributing
<!-- Guidelines for contributors on how to help with the project -->
Contributions to this project are welcome! If you have improvements or code contributions to make, please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -am 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a pull request.

## License
<!-- Information about the project's license -->


