import geopandas as gpd  # For handling geographic data
import rasterio  # For reading and writing raster datasets
from rasterio.mask import mask  # For masking raster datasets with geometric shapes
import json  # For parsing JSON format data
import logging  # For logging

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Blueprint
class RasterMasker:
    def __init__(self, raster_path, shp_path, output_path):
        # Constructor method to initialize the class object
        self.raster_path = raster_path  # Path to the input raster dataset
        self.shp_path = shp_path  # Path to the shapefile
        self.output_path = output_path  # Path to where the masked_raster will be saved

    @staticmethod
    def get_features(gdf):
        """Convert geodataframe to JSON features."""
        # This method converts a GDF to a list of geometry features in JSON format
        try:
            return [json.loads(gdf.to_json())['features'][i]['geometry'] for i in range(len(gdf))]
        except Exception as e:
            logging.error(f"An error occurred while converting geodataframe to JSON features: {e}")
            raise Exception(f"An error occurred: {e}")

    def mask_raster_with_shp(self):
        """Mask raster with Shapefile boundaries and save as new TIFF."""
        # This method performs the main functionality of masking a raster dataset using a shp
        try:
            logging.info("Loading shapefile as GeoDataFrame...")
            gdf = gpd.read_file(self.shp_path)  # Load shapefile as GeoDataFrame
            logging.info("Shapefile loaded successfully.")

            logging.info("Opening input raster dataset...")
            with rasterio.open(self.raster_path) as src:
                logging.info("Input raster dataset opened successfully.")
                logging.info("Converting GeoDataFrame to JSON features...")
                geoms = self.get_features(gdf)  # Convert GeoDataFrame to JSON features
                logging.info("GeoDataFrame converted to JSON features successfully.")

                logging.info("Applying mask to raster dataset...")
                out_image, out_transform = mask(src, geoms, crop=True)  # Apply mask
                logging.info("Mask applied successfully.")

                logging.info("Copying metadata of the source raster...")
                out_meta = src.meta.copy()  # Copy metadata of the source raster
                logging.info("Metadata copied successfully.")

            # Update metadata
            out_meta.update({
                "driver": "GTiff",  # Set the format of the output raster to TIFF
                "height": out_image.shape[1],  # Update height from the output image dimensions
                "width": out_image.shape[2],  # Update the width from the output image dimensions
                "transform": out_transform  # Update the affine transformation parameters
            })

            logging.info("Opening output raster dataset for writing...")
            with rasterio.open(self.output_path, "w", **out_meta) as dest:
                logging.info("Output raster dataset opened successfully.")
                logging.info("Writing masked dataset to file...")
                dest.write(out_image)  # Write to the file
                logging.info("Masked raster dataset written successfully.")

            logging.info(f"Masked raster saved to {self.output_path}")
            return self.output_path  # Return the path of the masked output
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            raise Exception(f"An error occurred: {e}")
