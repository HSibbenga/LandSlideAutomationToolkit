import geopandas as gpd
import rasterio
from rasterio.mask import mask as rasterio_mask
import numpy as np
import pandas as pd
import logging  # For logging

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Defining class to encapsulate the logic for analyzing population in areas at risk of landslide
class LandslidePopulationAnalysis:
    def __init__(self, shp_path, landslide_raster_path, population_raster_path):
        self.shp_path = shp_path
        self.landslide_raster_path = landslide_raster_path
        self.population_raster_path = population_raster_path

    # Method for masking a raster dataset with a given geometry, used to focus on specific areas
    def mask_raster(self, raster_path, geometry):
        try:
            with rasterio.open(raster_path) as src:
                out_image, out_transform = rasterio_mask(src, [geometry], crop=True)
                out_meta = src.meta.copy()
            return out_image, out_transform, out_meta
        except Exception as e:
            logging.error(f"Error masking raster {raster_path}: {e}")
            return None, None, None

    def calculate_population_in_risk_areas(self):
        try:
            gdf = gpd.read_file(self.shp_path)
        except Exception as e:
            logging.error(f"Error reading shapefile {self.shp_path}: {e}")
            return pd.DataFrame()

        results = []

        for _, row in gdf.iterrows():
            geometry = row['geometry']
            landslide_image, _, landslide_meta = self.mask_raster(self.landslide_raster_path, geometry)
            population_image, _, population_meta = self.mask_raster(self.population_raster_path, geometry)

            if landslide_image is None or population_image is None:
                continue

            max_rows = max(landslide_image.shape[1], population_image.shape[1])
            max_cols = max(landslide_image.shape[2], population_image.shape[2])

            landslide_padded = np.full((1, max_rows, max_cols), landslide_meta['nodata'], dtype=landslide_image.dtype)
            landslide_padded[:, :landslide_image.shape[1], :landslide_image.shape[2]] = landslide_image

            population_padded = np.full((1, max_rows, max_cols), population_meta['nodata'], dtype=population_image.dtype)
            population_padded[:, :population_image.shape[1], :population_image.shape[2]] = population_image

            landslide_image = landslide_padded
            population_image = population_padded

            population_nodata = population_meta.get('nodata', np.nan)
            population_image = np.where(population_image == population_nodata, np.nan, population_image)

            high_risk_mask = np.isin(landslide_image, [3, 4], assume_unique=True)

            population_at_risk = np.where(high_risk_mask, population_image, np.nan)
            total_population_at_risk = np.nansum(population_at_risk)

            total_population_at_risk = np.round(total_population_at_risk)

            if total_population_at_risk < 0:
                logging.warning(f"Negative population at risk for {row['ADM2_EN']}. Setting to zero, check your data.")
                total_population_at_risk = 0

            results.append({
                "admin_boundary": row['ADM2_EN'],
                "total_population_at_risk": total_population_at_risk
            })

        return pd.DataFrame(results)

    # Export to csv
    def export_to_csv(self, output_path):
        df = self.calculate_population_in_risk_areas()
        if not df.empty:
            df.to_csv(output_path, index=False)
            logging.info(f"Data exported to {output_path}")
        else:
            logging.warning("No data to export.")
