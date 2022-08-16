#!/usr/bin/env python
# -*- coding: utf-8 -*-

from girder.api import access
from girder.api.describe import describeRoute, Description
from girder.api.rest import loadmodel  # , setRawResponse, setResponseHeader
from girder.constants import AccessType
# from girder.exceptions import RestException

# from large_image.exceptions import TileGeneralException
from girder_large_image.rest.tiles import TilesItemResource as \
    LargeImageTilesItemResource
from girder_large_image.rest.tiles import \
    ItemResource  # , ImageMimeTypes, _adjustParams
# from large_image.tilesource.base import _encodeImage, \
#     TILE_FORMAT_PIL

# from ..models.label_image_item import LabelImageItem
from ..models.annotationelement import Annotationelement
# from ..utils import getLabel
# from ..utils import getAnnotationelementThumbnail


class TilesItemResource(LargeImageTilesItemResource):
    def __init__(self, apiRoot):
        super(ItemResource, self).__init__()

        self.resourceName = 'item'
        # apiRoot.item.route('GET', (':itemId', 'tiles', 'region', 'label'),
        #                    self.getTilesRegion)
        # apiRoot.item.route('GET', (':itemId', 'tiles', 'annotationelement',
        #                            'thumbnail', ':id',),
        #                    self.getAnnotationElementThumbnail)
        apiRoot.item.route('GET', (':itemId', 'tiles', 'annotationelement',
                                   'bbox', ':id',),
                           self.getAnnotationElementBoundingBox)
        # Cache the model singleton
        # self.imageItemModel = LabelImageItem()

    # @describeRoute(
    #     Description('Get an annotation by id.')
    #     .param('itemId', 'The ID of the item.', paramType='path')
    #     .param('id', 'The ID of the annotation element.', paramType='path')
    #     .param('label', 'Use the label image thumbnail', required=False,
    #            dataType='boolean')
    #     .param('labeled', 'Overlay the label image on the thumbnail',
    #            required=False, dataType='boolean')
    #     .param('transparent', 'Label image with alpha channel', required=False,
    #            dataType='boolean', default=False)
    #     .param('width', 'The maximum width of the thumbnail in pixels.',
    #            required=False, dataType='int')
    #     .param('height', 'The maximum height of the thumbnail in pixels.',
    #            required=False, dataType='int')
    #     .param('fill', 'A fill color.  If width and height are both specified '
    #            'and fill is specified and not "none", the output image is '
    #            'padded on either the sides or the top and bottom to the '
    #            'requested output size.  Most css colors are accepted.',
    #            required=False)
    #     .param('frame', 'For multiframe images, the 0-based frame number.  '
    #            'This is ignored on non-multiframe images.', required=False,
    #            dataType='int')
    #     .param('padding', 'Padding for annotation thumbnail', required=False,
    #            dataType='int')
    #     .param('scale', 'Scale up region of annotation thumbnail',
    #            required=False, dataType='boolean')
    #     .param('imageFill', 'Preserve aspect ratio of annotaion thumbnail',
    #            required=False, dataType='boolean')
    #     .param('encoding', 'Thumbnail output encoding', required=False,
    #            enum=['JPEG', 'PNG', 'TIFF'], default='JPEG')
    #     .param('contentDisposition', 'Specify the Content-Disposition response '
    #            'header disposition-type value.', required=False,
    #            enum=['inline', 'attachment'])
    #     .produces(ImageMimeTypes)
    # )
    # @access.public(cookie=True)
    # @loadmodel(model='item', map={'itemId': 'item'}, level=AccessType.READ)
    # @loadmodel(model='annotationelement', plugin='RNAScope')
    # def getAnnotationElementThumbnail(self, item, annotationelement, params):
    #     _adjustParams(params)
    #     params = self._parseParams(params, True, [
    #         ('label', bool),
    #         ('labeled', bool),
    #         ('transparent', bool),
    #         ('width', int),
    #         ('height', int),
    #         ('fill', str),
    #         ('frame', int),
    #         ('padding', int),
    #         ('scale', bool),
    #         ('imageFill', bool),
    #         ('jpegQuality', int),
    #         ('jpegSubsampling', int),
    #         ('tiffCompression', str),
    #         ('encoding', str),
    #         ('contentDisposition', str),
    #     ])
    #     if params.pop('labeled', False):
    #         labelItem = getLabel(item)
    #         label, _ = getAnnotationelementThumbnail(labelItem,
    #                                                  annotationelement,
    #                                                  transparent=False,
    #                                                  format=TILE_FORMAT_PIL,
    #                                                  **params)
    #         image, _ = getAnnotationelementThumbnail(item, annotationelement,
    #                                                  format=TILE_FORMAT_PIL,
    #                                                  **params)
    #         image.putalpha(label)
    #         result = _encodeImage(image, **params)
    #     else:
    #         if params.pop('label', False):
    #             item = getLabel(item)
    #         try:
    #             result = getAnnotationelementThumbnail(item, annotationelement,
    #                                                    **params)
    #         except TileGeneralException as e:
    #             raise RestException(e.args[0])
    #         except ValueError as e:
    #             raise RestException('Value Error: %s' % e.args[0])
    #     if not isinstance(result, tuple):
    #         return result
    #     thumbData, thumbMime = result
    #     self._setContentDisposition(
    #         item, params.get('contentDisposition'), thumbMime, 'thumbnail')
    #     setResponseHeader('Content-Type', thumbMime)
    #     setRawResponse()
    #     return thumbData

    @describeRoute(
        Description('Get an annotation by id.')
        .param('itemId', 'The ID of the item.', paramType='path')
        .param('id', 'The ID of the annotation element.', paramType='path')
    )
    @access.public(cookie=True)
    @loadmodel(model='item', map={'itemId': 'item'}, level=AccessType.READ)
    @loadmodel(model='annotationelement', plugin='RNAScope')
    def getAnnotationElementBoundingBox(self, item, annotationelement, params):
        return Annotationelement()._boundingBox(annotationelement['element'])
