Notes on unit conversion throughout biomass processing

Woods Hole version 4 (June 2018) delivery data units: 
    source example: s3://WHRC-carbon/WHRC_V4/As_provided/Afrotropic_MapV4_00N_000E.tif
    values: min: 3, max: 346
    units: megagrams of biomass / hectare

gdalwarp Woods Hole tiles:
    code: gdalwarp -t_srs EPSG:4326 -co COMPRESS=LZW -tr 0.00025 0.00025 -tap -te xmin ymin xmax ymax -dstnodata -9999 vrtname out (contained in this repo)
    process: makes sure that rasters match Hansen grid (cell size + -tap) . . . sample raster appears to match but good to make sure all input data is standardized
    units: megagrams of biomass / hectare

Mask tiles by > 30% tree cover density:
    code: some gdal_calc command to multiply biomass value by 1 | 0 mask where TCD > 30 (contained in this repo)
    units: megagrams of biomass / hectare

TSV from these >30% TCD tiles:
    source example: 
    code: s3://gfw2-data/alerts-tsv/batch-processing/sam-biomass-to-tsv.zip (not in this repo)
    process: convert raster to TSV
    units: megagrams of biomass / hectare

Run Hadoop:
    code: biomass.toDouble * area of pixels in m2 / 10000.0 (10,000 is used to convert area m2 to area ha) (not in this repo)
    simplified: biomass megagrams / ha of that pixel * area ha of that pixel
    final units: megagrams of biomass / pixel

    summarized —> megagrams of biomass per polyname / iso / adm1 / adm2
    (no cumulative summing required because this is all one TCD threshold (> 30))