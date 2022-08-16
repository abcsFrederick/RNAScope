#!/usr/bin/env python
import os.path
# from bson import json_util
import json
import six

from girder import plugin
from girder import events
from girder.settings import SettingDefault
from girder.constants import AccessType
from girder.exceptions import ValidationException
# from girder.models.folder import Folder
# from girder.models.item import Item
from girder.models.setting import Setting
from girder.utility import setting_utilities
from girder.utility.webroot import Webroot
from girder.utility.model_importer import ModelImporter

from girder_large_image_annotation.models.annotation import Annotation

# from girder_jobs.models.job import Job

# override TIFF tilesource
from . import tilesource  # noqa

from . import constants
from .utils import updateFileAnnotation, deleteFileAnnotation
# from .utils import updateLabel

from .rest import AnnotationResource, AnnotationParametersResource
from .rest import TilesItemResource, RNAScopeResource
# from .rest import BatchResource, ImageResource, ROIResource

from .models.annotationelement import Annotationelement
from .models.annotationparameters import AnnotationParameters
from .models import RNAScopeParameters
# from .models import Batch as BatchModel
# from .models import Image as ImageModel
# from .models import Roi as ROIModel

def onFileUpload(event):
    # print(event.info)
    reference = json.loads(event.info['reference'])
    file_ = event.info['file']
    if reference['isInfer_rnascope']:
        updateFileAnnotation(file_, reference['imageIdItemIdMap'])

def onFileSave(event):
    file_ = event.info
    updateFileAnnotation(file_)


# def onFileCreated(event):
#     file_ = event.info
#     if file_.get('itemId') is None:
#         return
#     item = Item().load(file_['itemId'], force=True)
#     folder = Folder().load(item['folderId'], force=True)
#     if folder['parentCollection'] != 'folder':
#         return
#     parentFolder = Folder().load(folder['parentId'], force=True)

#     csvFolders = list(Folder().childFolders(parentFolder,
#                                             folder['parentCollection'],
#                                             user={'admin': True}, limit=2,
#                                             filters={'name': 'csv'}))
#     if csvFolders and len(csvFolders) == 1:
#         csvFolder = csvFolders[0]
#         csvName = os.path.splitext(item['name'])[0] + '.csv'
#         csvItems = list(Folder().childItems(csvFolder,
#                                             filters={'name': csvName}))
#         if not csvItems or len(csvItems) > 1:
#             return
#         for csvFile in Item().childFiles(csvItems[0]):
#             if Annotation().findOne({'fileId': csvFile['_id']}):
#                 continue
#             updateFileAnnotation(csvFile)

#     updateLabel(file_)


def onFileRemove(event):
    deleteFileAnnotation(event.info['_id'])


# def onJobSaveAfter(event):
#     job = event.info
#     if job['type'] != 'large_image_tiff':
#         return

#     kwargs = json_util.loads(job['kwargs'])
#     if not kwargs.get('task'):
#         return

#     # FIXME: filter criteria
#     name = kwargs['inputs']['in_path']['name']
#     if os.path.splitext(name)[1].lower() not in ('.png', '.npy'):
#         return

#     path = os.path.join(os.path.dirname(__file__), 'create_tiff.py')
#     with open(path, 'r') as f:
#         kwargs['task']['script'] = f.read()

#     kwargs['task']['inputs'].append({
#         'format': 'text',
#         'id': 'compression',
#         'type': 'string',
#     })
#     kwargs['task']['inputs'].append({
#         'format': 'boolean',
#         'id': 'label',
#         'type': 'boolean',
#     })

#     kwargs['inputs']['compression'] = {
#         'data': 'lzw',
#         'format': 'text',
#         'mode': 'inline',
#         'type': 'string',
#     }
#     kwargs['inputs']['label'] = {
#         'data': True,
#         'format': 'boolean',
#         'mode': 'inline',
#         'type': 'boolean',
#     }

#     job['kwargs'] = json_util.dumps(kwargs)
#     Job().save(job, triggerEvents=False)


@setting_utilities.validator({
    constants.PluginSettings.RNASCOPE_PIXELS_PER_VIRION,
})
def validatePixelsPerVirion(doc):
    val = doc['value']
    try:
        val = int(val)
        if val < 0:
            raise ValueError
    except ValueError:
        raise ValidationException(
            'Pixels per virion must be a non-negative integer.', 'value')
    pixelThreshold = Setting().get(
        constants.PluginSettings.RNASCOPE_PIXEL_THRESHOLD)
    if pixelThreshold and val > pixelThreshold:
        raise ValidationException(
            'Pixels per virion must be less than pixel threshold.', 'value')
    doc['value'] = val


