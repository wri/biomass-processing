Biomass processing procedures for Woods Hole Research Center version 4, deliverd June 2018:

Woods Hole version 4 delivery data units: 
    File example: s3://WHRC-carbon/WHRC_V4/As_provided/Afrotropic_MapV4_00N_000E.tif
    Units: megagrams of biomass/hectare
    Note: In the Woods Hole delivery, some tiles had their data split between multiple ecoregions. For example, 10S_120E is found in the Australia ecoregion and the Tropical Asia ecoregion, while 30N_100W is found in the Neotropic ecoregion and the Nearctic ecoregion. There were around 15 tiles with data from multiple ecoregions. In these tiles, the data from the two ecoregions are non-overlapping, i.e. where ecoregion1 says Nodata, ecoregion2 has data and vice versa.

Make WH biomass tiles match Hansen tiles:
    Code: process_Woods_Hole_biomass.py (contained in this repo)
    Process: makes sure that rasters match Hansen grid (cell size + -tap) . . . sample raster appears to match but good to make sure all input data is standardized
    Units of output tiles: megagrams of biomass/hectare
    Note: This script handles the tiles with data from multiple ecoregions. The output tiles will have the proper data from both ecoregions in the input tiles.
    
QC the processed WH tiles:
    Process: copy select input (raw from WH) and output tiles to local computer and check whether their values are the same at the same locations using identify tool in QGIS or ArcMap. Also, using gdalinfo (with -mm argument on) on select input and output tiles to make sure they have the same coordinate bounds, minimum, and maximum values.
    Note: To QC the output tiles that had multiple input tiles (i.e. in multiple ecoregions), load the output tile and all the input tiles into QGIS or ArcMap and make sure they output tiles actually cover the areas of both input tiles. Also, make sure that the output tiles' values match the values of the input tiles using the identify tool. For some reason, in QGIS the values may appear not to match when using Identify while zoomed out but they will match if you zoom in a few levels and use Identify. Also, use gdalinfo (with -mm argument on) to make sure that the coordinate bounds and minimum and maximum of the output tile matches the values in the input tiles.

Mask tiles by > 30% tree cover density:
    code: some gdal_calc command to multiply biomass value by 1 | 0 mask where TCD > 30 (contained in this repo)
    units: megagrams of biomass/hectare

TSV from these >30% TCD tiles:
    source example: 
    code: s3://gfw2-data/alerts-tsv/batch-processing/sam-biomass-to-tsv.zip (not in this repo)
    process: convert raster to TSV
    units: megagrams of biomass/hectare

Run Hadoop:
    code: biomass.toDouble * area of pixels in m2 / 10000.0 (10,000 is used to convert area m2 to area ha) (not in this repo)
    simplified: biomass megagrams/ha of that pixel * area ha of that pixel
    final units: megagrams of biomass/pixel

    summarized —> megagrams of biomass per polyname / iso / adm1 / adm2
    (no cumulative summing required because this is all one TCD threshold (> 30))
