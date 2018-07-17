import subprocess
import os
import multiprocessing

def mask_biomass(tile_id):

    print "Hello"


    print "  Masking tile..."
    out = '{}_carbon.tif'.format(tile_id)
    # warp = ['gdalwarp', '-t_srs', 'EPSG:4326', '-co', 'COMPRESS=LZW', '-tr', '0.00025', '0.00025', '-tap', '-te', xmin, ymin, xmax, ymax, '-dstnodata', '-9999', vrtname, out]
    # subprocess.check_call(warp)
    print "    Tile masked"

    print "  Copying tile to s3..."
    s3_folder = 's3://WHRC-carbon/WHRC_V4/More_than_TCD30/'
    cmd = ['aws', 's3', 'cp', out, s3_folder]
    subprocess.check_call(cmd)
    print "    Tile copied to s3"



# Location of the tiles on s3
s3_locn = 's3://WHRC-carbon/WHRC_V4/Processed/'

print "Checking if tiles are already downloaded..."

if os.path.exists('./Palearctic_MapV4_60N_010W.tif') == False:

    # Creates a list of all the tiles on s3
    print "  Copying raw tiles to spot machine..."
    s3_to_spot(s3_locn)
    print "    Raw tiles copied"

else:

    print "  Tiles already copied"