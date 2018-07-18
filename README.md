Biomass processing procedures for Woods Hole Research Center version 4, deliverd June 2018:

Woods Hole version 4 delivery data units: 
    File example: s3://WHRC-carbon/WHRC_V4/As_provided/Afrotropic_MapV4_00N_000E.tif
    Units: megagrams of biomass/hectare

Make WH biomass tiles match Hansen tils:
    Code: process_Woods_Hole_biomass.py (contained in this repo)
    Process: makes sure that rasters match Hansen grid (cell size + -tap) . . . sample raster appears to match but good to make sure all input data is standardized
    Units of output tiles: megagrams of biomass/hectare
    
QC the processed WH tiles:
    Process: copy select input (raw from WH) and output tiles to local computer and check whether their values are the same at the same locations using identify tool in QGIS or ArcMap. Also, using gdalinfo (with -mm argument on) on select input and output tiles to make sure they have the same bounds, minimum, and maximum values.

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
