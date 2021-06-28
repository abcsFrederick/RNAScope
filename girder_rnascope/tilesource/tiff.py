import large_image_source_tiff as tiff
# from large_image.tilesource.base import GirderTileSource
from large_image_source_tiff import girder_source

from .tiff_reader import TiledTiffDirectory
tiff.TiledTiffDirectory = TiledTiffDirectory


class TiffFileTileSource(tiff.TiffFileTileSource):
    cacheName = 'tilesource'
    name = 'tifffile'


class TiffGirderTileSource(TiffFileTileSource, girder_source.TiffGirderTileSource):
    cacheName = 'tilesource'
    name = 'tiff'
