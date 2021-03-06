### Biomass processing procedures for Woods Hole Research Center version 4, delivered June 2018:

Woods Hole version 4 delivery: 
   - File example: s3://gfw2-data/climate/WHRC_biomass/WHRC_V4/As_provided/Afrotropic_MapV4_00N_000E.tif
   - Units: megagrams of biomass/hectare
   - Note: In the Woods Hole delivery, some tiles had their data split between multiple ecoregions. For example, 10S_120E is found in the Australia ecoregion and the Tropical Asia ecoregion, while 30N_100W is found in the Neotropic ecoregion and the Nearctic ecoregion. There were around 15 tiles with data from multiple ecoregions. In these tiles, the data from the two ecoregions are non-overlapping, i.e. where ecoregion1 says Nodata, ecoregion2 has data and vice versa.
    
Make WH biomass tiles match Hansen tiles:
   - Code: process_Woods_Hole_biomass.py (contained in this repo)
   - Process: Makes sure that rasters match Hansen grid (cell size + -tap)... Sample delivered raster appears to match but good to make sure all input data is standardized. This only outputs exports to s3 tiles that have data in them.
   - Units of output tiles: megagrams of biomass/hectare
   - Note: This script handles the tiles with data from multiple ecoregions. The output tiles will have the proper data from both ecoregions in the input tiles.
    
QC the processed WH tiles:
   - Process: Copy select input (raw from WH) and output tiles to local computer and check whether their values are the same at the same locations using identify tool in QGIS or ArcMap. Also, using gdalinfo (with -mm argument on) on select input and output tiles to make sure they have the same coordinate bounds, minimum, and maximum values.
   - Note: To QC the output tiles that had multiple input tiles (i.e. in multiple ecoregions), load the output tile and all the input tiles into QGIS or ArcMap and make sure they output tiles actually cover the areas of both input tiles. Also, make sure that the output tiles' values match the values of the input tiles using the identify tool. For some reason, in QGIS the values may appear not to match when using Identify while zoomed out but they will match if you zoom in a few levels and use Identify. Also, use gdalinfo (with -mm argument on) to make sure that the coordinate bounds and minimum and maximum of the output tile matches the values in the input tiles.

Mask tiles by > 30% tree cover density:
   - Code: mask_biomass_by_tcd.py (contained in this repo)
   - Process: Masks the biomass tiles to whatever the input TCD is (generally 30%). Biomass pixels on TCD pixels <30% will get NoData values of 0. Tiles that have no biomass pixels with values (no TCD>30) do not get saved to s3.
   - Units of output tiles: megagrams of biomass/hectare
	
QC the TCD-masked WH tiles:
   - Process: Copy select input (processed) and output (masked) tiles, raw Woods Hole tiles, and UMD tree cover density tiles to local computer and load in QGIS or ArcMap. Check whether the values of the masked tiles are the same as the values of the raw Woods Hole tiles except where TCD pixels are less than the input amount. Make sure that where TCD < threshold, the masked tiles show NoData values.

Run Hadoop:
    code: biomass.toDouble * area of pixels in m2 / 10000.0 (10,000 is used to convert area m2 to area ha) (not in this repo)
    simplified: biomass megagrams/ha of that pixel * area ha of that pixel
    final units: megagrams of biomass/pixel

    summarized —> megagrams of biomass per polyname / iso / adm1 / adm2
    (no cumulative summing required because this is all one TCD threshold (> 30))

Convert aboveground WHRC biomass to tCO2 emissions/hectare:
   - Code: biomass_to_emissions.py (contained in this repo)
   - Run it on an m4.16xlarge AWS spot machine
   - Process: It masks WHRC biomass 2000 tiles to Hansen loss pixels and converts those pixels from biomass to emissions
   - This script has three command line arguments: input aboveground biomass s3 folder (`--biomass`), Hansen loss s3 folder (`--loss-year`), and output s3 folder (`--output-dir`).
   - Example code is `python biomass_to_emissions_per_hectare.py -b s3://gfw2-data/climate/WHRC_biomass/WHRC_V4/Processed/ -l s3://gfw2-data/forest_change/hansen_2018/ -o s3://gfw2-data/climate/Hansen_emissions/2018_loss/per_hectare/`
   - Units of output tiles: tCO2/hectare
   - Note: This should be run every time a new Hansen loss year is delivered
   - Note: It is not used for further analyses at this point; it is just for putting on the Open Data Portal for people to download
   
QC the conversion to emissions/ha:
   - Process: Loaded sample biomass 2000, Hansen loss, and output tiles into ArcMap and checked whether the output pixels had the right value and were showing up only where there were both biomass and loss pixels.
   - Process: Loaded sample biomass 2000 and Hansen tiles that didn't have output emissions tiles and confirmed that those tiles did not have any pixels with both biomass and loss.
      
Convert aboveground tCO2/ha emissions to tCO2/pixel emissions:
   - Code: biomass_to_emissions.py (contained in this repo)
   - Process: It uses a raster of the area of each pixel in m2 to convert emissions from ha to pixel
   - It runs in the same script as the creation of the emissions per hectare. This should not be run separately.
   - Units of output tiles: tCO2/pixel
   - Note: This should be run every time a new Hansen loss year is delivered
   - Note: It is not used for further analyses at this point; it is just for putting on the Open Data Portal for people to download. It is made available for people to use for zonal statistics, being better for that than emissions/ha (easier to sum).
   
QC the emissions conversion:
   - Process: Loaded emissions/ha and area rasters into ArcMap for two tiles and checked the arithmetic for a few pixels in each tile.