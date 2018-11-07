
import os
import subprocess
from osgeo import gdal

def s3_folder_download(source, dest):
    cmd = ['aws', 's3', 'cp', source, dest, '--recursive']
    subprocess.check_call(cmd)

def s3_file_download(source, dest):
    cmd = ['aws', 's3', 'cp', source, dest]
    subprocess.check_call(cmd)


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


print "Making list of biomass tiles..."
# biomass_tile_list = list_tiles()
biomass_tile_list = ['10N_080W', '40N_120E'] # test tiles
biomass_tile_list = ['10N_080W'] # test tiles
print "  Biomass tile list retrieved. There are", len(biomass_tile_list), "biomass tiles total."

# Location of the biomass tiles on s3
biomass_dir = 's3://gfw2-data/climate/WHRC_biomass/WHRC_V4/Processed/'

tcd_dir = 's3://gfw2-data/forest_cover/2000_treecover/'

# # For downloading all tiles in the input folders
# download_list = [biomass_dir, tcd_dir]
#
# for input in download_list:
#     s3_folder_download('{}'.format(input), '.')

out_locn = 's3://gfw-files/dgibbs/test_join_biomass2000_tcd2000/'

# Iterates through tiles to convert them to tsvs
for tile in biomass_tile_list:

    print "Processing tile", tile

    biomass_local = r'/home/ubuntu/data/biomass/{}_biomass.tif'.format(tile)
    tcd_local = r'/home/ubuntu/data/tcd/Hansen_GFC2014_treecover2000_{0}.tif'.format(tile)

    s3_file_download('{0}Hansen_GFC2014_treecover2000_{1}.tif'.format(tcd_dir, tile), tcd_local)  # tree cover density 2000 tile
    s3_file_download('{0}{1}_biomass.tif'.format(biomass_dir, tile), biomass_local)  # biomass 2000 tile

    biomass = '{}_biomass.tif'.format(tile)
    tcd = 'Hansen_GFC2014_treecover2000_{}.tif'.format(tile)

    ras_cwd = r'/home/ubuntu/raster-to-tsv'
    ras_to_vec_cmd = ['python', 'write-tsv.py', '--datasets', biomass_local, tcd_local, '--s3-output', out_locn]
    ras_to_vec_cmd += ['--threads', '1', '--csv-process', 'area', '--prefix', 'biomass2000_tcd2000', '--separate']

    # subprocess.check_call(ras_to_vec_cmd, cwd=ras_cwd)
    subprocess.check_call(ras_to_vec_cmd, cwd=ras_cwd)
