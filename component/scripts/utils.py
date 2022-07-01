import xml.etree.ElementTree as ET

import rasterio as rio
from rasterio.shutil import copy as riocopy
from rasterio.io import MemoryFile


# TODO not used until I find a way to make path of the sourcename relative
def stack_vrts(path, srcs, band=1):
    vrt_bands = []
    for srcnum, src in enumerate(srcs, start=1):
        with rio.open(src) as ras, MemoryFile() as mem:
            riocopy(ras, mem.name, driver="VRT")
            vrt_xml = mem.read().decode("utf-8")
            vrt_dataset = ET.fromstring(vrt_xml)
            for bandnum, vrt_band in enumerate(
                vrt_dataset.iter("VRTRasterBand"), start=1
            ):
                if bandnum == band:
                    vrt_band.set("band", str(srcnum))
                    vrt_bands.append(vrt_band)
                    vrt_dataset.remove(vrt_band)
    for vrt_band in vrt_bands:
        vrt_dataset.append(vrt_band)

    path.write_text(ET.tostring(vrt_dataset).decode("UTF-8"))

    return
