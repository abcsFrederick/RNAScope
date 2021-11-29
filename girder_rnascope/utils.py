#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bson import ObjectId
import csv
import os.path
import re

# from six import BytesIO
# from PIL import Image  # , ImageOps
# import numpy as np

# from girder import logger
from girder.models.file import File
from girder.models.folder import Folder
from girder.models.item import Item
# from girder.models.upload import Upload
from girder.models.user import User
from girder_large_image_annotation.models.annotation import Annotation
# from girder.plugins.large_image.models.annotation import Annotation
# from girder_large_image_annotation.models.annotationelement import \
#     Annotationelement
# from girder_large_image.models.image_item import ImageItem
# from large_image.tilesource.base import _encodeImage, \
#     TILE_FORMAT_IMAGE, TILE_FORMAT_PIL

from .constants import IMAGE_DIRECTORY
# from .constants import LABEL_DIRECTORY  # , LABEL_DIRECTORIES, LABEL_FILENAME
# from .constants import MASKED_IMAGE_FILENAME


# FIXME
# def read(f):
#     contents = b''
#     while True:
#         chunk = f.read(f._maximumReadSize)
#         if not chunk:
#             return contents
#         contents += chunk


# def labelImage(file_, mask=False):
#     with File().open(file_) as f:
#         if 'npy' in file_.get('exts', []):
#             i = np.load(f) == 0
#             image = np.full(i.shape, 255, np.uint8)
#             image[i] = 0
#             image = Image.fromarray(image)
#         else:
#             try:
#                 image = Image.open(BytesIO(read(f)))
#             except IOError as e:
#                 logger.error(e)
#                 return
#     if mask:
#         # maskedImage = Image.new('RGBA', image.size, color='white')
#         with File().open(mask) as f:
#             try:
#                 maskedImage = Image.open(BytesIO(read(f)))
#             except IOError as e:
#                 logger.error(e)
#                 return
#         maskedImage.putalpha(image)
#         return image, maskedImage
#     return image


# def _updateLabel(file_, mask=None, user=None, token=None):
#     result = labelImage(file_, mask=mask)
#     if mask:
#         label_, masked_ = result
#     else:
#         label_, masked_ = result, None
#     label = BytesIO()
#     label_.convert('1').save(label, format='tiff')
#     label.seek(0)

#     if masked_:
#         masked = BytesIO()
#         try:
#             masked_.save(masked, format='tiff')
#             masked.seek(0)
#         except Exception as e:
#             logger.error(e)
#             return
#     else:
#         masked = None

#     item = Item().load(file_['itemId'], force=True)
#     user = User().load(item['creatorId'], force=True)
#     ImageItem().delete(item)
#     size = label.len if hasattr(label, 'len') else label.getbuffer().nbytes
#     file = Upload().uploadFromFile(label, size=size, name=LABEL_FILENAME,
#                                    parentType='item', parent=item,
#                                    user=user, mimeType='image/tiff')
#     ImageItem().createImageItem(item, file, user=user, token=token)

#     if masked:
#         size = masked.len if hasattr(masked, 'len') else masked.getbuffer().nbytes
#         Upload().uploadFromFile(masked, size=size,
#                                 name=MASKED_IMAGE_FILENAME, parentType='item',
#                                 parent=item, user=user, mimeType='image/tiff')


# def updateLabel(file_, user=None, token=None):
#     item = Item().load(file_['itemId'], force=True)
#     name = os.path.splitext(item['name'])[0]
#     nameFilter = {'name': {'$regex': name + '\\..*'}}
#     folder = Folder().load(item['folderId'], force=True)
#     if folder['parentCollection'] != 'folder':
#         return
#     parentFolder = Folder().load(folder['parentId'], force=True)
#     labelItems = []
#     if folder['name'] == IMAGE_DIRECTORY:
#         filters = {'$or': [{'name': n} for n in LABEL_DIRECTORIES]}
#         labelFolderQuery = Folder().childFolders(parentFolder,
#                                                  folder['parentCollection'],
#                                                  user={'admin': True},
#                                                  filters=filters)
#         for labelFolder in labelFolderQuery:
#             items = Folder().childItems(labelFolder, user={'admin': True},
#                                         filters=nameFilter)
#             labelItems.extend((item, labelItem) for labelItem in items)
#     elif folder['name'] in LABEL_DIRECTORIES:
#         originalFolders = list(Folder().childFolders(parentFolder,
#                                                      folder['parentCollection'],
#                                                      user={'admin': True},
#                                                      limit=1,
#                                                      filters={'name': IMAGE_DIRECTORY}))
#         if not originalFolders:
#             return
#         items = list(Folder().childItems(originalFolders[0],
#                                          user={'admin': True},
#                                          limit=2, filters=nameFilter))
#         if not items or len(items) > 1:
#             return
#         originalItem = items[0]
#         labelItems.append((originalItem, item))
#     else:
#         return

