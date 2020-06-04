# Converts the aboveground biomass 2000 tiles to aboveground CO2 emissions tiles (tons CO2/hectare)
# wherever there is a Hansen loss pixel.

# Example run code:
#  python mp_biomass_to_emissions.py -b s3://gfw2-data/climate/WHRC_biomass/WHRC_V4/Processed/ -l s3://gfw2-data/forest_change/hansen_2018/ -o s3://gfw2-data/climate/Hansen_emissions/2018_loss/ -y 2019

import subprocess
import argparse
import multiprocessing
import utilities
from multiprocessing.pool import Pool
from functools import partial
import emissions_per_hectare
import emissions_per_pixel
from osgeo import gdal

## Actually masks the biomass tiles by tree cover density
def main():

    parser = argparse.ArgumentParser(description='Convert WHRC biomass 2000/ha to CO2/ha masked by Hansen loss')
    parser.add_argument('--biomass', '-b', required=True,
                        help='WHRC aboveground biomass in 2000/ha to use as basis for CO2')
    parser.add_argument('--loss-year', '-l', required=True,
                        help='Hansen loss for 2001 to present year')
    parser.add_argument('--output-dir', '-o', required=True,
                        help='Output s3 directory for CO2/ha masked by Hansen loss')
    parser.add_argument('--year', '-y', required=True,
                       help='Maximum tree cover loss year')
    args = parser.parse_args()

    biomass_dir = args.biomass
    loss_dir = args.loss_year
    out_dir = args.output_dir
    max_year = args.year

    # # Copies tree loss tiles to spot machine
    # print "  Copying loss tiles to spot machine..."
    # utilities.s3_to_spot(loss_dir)
    # print "    Loss tiles copied"

    print "Getting list of loss tiles..."
    loss_file_list = utilities.list_tiles(loss_dir)
    print loss_file_list
    print "  Loss tile list retrieved. There are", len(loss_file_list), "loss tiles total."

    # # Copies biomass tiles in the s3 folder
    # print "  Copying biomass tiles to spot machine..."
    # utilities.s3_to_spot(biomass_dir)
    # print "    Biomass tiles copied"

    print "Getting list of biomass tiles..."
    biomass_file_list = utilities.list_tiles(biomass_dir)
    print biomass_file_list
    print "  Loss tile list retrieved. There are", len(biomass_file_list), "loss tiles total."

    # In order to be processed, a tile must have both loss and biomass.
    # There are some tiles that have only one of those.
    # This creates a list of tiles that have loss and biomass.
    shared_tile_list = list(set(biomass_file_list).intersection(loss_file_list))
    print "  List of tiles with both biomass and loss retrieved. There are", len(shared_tile_list), "shared tiles total."

    # # Copies biomass tiles in the s3 folder
    # print "  Copying pixel area tiles to spot machine..."
    # utilities.s3_to_spot('s3://gfw2-data/analyses/area_28m/')
    # print "    Biomass tiles copied"

    # # Peaks at about 180 GB, which is fine on an m4.16xlarge machine
    # num_of_processes = 22
    # pool = Pool(num_of_processes)
    # pool.map(partial(emissions_per_hectare.biomass_to_emissions_ha, out_dir=out_dir, max_year=max_year), shared_tile_list)
    # pool.close()
    # pool.join()

    # This uses just about X GB, which is fine on an m4.16xlarge machine
    num_of_processes = 15
    pool = Pool(num_of_processes)
    pool.map(partial(emissions_per_pixel.emissions_per_pixel, out_dir=out_dir, max_year=max_year), shared_tile_list)
    pool.close()
    pool.join()


if __name__ == '__main__':
    main()
