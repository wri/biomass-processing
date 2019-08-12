# Converts the aboveground biomass 2000 tiles to aboveground CO2 emissions tiles (tons CO2/hectare)
# wherever there is a Hansen loss pixel.

import subprocess
import os
import re
import argparse
import multiprocessing
from osgeo import gdal

# Copies the tiles in the s3 folder to the spot machine
def s3_to_spot(folder):

    dld = ['aws', 's3', 'cp', folder, '.', '--recursive']
    subprocess.check_call(dld)


# Gets the tile id from the full tile name using a regular expression
def get_tile_id(tile_name):

    # based on https://stackoverflow.com/questions/20003025/find-1-letter-and-2-numbers-using-regex and https://docs.python.org/3.4/howto/regex.html
    tile_id = re.search("[0-9]{2}[A-Z][_][0-9]{3}[A-Z]", tile_name).group()

    return tile_id

# Lists all the tiles in a folder on s3
def list_tiles(source):

    print "Creating list of tiles..."

    ## For an s3 folder in a bucket using AWSCLI
    # Captures the list of the files in the folder
    out = subprocess.Popen(['aws', 's3', 'ls', source], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = out.communicate()

    # Writes the output string to a text file for easier interpretation
    biomass_tiles = open("tiles.txt", "w")
    biomass_tiles.write(stdout)
    biomass_tiles.close()

    file_list = []

    # Iterates through the text file to get the names of the tiles and appends them to list
    with open("tiles.txt", 'r') as tile:
        for line in tile:
            num = len(line.strip('\n').split(" "))
            tile_name = line.strip('\n').split(" ")[num - 1]

            # Only tifs will be in the tile list
            if '.tif' in tile_name:

                tile_id = get_tile_id(tile_name)
                file_list.append(tile_id)

    return file_list

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
s3_to_spot(loss_dir)
print "    Loss tiles copied"

print "Getting list of loss tiles..."
loss_file_list = list_tiles(loss_dir)
print loss_file_list
print "  Biomass tile list retrieved. There are", len(loss_file_list), "biomass tiles total."

# Copies all the biomass tiles in the s3 folder
print "  Copying biomass tiles to spot machine..."
s3_to_spot(biomass_dir)
print "    Biomass tiles copied"



# For multiple processors
count = multiprocessing.cpu_count()
pool = multiprocessing.Pool(count/3)
pool.map(biomass_to_emissions_ha, loss_file_list)

# # For a single processor
# for tile in loss_file_list:
#     mask_biomass_by_loss(tile)
