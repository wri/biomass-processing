# Converts the aboveground biomass 2000 tiles to aboveground CO2 emissions tiles (tons CO2/hectare)
# wherever there is a Hansen loss pixel.

import subprocess
import argparse
import multiprocessing
import utilities
from osgeo import gdal

# Converts aboveground biomass per hectare to emissions from aboveground biomass per hectare
def biomass_to_emissions_ha(tile_id, out_dir):

    biomass_to_c = 0.5
    c_to_co2 = 3.66667
    megagrams_to_tons = 1

    # Names of the input biomass and TCD tiles
    biomass_tile = '{}_t_aboveground_biomass_ha_2000.tif'.format(tile_id)
    loss_tile = '{}.tif'.format(tile_id)

    # Output file name
    outname = '{0}_tCO2_ha_AGB_masked_by_loss.tif'.format(tile_id)

    # Equation argument for masking biomass below TCD threshold
    calc = '--calc=A*(B>0)*{0}*{1}*{2}'.format(biomass_to_c, c_to_co2, megagrams_to_tons)

    # Argument for outputting file
    out = '--outfile={}'.format(outname)

    print "Masking tile", tile_id, "by loss pixels and converting from megagrams biomass to tons CO2..."
    cmd = ['gdal_calc.py', '-A', biomass_tile, '-B', loss_tile,  calc, out, '--NoDataValue=0', '--co', 'COMPRESS=LZW', '--overwrite']
    subprocess.check_call(cmd)
    print "  Tile masked"

    print "Checking if masked tile contains any data in it...".format(tile_id)
    # Source: http://gis.stackexchange.com/questions/90726
    # Opens raster and chooses band to find min, max
    gtif = gdal.Open(outname)
    srcband = gtif.GetRasterBand(1)
    stats = srcband.GetStatistics(True, True)
    print "  Tile stats =  Minimum=%.3f, Maximum=%.3f, Mean=%.3f, StdDev=%.3f" % (stats[0], stats[1], stats[2], stats[3])

    if stats[0] > 0:

        print "  Data found in tile. Copying tile to s3..."
        out_dir_full = out_dir + "per_hectare/"
        cmd = ['aws', 's3', 'cp', outname, out_dir_full]
        subprocess.check_call(cmd)
        print "    Tile copied to s3"

    else:

        print "  No data found. Not copying tile."