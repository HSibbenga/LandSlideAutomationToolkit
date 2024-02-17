import os
from pathlib import Path
import rasterio
import numpy as np
import pandas as pd
# Import custom modules
from raster_masker import RasterMasker
from raster_upsampler import RasterUpsampler
from LandslidePopulationAnalysis import LandslidePopulationAnalysis

# Function to set the working dir to the project dir
def set_working_directory(target_dir_name="GeospatialProject"):
    # Get the current script's directory
    current_script_path = Path(__file__).resolve().parent

    # Search for the target directory in the current path and its parents with the target name
    target_dir_path = current_script_path
    while target_dir_path.name != target_dir_name and target_dir_path.parent != target_dir_path:
        target_dir_path = target_dir_path.parent

    # Check if the target directory was found, change the current working dir to it
    if target_dir_path.name == target_dir_name:
        # Change the working directory to the target directory
        os.chdir(target_dir_path)
        print(f"Changed working directory to: {target_dir_path}")
    else:
        print(f"Warning: Target directory '{target_dir_name}' not found. Current working directory is {Path.cwd()}") # Print a warning if not found

# Function to convert raster to csv : extracting lon lat and pixel values
def convert_raster_to_csv(file_path):
    with rasterio.open(file_path) as src: # open rast for reading
        array = src.read(1)  # Reading the first band
        transform = src.transform # rasterio method to convert pixel coordinates to world coordinates
        
        rows, cols = np.where(array != src.nodata) # Identify all pixels that are not NoData values
        values = array[rows, cols] # Extract them
        geoms = [transform * (col, row) for row, col in zip(rows, cols)] # Convert pixel coordinates to world lon lat
        lons, lats = zip(*geoms)
        
        df = pd.DataFrame({'longitude': lons, 'latitude': lats, 'value': values}) # create a df with lon lat and pixel value collumn
        
        output_csv_path = file_path.rsplit('.', 1)[0] + '_upsampled.csv' # Generate the csv path
        df.to_csv(output_csv_path, index=False) # Save to csv
        print(f"Upsampled raster data exported to CSV at: {output_csv_path}")

## Main function to execute the workflow: 
#        
# Main function to execute the workflow:
# 1. Initial Setup: Begins by printing the current working directory to provide context on where the script is running. 
#    It then prepares an output directory ('data/output'), ensuring it exists for storing output files.
#
# 2. Data Input: The user is prompted to enter paths for essential datasets - a global raster TIFF representing some geospatial 
#    data (landslide risk index) and a Shapefile containing administrative boundaries. These inputs are foundational 
#    for the subsequent analysis.
#
# 3. Raster Masking: A RasterMasker object is instantiated with paths to the input raster and Shapefile, along with a designated 
#    output path for the masked raster. The RasterMasker's method 'mask_raster_with_shp' is called to apply the Shapefile's 
#    boundaries as a mask to the raster, focusing the analysis on specified regions. This step is critical for isolating the 
#    area of interest from the global dataset.
#
# 4. Optional Upsampling: The user decides whether to upsample the masked TIFF file to a higher resolution. If chosen, the path 
#    to a higher-resolution population data raster is requested. This step involves creating an RasterUpsampler object and 
#    running the upsampling process, which adjusts the spatial resolution of the masked raster to match that of the 
#    high-resolution population data. Upsampling is pivotal for aligning the spatial granularity of data sources, ensuring 
#    consistency in subsequent analyses.
#
# 5. Raster to CSV Conversion: Regardless of upsampling, the script converts the final raster data (masked and upsampled) 
#    into a CSV format. This conversion facilitates easier manipulation and analysis of the data, particularly for tasks that 
#    might be conducted outside of GIS software (INFORM Subnational), leveraging the tabular data format's accessibility and versatility.
#
# 6. Landslide Population Analysis: With the raster data prepared, a LandslidePopulationAnalysis object is initialised, tasked 
#    with evaluating the population at risk within the landslide-prone areas defined by the raster data. This analysis 
#    quantifies the impact of landslides on human populations, culminating in the export of findings to a CSV file. 
#
##
def main():
    print(f"Current Working Directory: {Path.cwd()}")
    output_base_dir = Path("data") / "output" # Create output dir path
    output_base_dir.mkdir(parents=True, exist_ok=True)

    # Prompt user input
    raster_path = input("Enter the path to the input Global raster TIFF: ")
    shp_path = input("Enter the path to the Shapefile with administrative boundaries: ")
    masked_raster_filename = "masked_raster.tif" # Define the filename
    output_masked_path = output_base_dir / masked_raster_filename # Create the full path 

    raster_masker = RasterMasker(raster_path, shp_path, str(output_masked_path)) # Instance of RasterMAsker object
    raster_masker.mask_raster_with_shp() # Perform masking of raster
    print(f"Raster masking completed. Masked raster saved at: {output_masked_path}")

    upsampling_choice = input("Do you want to upsample the masked TIFF? (y/n): ").lower() # Ask user for upsample the masked tiff
    if upsampling_choice == 'y': # If yes prompt for path
        higher_res_path = input("Enter the path to the higher-resolution Population_Data TIFF for target resolution: ")
        upsampled_raster_filename = "upsampled_raster.tif" # Define file for upsampled raster
        output_upsampled_path = output_base_dir / upsampled_raster_filename # Create the full path 

        upsampler = RasterUpsampler(str(output_masked_path), higher_res_path, str(output_upsampled_path)) # Instance of RasterUpsampler
        upsampler.run_warp_tool() # Perform upsampling

        # After upsampling, convert the raster to CSV
        convert_raster_to_csv(str(output_upsampled_path))


        # Perform Landslide Population Analysis and export results to CSV
        #landslide_population_analysis = LandslidePopulationAnalysis(shp_path, str(output_upsampled_path), higher_res_path)
        #output_population_risk_path = output_base_dir / "population_at_risk.csv"
        #landslide_population_analysis.export_to_csv(output_population_risk_path)

        # Prompt the user to decide if they want to proceed with the Landslide Population Analysis
        landslide_analysis_choice = input("Do you want to perform Landslide Population Analysis? (y/n): ").lower()

        if landslide_analysis_choice == 'y':
            # If the user chooses 'y', proceed with the Landslide Population Analysis
            # Instantiate the LandslidePopulationAnalysis object with necessary paths
            landslide_population_analysis = LandslidePopulationAnalysis(shp_path, str(output_upsampled_path), higher_res_path)
            # Define the path for the CSV output that will contain the analysis results
            output_population_risk_path = output_base_dir / "population_at_risk.csv"
            # Execute the analysis and export the results to the defined CSV file
            landslide_population_analysis.export_to_csv(output_population_risk_path)
            print(f"Landslide Population Analysis completed. Results exported to: {output_population_risk_path}")
        else:
            # If the user chooses not to perform the analysis, print a message indicating the choice
            print("Landslide Population Analysis was skipped.")



if __name__ == "__main__":
    main()