#     for originalItem, labelItem in labelItems:
#         query = {
#             'itemId': originalItem['_id'],
#         }
#         query.update(nameFilter)
#         originalFiles = list(File().find(query, user={'admin': True}, limit=2))
#         if not originalFiles or len(originalFiles) > 1:
#             continue
#         mask = originalFiles[0]

#         query = {
#             'itemId': originalItem['_id'],
#             'name': MASKED_IMAGE_FILENAME,
#         }
#         maskedFiles = list(File().find(query, user={'admin': True}, limit=1))
#         if maskedFiles:
#             mask = None

#         query = {
#             'itemId': labelItem['_id'],
#         }
#         query.update(nameFilter)
#         imageFiles = list(File().find(query, user={'admin': True}, limit=2))
#         if not imageFiles or len(imageFiles) > 1:
#             continue

#         query = {
#             'itemId': labelItem['_id'],
#             'name': LABEL_FILENAME,
#         }
#         labelFiles = list(File().find(query, user={'admin': True}, limit=1))
#         if labelFiles:
#             continue

#         _updateLabel(imageFiles[0], mask=mask, user=user, token=token)


# def updateLabels(user=None, token=None):
#     query = {'name': IMAGE_DIRECTORY}
#     for originalFolder in Folder().find(query, user={'admin': True}):
#         for item in Folder().childItems(originalFolder, user={'admin': True}):
#             for file_ in Item().childFiles(item, user={'admin': True}):
#                 updateLabel(file_, user=user, token=token)


# def deleteLabels():
#     query = {'name': IMAGE_DIRECTORY}
#     filters = {'$or': [{'name': name} for name in LABEL_DIRECTORIES]}
#     for originalFolder in Folder().find(query, user={'admin': True}):
#         parentFolder = Folder().load(originalFolder['parentId'], force=True)
#         labelFolders = list(Folder().childFolders(parentFolder,
#                                                   originalFolder['parentCollection'],
#                                                   user={'admin': True},
#                                                   filters=filters))
#         for item in Folder().childItems(originalFolder, user={'admin': True}):
#             name = os.path.splitext(item['name'])[0]
#             nameFilter = {'name': {'$regex': name + '\\..*'}}
#             for labelFolder in labelFolders:
#                 items = Folder().childItems(labelFolder, user={'admin': True},
#                                             filters=nameFilter)
#                 for labelItem in items:
#                     query = {
#                         'itemId': labelItem['_id'],
#                         'name': MASKED_IMAGE_FILENAME,
#                     }
#                     maskedFiles = list(File().find(query, user={'admin': True}))
#                     if not maskedFiles:
#                         continue
#                     for maskedFile in maskedFiles:
#                         File().remove(maskedFile)

#                     query = {
#                         'itemId': labelItem['_id'],
#                         'name': LABEL_FILENAME,
#                     }
#                     labelFiles = list(File().find(query, user={'admin': True}))

#                     if not labelFiles:
#                         continue

#                     for labelFile in labelFiles:
#                         File().remove(labelFile)

#                     ImageItem().delete(labelItem)

