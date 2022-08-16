from girder import logger

from large_image_source_tiff import tiff_reader

try:
    from libtiff import libtiff_ctypes
except ValueError as exc:
    logger.warn('Failed to import libtiff; try upgrading the python module (%s)' % exc)
    raise ImportError(str(exc))
try:
    import PIL.Image
except ImportError:
    raise
    PIL = None


class TiledTiffDirectory(tiff_reader.TiledTiffDirectory):
    def _validate(self):
        validateExceptions = (
            'Only uncompressed and JPEG compressed TIFF files are supported',
            'Only RGB and greyscale TIFF files are supported'
        )
        try:
            return super(TiledTiffDirectory, self)._validate()
        except tiff_reader.ValidationTiffException as e:
            if e.args and e.args[0] not in validateExceptions:
                raise

        if (not self._tiffInfo.get('istiled') or
                not self._tiffInfo.get('tilewidth') or
                not self._tiffInfo.get('tilelength')):
            raise tiff_reader.ValidationTiffException('Only tiled TIFF files are supported')

    def getTile(self, x, y):
        exception = ValueError('Unsupported TIFF file')
        try:
            tile = super(TiledTiffDirectory, self).getTile(x, y)
        except Exception as e:
            tile = None
            exception = e

        if tile is not None:
            return tile

        compression_types = (
            libtiff_ctypes.COMPRESSION_NONE,
            libtiff_ctypes.COMPRESSION_ADOBE_DEFLATE,
            libtiff_ctypes.COMPRESSION_LZW
        )
        if self._tiffInfo.get('compression') in compression_types:
            tile_plane = self._tiffFile.read_one_tile(x * self._tileHeight,
                                                      y * self._tileWidth)
            return PIL.Image.fromarray(tile_plane)

        raise exception
