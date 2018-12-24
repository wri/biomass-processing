### This script processes raw Woods Hole biomass tiles to conform to Hansen loss and tree cover density tiles
### in terms of pixel size, tile extent, pixel alignment, compression, etc.
### It requires only biomass tiles and it exports only tiles with biomass values.

### David Gibbs, World Resources Institute, started July 2018

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
    os.system('ls *.tif > spot_biomass_tiles.txt')

    # List for the tile names
    total_file_list = []

    # Iterates through the text file to get the names of the tiles and appends them to list
    with open('spot_biomass_tiles.txt', 'r') as tile:
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


# Creates a virtual raster mosaic
def create_vrt():

    # Names and creates the virtual raster mosaic
    vrtname = 'biomass_v4.vrt'
    os.system('gdalbuildvrt {0} *.tif'.format(vrtname))

    return vrtname


# Gets the bounding coordinates for each tile
def coords(tile_id):
    NS = tile_id.split("_")[0][-1:]
    EW = tile_id.split("_")[1][-1:]

    if NS == 'S':
        ymax = -1 * int(tile_id.split("_")[0][:2])
    else:
        ymax = int(str(tile_id.split("_")[0][:2]))

    if EW == 'W':
        xmin = -1 * int(str(tile_id.split("_")[1][:3]))
    else:
        xmin = int(str(tile_id.split("_")[1][:3]))

    ymin = str(int(ymax) - 10)
    xmax = str(int(xmin) + 10)

    return str(ymax), str(xmin), str(ymin), str(xmax)


# Cuts the vrt into Hansen-compatible 10x10 chunks
def process_tile(tile_id):

    print "  Getting coordinates for {}".format(tile_id), "..."
    ymax, xmin, ymin, xmax = coords(tile_id)
    print "    Coordinates are: ymax-", ymax, "; ymin-", ymin, "; xmax-", xmax, "; xmin-", xmin

    print "  Warping tile..."
    out = '{}_t_aboveground_biomass_ha_2000.tif'.format(tile_id)
    warp = ['gdalwarp', '-t_srs', 'EPSG:4326', '-co', 'COMPRESS=LZW', '-tr', '0.00025', '0.00025', '-tap', '-te', xmin, ymin, xmax, ymax, '-dstnodata', '-9999', vrtname, out]
    subprocess.check_call(warp)
    print "    Tile warped"

    print "Checking if {} contains any data...".format(tile_id)
    # Source: http://gis.stackexchange.com/questions/90726
    # Opens raster and chooses band to find min, max
    gtif = gdal.Open(out)
    srcband = gtif.GetRasterBand(1)
    stats = srcband.GetStatistics(True, True)
    print "  Tile stats =  Minimum=%.3f, Maximum=%.3f, Mean=%.3f, StdDev=%.3f" % (stats[0], stats[1], stats[2], stats[3])

    if stats[1] > 0:

        print "  Data found in {}. Copying tile to s3...".format(tile_id)
        cmd = ['aws', 's3', 'cp', out, out_folder]
        subprocess.check_call(cmd)
        print "    Tile copied to s3"

    else:

        print "  No data found. Not copying {}.".format(tile_id)


### Actually processes the tiles

# Location of the tiles on s3
s3_locn = 's3://gfw2-data/climate/WHRC_biomass/WHRC_V4/As_provided/'

# Where the tiles will be output to
out_folder = 's3://gfw2-data/climate/WHRC_biomass/WHRC_V4/Processed/'

print "Checking if tiles are already downloaded..."

if os.path.exists('./Neotropic_MapV4_30N_110W.tif') == False:       # This is a bad way to check if files are downloaded but doing it anyhow

    # Copies all the tiles in the s3 folder
    print "  Copying raw tiles to spot machine..."
    s3_to_spot(s3_locn)
    print "    Raw tiles copied"

else:

    print "  Tiles already copied"

print "Getting list of tiles..."            #For v4 of the Woods Hole data, there were 315 unique tiles (counts tiles in multiple regions only once)
unique_file_list, total_file_list = list_tiles()
print "  Tile list retrieved. There are", len(total_file_list), "tiles total and", len(unique_file_list), "unique tiles in the dataset"

print "Creating vrt..."
vrtname = create_vrt()
print "  vrt created"

# For multiple processors
count = multiprocessing.cpu_count()
pool = multiprocessing.Pool(count/3)
pool.map(process_tile, unique_file_list)

# # For a single processor
# for tile in unique_file_list:
#     print "Processing tile {}".format(tile)
#     process_tile(tile)
#     print "   Tile processed"