def annotationUpdate(doc, item, file_, itemId):
    doc.update({
        'itemId': itemId,
        'creatorId': file_['creatorId'],
        'created': file_['created'],
        'updatedId': file_['creatorId'],
        'updated': file_.get('updated', file_['created']),
        'annotation': {
            'description': 'Generated from file %s' % file_['_id'],
            'elements': [],
            'name': os.path.splitext(file_['name'])[0],
        },
        'groups': [
            '(file generated)',
        ],
    })
    user = User().load(item['creatorId'], force=True)
    Annotation().copyAccessPolicies(src=user, dest=doc, save=False)

    with File().open(file_) as f:
        # FIXME
        contents = b''
        while True:
            chunk = f.read()
            if not chunk:
                break
            contents += chunk
        contents = contents.decode()
        doc['annotation']['description'] += \
            ' #elements: {}'.format(str(len(list(csv.DictReader(contents.splitlines())))))
        for row in csv.DictReader(contents.splitlines()):
            doc['annotation']['elements'].append({
                'label': {
                    'value': row['id'],
                },
                'center': [
                    float(row['bboxX']) + float(row['bboxWidth']) / 2,
                    float(row['bboxY']) + float(row['bboxHeight']) / 2,
                    0,
                ],
                'height': float(row['bboxHeight']),
                'width': float(row['bboxWidth']),
                'type': 'rectangle',
                'group': '(file generated)',
                'pixels': int(row['pixels']),
                'roundness': float(row['roundness']),
            })
            # if int(row['id']) == viewThreshold:
            #     doc
    return Annotation().save(doc)

def updateFileAnnotation(file_, imageIdItemIdMap=None):
    doc = Annotation().findOne({'fileId': file_['_id']})
    if doc is None:
        if file_.get('mimeType') != 'text/csv' and 'csv' not in file_.get('exts'):
            return
        doc = {'fileId': file_['_id']}
    item = Item().load(file_['itemId'], force=True)
    if imageIdItemIdMap:
        itemId = ObjectId(imageIdItemIdMap[os.path.splitext(item['name'])[0]])
    else:
        folder = Folder().load(item['folderId'], force=True)
        if folder['parentCollection'] != 'folder':
            if doc and '_id' in doc:
                Annotation().remove(doc)
            return

        parentFolder = Folder().load(folder['parentId'], force=True)
        regx = re.compile(IMAGE_DIRECTORY, re.IGNORECASE)
        wsiFolders = list(Folder().childFolders(parentFolder,
                                                folder['parentCollection'],
                                                user={'admin': True}, limit=2,
                                                filters={'name': regx}))

        if not wsiFolders or len(wsiFolders) > 1:
            if doc and '_id' in doc:
                Annotation().remove(doc)
            return

        wsiFolder = wsiFolders[0]
        wsiName = os.path.splitext(item['name'])[0]

        regx = re.compile(wsiName, re.IGNORECASE)
        wsiItems = list(Folder().childItems(wsiFolder,
                                            filters={'name': regx}))

        if not wsiItems or len(wsiItems) > 1:
            if doc and '_id' in doc:
                Annotation().remove(doc)
            return

        if file_['created'] == doc.get('created'):
            return

        itemId = wsiItems[0]['_id']
    return annotationUpdate(doc, item, file_, itemId)


def updateFileAnnotations():
    query = {'$or': [{'exts': 'csv'}, {'mimeType': 'text/csv'}]}
    for file_ in File().find(query):
        updateFileAnnotation(file_)


def deleteFileAnnotation(fileId):
    Annotation().removeWithQuery({'fileId': fileId})


def deleteFileAnnotations():
    Annotation().removeWithQuery({'fileId': {'$exists': True}})


# def getLabel(item):
#     name = os.path.splitext(item['name'])[0]
#     nameFilter = {'name': {'$regex': name + '\\..*'}}
#     folder = Folder().load(item['folderId'], force=True)
#     if folder['parentCollection'] != 'folder':
#         raise ValueError('parent collection is not a folder')
#     parentFolder = Folder().load(folder['parentId'], force=True)
#     labelFolders = Folder().childFolders(parentFolder,
#                                          folder['parentCollection'],
#                                          user={'admin': True},
#                                          filters={'name': LABEL_DIRECTORY})
#     labelFolders = list(labelFolders)
#     if not labelFolders or len(labelFolders) > 1:
#         raise ValueError('no or too many label folders')
#     labelFolder = labelFolders[0]
#     items = Folder().childItems(labelFolder, user={'admin': True},
#                                 filters=nameFilter)
#     items = list(items)
#     if not items or len(items) > 1:
#         raise ValueError('no or too many label items')
#     return items[0]


