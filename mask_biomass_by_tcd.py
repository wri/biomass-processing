### This script masks Woods Hole biomass tiles by a user-defined tree cover density.
### It requires both biomass tiles and TCD tiles.
### Biomass pixels where TCD<threshold will be output as NoData while biomass pixels with TCD>threshold
### will be unchanged.

### David Gibbs, World Resources Institute, started July 2018

import subprocess
import os
import multiprocessing

# Copies the tiles in the s3 folder to the spot machine
def s3_to_spot(folder):

    dld = ['aws', 's3', 'cp', folder, '.', '--recursive']
    subprocess.check_call(dld)


# Lists all the biomass tiles on the spot machine
def list_tiles():

    # Makes a text file of the tifs in the folder on the spot machine
    os.system('ls *biomass.tif > processed_biomass_tiles.txt')

    # List for the tile names
    biomass_file_list = []

    # Iterates through the text file to get the names of the tiles and appends them to list
    with open('processed_biomass_tiles.txt', 'r') as tile:
        for line in tile:
            # Extracts the tile name from the file name
            num = len(line)
            start = num - 21
            end = num - 13
            tile_short = line[start:end]

            biomass_file_list.append(tile_short)

    # The lists of tile names
    return biomass_file_list


def mask_biomass_by_tcd(tile_id):

    # The tree cover density below which biomass will be masked (only biomass pixels on TCD pixels > this value will be output)
    tcd_mask = 30

    # Names of the input biomass and TCD tiles
    biomass_tile = '{}_biomass.tif'.format(tile_id)
    tcd_tile = 'Hansen_GFC2014_treecover2000_{}.tif'.format(tile_id)

    # Output file name
    outname = '{0}_biomass_at_{1}tcd.tif'.format(tile_id, tcd_mask)

    # Equation argument for masking biomass below TCD threshold
    calc = '--calc=A*(B>{})'.format(tcd_mask)

    # Argument for outputting file
    out = '--outfile={}'.format(outname)

    print "Masking tile", tile_id, "..."
    cmd = ['gdal_calc.py', '-A', biomass_tile, '-B', tcd_tile,  calc, out, '--NoDataValue=0', '--co', 'COMPRESS=LZW', '--overwrite']
    subprocess.check_call(cmd)
    print "  Tile masked"

    print "  Copying tile to s3..."
    s3_folder = 's3://WHRC-carbon/WHRC_V4/Masked_to_{}tcd/'.format(tcd_mask)
    cmd = ['aws', 's3', 'cp', outname, s3_folder]
    subprocess.check_call(cmd)
    print "    Tile copied to s3"


### Actually masks the biomass tiles by tree cover density

# Location of the biomass tiles on s3
s3_biomass_locn = 's3://WHRC-carbon/WHRC_V4/Processed/'

print "Checking if biomass tiles are already downloaded..."

if os.path.exists('./60N_010W_biomass.tif') == False:     # This is a bad way to check if files are downloaded but doing it anyhow

    # Copies all the tiles in the s3 folder
    print "  Copying biomass tiles to spot machine..."
    s3_to_spot(s3_biomass_locn)
    print "    Biomass tiles copied"

else:

    print "  Biomass tiles already on machine"

print "Getting list of biomass tiles..."
biomass_file_list = list_tiles()
print "  Biomass tile list retrieved. There are", len(biomass_file_list), "biomass tiles total."

# Location of the tree cover density tiles on s3
s3_tcd_locn = 's3://gfw2-data/forest_cover/2000_treecover/'

print "Checking if tree cover density tiles are already downloaded..."

if os.path.exists('./Hansen_GFC2014_treecover2000_60N_010W.tif') == False:   # This is a bad way to check if files are downloaded but doing it anyhow

    # Creates a list of all the tiles on s3
    print "  Copying TCD tiles to spot machine..."
    s3_to_spot(s3_tcd_locn)
    print "    TCD tiles copied"

else:

    print "  TCD tiles already on machine"

# For multiple processors
count = multiprocessing.cpu_count()
pool = multiprocessing.Pool(count/3)
pool.map(mask_biomass_by_tcd, biomass_file_list)

# # For a single processor
# for tile in biomass_file_list:
#     mask_biomass_by_tcd(tile)
