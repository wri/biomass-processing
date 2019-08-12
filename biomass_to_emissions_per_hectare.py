# Converts the aboveground biomass 2000 tiles to aboveground CO2 emissions tiles (tons CO2/hectare)
# wherever there is a Hansen loss pixel.

import subprocess
import argparse
import multiprocessing
import utilities
from osgeo import gdal

# Converts aboveground biomass per hectare to emissions from aboveground biomass per hectare
def biomass_to_emissions_ha(tile_id):

    biomass_to_c = 0.5
    c_to_co2 = 3.67
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
        s3_folder = 's3://gfw2-data/climate/Hansen_emissions/2018_loss/per_hectare/'
        cmd = ['aws', 's3', 'cp', outname, s3_folder]
        subprocess.check_call(cmd)
        print "    Tile copied to s3"

    else:

        print "  No data found. Not copying tile."


## Actually masks the biomass tiles by tree cover density

parser = argparse.ArgumentParser(description='Convert WHRC biomass 2000/ha to CO2/ha masked by Hansen loss')
parser.add_argument('--biomass', '-b', required=True,
                    help='WHRC aboveground biomass in 2000/ha to use as basis for CO2')
parser.add_argument('--loss-year', '-l', required=True,
                    help='Hansen loss for 2001 to present year')
parser.add_argument('--output-dir', '-o', required=True,
                    help='Output s3 directory for CO2/ha masked by Hansen loss')
args = parser.parse_args()

biomass_dir = args.biomass
loss_dir = args.loss_year
out_dir = args.output_dir

# Location of the biomass tiles on s3
# s3://gfw2-data/climate/WHRC_biomass/WHRC_V4/Processed/

# Standard location of the annual tree cover loss tiles on s3
# s3://gfw2-data/forest_change/hansen_2018/

# Standard output directory on s3
# s3://gfw2-data/climate/Hansen_emissions/2018_loss/per_hectare/

# Example run code:
#  python biomass_to_emissions_per_hectare.py -b s3://gfw2-data/climate/WHRC_biomass/WHRC_V4/Processed/ -l s3://gfw2-data/forest_change/hansen_2018/ -o s3://gfw2-data/climate/Hansen_emissions/2018_loss/per_hectare/


# Copies tree loss tiles to spot machine
print "  Copying loss tiles to spot machine..."
utilities.s3_to_spot(loss_dir)
print "    Loss tiles copied"

print "Getting list of loss tiles..."
loss_file_list = utilities.list_tiles(loss_dir)
print loss_file_list
print "  Loss tile list retrieved. There are", len(loss_file_list), "loss tiles total."

# Copies biomass tiles in the s3 folder
print "  Copying biomass tiles to spot machine..."
utilities.s3_to_spot(biomass_dir)
print "    Biomass tiles copied"

print "Getting list of biomass tiles..."
biomass_file_list = utilities.list_tiles(biomass_dir)
print biomass_file_list
print "  Loss tile list retrieved. There are", len(biomass_file_list), "loss tiles total."

# In order to be processed, a tile must have both loss and biomass.
# There are some tiles that have only one of those.
# This creates a list of tiles that have loss and biomass.
shared_tile_list = list(set(biomass_file_list).intersection(loss_file_list))
print "  List of tiles with both biomass and loss retrieved. There are", len(shared_tile_list), "loss tiles total."

# For multiple processors
count = multiprocessing.cpu_count()
pool = multiprocessing.Pool(count/3)
pool.map(biomass_to_emissions_ha, shared_tile_list)

# # For a single processor
# for tile in loss_file_list:
#     mask_biomass_by_loss(tile)
