# Converts the aboveground CO2 emissions per hectare tiles to aboveground CO2 emissions per pixel (tCO2/pixel)
# wherever there is an emissions pixel.

import subprocess
import utilities
import argparse
import multiprocessing
from osgeo import gdal

# Converts aboveground biomass per hectare to emissions from aboveground biomass per hectare
def emissions_per_pixel(tile_id, out_dir, max_year):

    # m2 per hectare
    m2_per_ha = 100*100

    # Names of the input biomass and TCD tiles
    emis_ha_tile = '{0}_Mg_CO2_ha_AGB_masked_by_loss_{1}.tif'.format(tile_id, max_year)
    area_tile = 'hanson_2013_area_{}.tif'.format(tile_id)

    # Output file name
    outname = '{0}_Mg_CO2_pixel_AGB_masked_by_loss_{1}.tif'.format(tile_id, max_year)

    # Equation argument for converting emissions from per hectare to per pixel.
    # First, multiplies the per hectare emissions by the area of the pixel in m2, then divides by the number of m2 in a hectare.
    calc = '--calc=A*B/{}'.format(m2_per_ha)

    # Argument for outputting file
    out = '--outfile={}'.format(outname)

    print "Converting {} from Mg CO2/ha to Mg CO2/pixel...".format(tile_id)
    cmd = ['gdal_calc.py', '-A', emis_ha_tile, '-B', area_tile,  calc, out, '--NoDataValue=0', '--co', 'COMPRESS=LZW', '--overwrite']
    subprocess.check_call(cmd)
    print "  Emissions calculated"

    print "Checking if masked tile contains any data in it...".format(tile_id)
    # Source: http://gis.stackexchange.com/questions/90726
    # Opens raster and chooses band to find min, max
    gtif = gdal.Open(outname)
    srcband = gtif.GetRasterBand(1)
    stats = srcband.GetStatistics(True, True)
    print "  Tile stats =  Minimum=%.3f, Maximum=%.3f, Mean=%.3f, StdDev=%.3f" % (stats[0], stats[1], stats[2], stats[3])

    if stats[0] > 0:

        print "  Data found in tile. Copying tile to s3..."
        out_dir_full = out_dir + "per_pixel/"
        cmd = ['aws', 's3', 'cp', outname, out_dir_full]
        subprocess.check_call(cmd)
        print "    Tile copied to s3"

    else:

        print "  No data found. Not copying tile."