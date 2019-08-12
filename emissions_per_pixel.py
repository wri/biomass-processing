# Converts the aboveground CO2 emissions per hectare tiles to aboveground CO2 emissions per pixel (tCO2/pixel)
# wherever there is an emissions pixel.

import subprocess
import utilities
import argparse
import multiprocessing
from osgeo import gdal

# Converts aboveground biomass per hectare to emissions from aboveground biomass per hectare
def emissions_per_pixel(tile_id, out_dir):

    # m2 per hectare
    m2_per_ha = 100*100

    # Names of the input biomass and TCD tiles
    emis_ha_tile = '{}_tCO2_ha_AGB_masked_by_loss.tif'.format(tile_id)
    area_tile = 'hanson_2013_area_{}.tif'.format(tile_id)

    # Output file name
    outname = '{}_tCO2_pixel_AGB_masked_by_loss.tif'.format(tile_id)

    # Equation argument for converting emissions from per hectare to per pixel.
    # First, multiplies the per hectare emissions by the area of the pixel in m2, then divides by the number of m2 in a hectare.
    calc = '--calc=A*B/{}'.format(m2_per_ha)

    # Argument for outputting file
    out = '--outfile={}'.format(outname)

    print "Converting {} from tons CO2/ha to tons CO2/pixel...".format(tile_id)
    cmd = ['gdal_calc.py', '-A', emis_ha_tile, '-B', area_tile,  calc, out, '--NoDataValue=0', '--co', 'COMPRESS=LZW', '--overwrite']
    subprocess.check_call(cmd)
    print "  Emissions calculated"

    print "Copying tile to s3..."
    out_dir_full = out_dir + "per_pixel/"
    cmd = ['aws', 's3', 'cp', outname, out_dir_full]
    subprocess.check_call(cmd)
    print "  Tile copied to s3"
