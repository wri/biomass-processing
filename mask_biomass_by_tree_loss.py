

import subprocess
import os
import multiprocessing
from osgeo import gdal

# Copies the tiles in the s3 folder to the spot machine
def s3_to_spot(folder):

    dld = ['aws', 's3', 'cp', folder, '.', '--recursive', '--exclude', '*.xml']
    subprocess.check_call(dld)


# Lists all the tiles on the spot machine
def list_tiles():

    # Makes a text file of the tifs in the folder on the spot machine
    os.system('ls *biomass.tif > spot_biomass_tiles.txt')

    # List for the tile names
    file_list = []

    # Iterates through the text file to get the names of the tiles and appends them to list
    with open('spot_biomass_tiles.txt', 'r') as tile:
        for line in tile:
            # Extracts the tile name from the file name
            tile_short = line[0:8]

            file_list.append(tile_short)

    # The lists of unique tile names and all tile names
    return file_list


def mask_biomass_by_loss(tile_id):

    # Names of the input biomass and TCD tiles
    biomass_tile = '{}_biomass.tif'.format(tile_id)
    loss_tile = '{}.tif'.format(tile_id)

    # Output file name
    outname = '{0}_biomass_masked_by_loss.tif'.format(tile_id)

    # Equation argument for masking biomass below TCD threshold
    calc = '--calc=A*(B>0)'

    # Argument for outputting file
    out = '--outfile={}'.format(outname)

    print "Masking tile", tile_id, "by loss pixels..."
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
        s3_folder = 's3://WHRC-carbon/WHRC_V4/Masked_by_loss/'
        cmd = ['aws', 's3', 'cp', outname, s3_folder]
        subprocess.check_call(cmd)
        print "    Tile copied to s3"

    else:

        print "  No data found. Not copying tile."


## Actually masks the biomass tiles by tree cover density

# Location of the biomass tiles on s3
s3_biomass_locn = 's3://WHRC-carbon/WHRC_V4/Processed/'

# # Copies all the tiles in the s3 folder
# print "  Copying biomass tiles to spot machine..."
# s3_to_spot(s3_biomass_locn)
# print "    Biomass tiles copied"

print "Getting list of biomass tiles..."
biomass_file_list = list_tiles()
print "  Biomass tile list retrieved. There are", len(biomass_file_list), "biomass tiles total."

# Location of the tree cover density tiles on s3
s3_tcd_locn = 's3://gfw2-data/forest_change/hansen_2017/'

# # Copies tree loss tiles to spot machine
# print "  Copying TCD tiles to spot machine..."
# s3_to_spot(s3_tcd_locn)
# print "    TCD tiles copied"

# For multiple processors
count = multiprocessing.cpu_count()
pool = multiprocessing.Pool(count/3)
pool.map(mask_biomass_by_loss, biomass_file_list)

# # For a single processor
# for tile in biomass_file_list:
#     mask_biomass_by_loss(tile)