@setting_utilities.validator({
    constants.PluginSettings.RNASCOPE_PIXEL_THRESHOLD,
})
def validatePixelThreshold(doc):
    val = doc['value']
    try:
        val = int(val)
        if val < 0:
            raise ValueError
    except ValueError:
        raise ValidationException('%s must be a non-negative integer.' % (
            doc['key'], ), 'value')
    pixelsPerVirion = Setting().get(
        constants.PluginSettings.RNASCOPE_PIXELS_PER_VIRION)
    if pixelsPerVirion and val < pixelsPerVirion:
        raise ValidationException(
            'Pixel threshold must be greater than pixels per virion.', 'value')
    doc['value'] = val


@setting_utilities.validator({
    constants.PluginSettings.RNASCOPE_ROUNDNESS_THRESHOLD,
})
def validateRoundnessThreshold(doc):
    val = doc['value']
    try:
        val = float(val)
        if val < 0:
            raise ValueError
    except ValueError:
        raise ValidationException(
            'Roundness threshold must be a non-negative number.', 'value')
    doc['value'] = val


@setting_utilities.validator({
    constants.PluginSettings.RNASCOPE_SINGLE_VIRION_COLOR,
    constants.PluginSettings.RNASCOPE_PRODUCTIVE_INFECTION_COLOR,
    constants.PluginSettings.RNASCOPE_AGGREGATE_VIRIONS_COLOR,
})
def validateColorString(doc):
    val = doc['value']
    print(val)
    if not isinstance(val, six.string_types):
        raise ValueError('color string must be a string')
    doc['value'] = val


SettingDefault.defaults.update({
    constants.PluginSettings.RNASCOPE_PIXELS_PER_VIRION: 25,
    constants.PluginSettings.RNASCOPE_PIXEL_THRESHOLD: 1000,
    constants.PluginSettings.RNASCOPE_ROUNDNESS_THRESHOLD: 0.5,
    constants.PluginSettings.RNASCOPE_SINGLE_VIRION_COLOR: 'rgb(255,0,0)',
    constants.PluginSettings.RNASCOPE_PRODUCTIVE_INFECTION_COLOR:
        'rgb(0, 255, 0)',
    constants.PluginSettings.RNASCOPE_AGGREGATE_VIRIONS_COLOR:
        'rgb(0, 0, 255)',
})


class RNAScopePlugin(plugin.GirderPlugin):
    DISPLAY_NAME = 'RNAScope'
    CLIENT_SOURCE_PATH = 'web_client'

    def load(self, info):
        ModelImporter.registerModel('annotationelement', Annotationelement, 'RNAScope')
        ModelImporter.registerModel('rnascopeparameters', RNAScopeParameters, 'RNAScope')
        ModelImporter.registerModel('annotationparameters', AnnotationParameters, 'RNAScope')
        # ModelImporter.registerModel('batch', BatchModel, 'RNAScope')
        # ModelImporter.registerModel('image', ImageModel, 'RNAScope')
        # ModelImporter.registerModel('annotation', , 'RNAScope')
        # ModelImporter.registerModel('roi', ROIModel, 'RNAScope')

        Annotation().exposeFields(level=AccessType.READ, fields='fileId')

        templatePath = os.path.join(os.path.dirname(__file__), 'webroot.mako')
        info['serverRoot'].RNAScope = Webroot(templatePath)
        info['serverRoot'].RNAScope.updateHtmlVars(info['serverRoot'].vars)
        info['serverRoot'].RNAScope.updateHtmlVars({
            'pluginBrandName': 'RNAScope',
            'pluginBannerColor': '#f8f8f8',
        })
        info['apiRoot'].annotation = AnnotationResource()
        AnnotationParametersResource(info['apiRoot'])
        info['apiRoot'].RNAScope = RNAScopeResource()
        # BatchResource(info['apiRoot'])
        # ImageResource(info['apiRoot'])
        # ROIResource(info['apiRoot'])
        TilesItemResource(info['apiRoot'])

        # # create annotations from CSV if they don't already exist
        # updateCSVFiles()
        # print (info)
        events.bind('model.file.save.after', 'RNAScope', onFileSave)
        # events.bind('model.file.save.created', 'RNAScope', onFileCreated)
        events.bind('model.file.remove', 'RNAScope', onFileRemove)
        events.bind('data.process', 'RNAScope', onFileUpload)

        # events.bind('model.job.save.after', 'RNAScope', onJobSaveAfter)
