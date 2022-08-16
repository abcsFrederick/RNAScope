import os.path
import six

from large_image.cache_util import LruCacheMetaclass
import large_image_source_pil as pil
from large_image_source_pil import girder_source
from large_image.exceptions import TileSourceException


@six.add_metaclass(LruCacheMetaclass)
class PILFileTileSource(pil.PILFileTileSource):
    cacheName = 'tilesource'
    name = 'pilfile'

    def __init__(self, path, *args, **kwargs):
        super(PILFileTileSource, self).__init__(path, *args, **kwargs)
        # FIXME: filter criteria
        largeImagePath = self._getLargeImagePath()
        if os.path.splitext(largeImagePath)[1].lower() in ('.png', '.npy'):
            raise TileSourceException('File cannot be opened via PIL.')


class PILGirderTileSource(PILFileTileSource, girder_source.PILGirderTileSource):
    cacheName = 'tilesource'
    name = 'pilfile'