# def getAnnotationelementThumbnail(item, annotationelement, **kwargs):
#     boundingBox = Annotationelement()._boundingBox(annotationelement['element'])

#     kwargs = dict(kwargs)
#     kwargs.update({
#         'region': {
#             'left': boundingBox['lowx'],
#             'top': boundingBox['lowy'],
#             'right': boundingBox['highx'],
#             'bottom': boundingBox['highy'],
#         },
#         'output': {
#             'maxWidth': kwargs.get('width'),
#             'maxHeight': kwargs.get('height'),
#         },
#     })

#     checkAndCreate = kwargs.pop('checkAndCreate', False)
#     transparent = kwargs.pop('transparent', True)

#     padding = kwargs.pop('padding', 0) + kwargs.get('lineWidth', 1) / 2.0
#     kwargs['region']['left'] -= padding
#     kwargs['region']['top'] -= padding
#     kwargs['region']['right'] += padding
#     kwargs['region']['bottom'] += padding

#     if not kwargs.get('scale', True):
#         regionWidth = kwargs['region']['right'] - kwargs['region']['left']
#         if regionWidth < kwargs.get('width', 0):
#             padding = (kwargs.get('width', 0) - regionWidth) / 2.0
#             kwargs['region']['left'] -= padding
#             kwargs['region']['right'] += padding

#         regionHeight = kwargs['region']['bottom'] - kwargs['region']['top']
#         if regionHeight < kwargs.get('height', 0):
#             padding = (kwargs.get('height', 0) - regionHeight) / 2.0
#             kwargs['region']['top'] -= padding
#             kwargs['region']['bottom'] += padding

#     if kwargs.get('imageFill') and kwargs.get('width') and kwargs.get('height'):
#         regionWidth = kwargs['region']['right'] - kwargs['region']['left']
#         regionHeight = kwargs['region']['bottom'] - kwargs['region']['top']
#         aspectRatio = float(kwargs['width']) / float(kwargs['height'])
#         if regionWidth < regionHeight * aspectRatio:
#             padding = (regionHeight * aspectRatio - regionWidth) / 2.0
#             kwargs['region']['left'] -= padding
#             kwargs['region']['right'] += padding
#         elif regionHeight < regionWidth / aspectRatio:
#             padding = (regionWidth / aspectRatio - regionHeight) / 2.0
#             kwargs['region']['top'] -= padding
#             kwargs['region']['bottom'] += padding

#     annotationId = annotationelement['annotationId']
#     if isinstance(annotationId, ObjectId):
#         annotationId = str(annotationelement['annotationId'])

#     annotationelementId = annotationelement['_id']
#     if isinstance(annotationelementId, ObjectId):
#         annotationelementId = str(annotationelementId)

#     keydict = dict(kwargs, annotationId=annotationId,
#                    elementId=annotationelementId)

#     # TODO: fix this mess
#     format = kwargs.get('format', TILE_FORMAT_IMAGE)
#     if transparent:
#         if format == TILE_FORMAT_PIL:
#             return ImageItem().getRegion(item, **kwargs)
#         else:
#             return ImageItem()._getAndCacheImage(item, 'getRegion',
#                                                  checkAndCreate, keydict,
#                                                  **kwargs)

#     kwargs['format'] = TILE_FORMAT_PIL
#     image, mimeType = ImageItem().getRegion(item, **kwargs)
#     background = Image.new('L', image.size, 'black')
#     background.paste(image, mask=image.split()[3])
#     image = ImageOps.invert(background.convert('1').convert('L'))
#     if format == TILE_FORMAT_PIL:
#         return image, mimeType
#     kwargs['format'] = format
#     return _encodeImage(image, **kwargs)


# def createAnnotationThumbnails(annotation, **kwargs):
#     item = Item().load(annotation['itemId'], force=True)

#     # TODO: move me
#     ImageItem().removeThumbnailFiles(item)

#     kwargs = dict(kwargs, checkAndCreate=True)
#     for element in annotation['annotation'].get('elements', []):
#         annotationelement = Annotationelement().load(element['id'])
#         getAnnotationelementThumbnail(item, annotationelement, **kwargs)
