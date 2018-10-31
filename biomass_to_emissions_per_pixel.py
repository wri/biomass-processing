# Converts the aboveground biomass 2000 tiles to aboveground CO2 emissions tiles (tons CO2/pixel)
# wherever there is a Hansen loss pixel.

import subprocess
import os
import multiprocessing
from osgeo import gdal

# Copies the tiles in the s3 folder to the spot machine
def s3_to_spot(folder):

    dld = ['aws', 's3', 'cp', folder, '.', '--recursive']
    subprocess.check_call(dld)


# Lists all the tiles on the spot machine
def list_tiles():

    # Makes a text file of the tifs in the folder on the spot machine
    os.system('ls *tCO2_ha.tif > spot_emis_tiles.txt')

    # List for the tile names
    file_list = []

    # Iterates through the text file to get the names of the tiles and appends them to list
    with open('spot_emis_tiles.txt', 'r') as tile:
        for line in tile:
            # Extracts the tile name from the file name
            tile_short = line[0:8]

            file_list.append(tile_short)

    # The lists of unique tile names and all tile names
    return file_list

# Converts aboveground biomass per hectare to emissions from aboveground biomass per hectare
def emissions_per_pixel(tile_id):

    m2_per_ha = 100*100

    # Names of the input biomass and TCD tiles
    emis_ha_tile = '{}_tCO2_ha_AGB_masked_by_loss.tif'.format(tile_id)
    area_tile = 'hanson_2013_area_{}.tif'.format(tile_id)

    # Output file name
    outname = '{}_tCO2_pixel_AGB_masked_by_loss.tif'.format(tile_id)

    # Equation argument for masking biomass below TCD threshold
    calc = '--calc=A*B/{}'.format(m2_per_ha)

    # Argument for outputting file
    out = '--outfile={}'.format(outname)

    print "Converting from tons CO2/ha to tons CO2/pixel..."
    cmd = ['gdal_calc.py', '-A', emis_ha_tile, '-B', area_tile,  calc, out, '--NoDataValue=0', '--co', 'COMPRESS=LZW', '--overwrite']
    subprocess.check_call(cmd)
    print "  Emissions calculated"

    print "Copying tile to s3..."
    s3_folder = 's3://gfw2-data/climate/Hansen_emissions/2017_loss/per_pixel/'
    cmd = ['aws', 's3', 'cp', outname, s3_folder]
    subprocess.check_call(cmd)
    print "  Tile copied to s3"


### Converts emissions from per hectare to per pixel

# Location of the emissions/ha tiles on s3
s3_emiss_ha_locn = 's3://gfw2-data/climate/Hansen_emissions/2017_loss/per_hectare/'

# Location of the pixel area tiles on s3
s3_area_locn = 's3://gfw2-data/analyses/area_28m/'

# List of tiles to download
downloads = [s3_emiss_ha_locn, s3_area_locn]

print "  Copying tiles to spot machine"
for data in downloads:
    s3_to_spot(data)
print "    Tiles copied to spot machine"

print "Getting list of biomass tiles..."
emis_file_list = list_tiles()
print "  Biomass tile list retrieved. There are", len(emis_file_list), "biomass tiles total."

# For multiple processors
count = multiprocessing.cpu_count()
pool = multiprocessing.Pool(count/3)
pool.map(emissions_per_pixel, emis_file_list)

# # For a single processor
# for tile in emis_file_list:
#     emissions_per_pixel(tile)
