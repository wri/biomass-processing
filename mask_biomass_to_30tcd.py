import subprocess
import os
import multiprocessing

def s3_to_spot(folder):

    dld = ['aws', 's3', 'cp', folder, '.', '--recursive']
    subprocess.check_call(dld)

def list_tiles():
    # Makes a text file of the tifs in the folder
    os.system('ls *biomass.tif > processed_biomass_tiles.txt')

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

    # The lists of unique tile names and all tile names
    return biomass_file_list


def mask_biomass_by_tcd(tile_id):

    tcd_mask = 30

    biomass_tile = '{}_biomass.tif'.format(tile_id)
    tcd_tile = 'Hansen_GFC2014_treecover2000_{}.tif'.format(tile_id)

    calc = '--calc=A*(B>{})'.format(tcd_mask)

    outname = '{0}_biomass_at_{1}tcd.tif'.format(tile_id, tcd_mask)

    out = '--outfile={}'.format(outname)

    print "Masking tile", tile_id, "..."
    cmd = ['gdal_calc.py', '-A', biomass_tile, '-B', tcd_tile,  calc, out, '--NoDataValue=-9999', '--co', 'COMPRESS=LZW']
    subprocess.check_call(cmd)
    print "    Tile masked"

    print "  Copying tile to s3..."
    s3_folder = 's3://WHRC-carbon/WHRC_V4/More_than_{}tcd/'.format(tcd_mask)
    cmd = ['aws', 's3', 'cp', outname, s3_folder]
    subprocess.check_call(cmd)
    print "    Tile copied to s3"


# Location of the biomass tiles on s3
s3_biomass_locn = 's3://WHRC-carbon/WHRC_V4/Processed/'

print "Checking if biomass tiles are already downloaded..."

if os.path.exists('./60N_010W_biomass.tif') == False:

    # Creates a list of all the tiles on s3
    print "  Copying biomass tiles to spot machine..."
    s3_to_spot(s3_biomass_locn)
    print "    Biomass tiles copied"

else:

    print "  Biomass tiles already on machine"

print "Getting list of biomass tiles..."
file_list = list_tiles()
print "  Biomass tile list retrieved. There are", len(file_list), "biomass tiles total."

# Location of the tree cover density tiles on s3
s3_tcd_locn = 's3://gfw2-data/forest_cover/2000_treecover/'

print "Checking if tree cover density tiles are already downloaded..."

if os.path.exists('./Hansen_GFC2014_treecover2000_60N_010W.tif') == False:

    # Creates a list of all the tiles on s3
    print "  Copying TCD tiles to spot machine..."
    s3_to_spot(s3_tcd_locn)
    print "    TCD tiles copied"

else:

    print "  TCD tiles already on machine"


# For a single processor
for tile in file_list:
    mask_biomass_by_tcd(tile)

# # For multiple processors
# count = multiprocessing.cpu_count()
# pool = multiprocessing.Pool(count/3)
# pool.map(mask_biomass, file_list)
