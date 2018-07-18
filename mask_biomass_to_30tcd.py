import subprocess
import os
import multiprocessing

def s3_to_spot(folder):

    dld = ['aws', 's3', 'cp', folder, '.', '--recursive', '--exclude', '*.xml']
    subprocess.check_call(dld)

def list_tiles():
    # Makes a text file of the tifs in the folder
    os.system('ls *.tif > processed_biomass_tiles.txt')

    total_file_list = []

    # Iterates through the text file to get the names of the tiles and appends them to list
    with open('processed_biomass_tiles.txt', 'r') as tile:
        for line in tile:
            # Extracts the tile name from the file name
            num = len(line)
            start = num - 13
            end = num - 5
            tile_short = line[start:end]

            total_file_list.append(tile_short)

    # Some tile names were in multiple ecoregions (e.g., 30N_110W in Palearctic and Nearctic). This produces only the unique tile names.
    unique_file_list = set(total_file_list)

    # The lists of unique tile names and all tile names
    return unique_file_list, total_file_list


def mask_biomass(tile_id):

    print "Hello"

    biomass_tile = 's3://WHRC-carbon/WHRC_V4/Processed/{}_biomass.tif'.format(tile_id)
    tcd_tile = 's3://gfw2-data/forest_cover/2000_treecover/Hansen_GFC2014_treecover2000_{}.tif'.format(tile_id)

    calc = '--calc=A*(B>30)'

    print "  Masking tile..."
    out = '{}_biomass_at_30tcd.tif'.format(tile_id)
    cmd = ['gdal_calc.py', '-A', biomass_tile, '-B', tcd_tile,  calc, out, '--NoDataValue=-9999', '--co', 'COMPRESS=LZW']
    subprocess.check_call(cmd)
    print "    Tile masked"

    print "  Copying tile to s3..."
    s3_folder = 's3://WHRC-carbon/WHRC_V4/More_than_30tcd/'
    cmd = ['aws', 's3', 'cp', out, s3_folder]
    subprocess.check_call(cmd)
    print "    Tile copied to s3"


# Location of the biomass tiles on s3
s3_biomass_locn = 's3://WHRC-carbon/WHRC_V4/Processed/'

print "Checking if biomass tiles are already downloaded..."

if os.path.exists('./Palearctic_MapV4_60N_010W.tif') == False:

    # Creates a list of all the tiles on s3
    print "  Copying biomass tiles to spot machine..."
    s3_to_spot(s3_biomass_locn)
    print "    Biomass tiles copied"

else:

    print "  Biomass tiles already on machine"

# Location of the tree cover density tiles on s3
s3_tcd_locn = 's3://gfw2-data/forest_cover/2000_treecover/'

print "Checking if tree cover density tiles are already downloaded..."

print "Getting list of tiles..."
unique_file_list, total_file_list = list_tiles()
print "  Tile list retrieved. There are", len(total_file_list), "tiles total and", len(unique_file_list), "unique tiles in the dataset"


if os.path.exists('./Hansen_GFC2014_treecover2000_50N_050W.tif') == False:

    # Creates a list of all the tiles on s3
    print "  Copying TCD tiles to spot machine..."
    s3_to_spot(s3_tcd_locn)
    print "    TCD tiles copied"

else:

    print "  TCD tiles already on machine"


# # For a single processor
# for tile in unique_file_list:
#     print "Processing tile {}".format(tile)
#     process_tile(tile)
#     print "   Tile processed"

# For multiple processors
count = multiprocessing.cpu_count()
pool = multiprocessing.Pool(count/3)
pool.map(mask_biomass, unique_file_list)
