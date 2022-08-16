from large_image.tilesource import AvailableTileSources

from .pil import PILFileTileSource, PILGirderTileSource
from .tiff import TiffFileTileSource, TiffGirderTileSource

AvailableTileSources['pilfile'] = PILFileTileSource
AvailableTileSources['pil'] = PILGirderTileSource
AvailableTileSources['tifffile'] = TiffFileTileSource
AvailableTileSources['tiff'] = TiffGirderTileSource
