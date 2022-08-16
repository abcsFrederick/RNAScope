#!/usr/bin/env python
# -*- coding: utf-8 -*-

from girder.api import access
from girder.api.describe import describeRoute, autoDescribeRoute, Description
from girder.api.rest import Resource, loadmodel, filtermodel
from girder.constants import AccessType
from girder.exceptions import ValidationException, RestException
from girder.models.setting import Setting

from .. import constants
from ..models import RNAScopeParameters
from ..utils import updateFileAnnotations, deleteFileAnnotations
# from ..utils import updateLabels, deleteLabels
# from ..utils import createAnnotationThumbnails


class RNAScopeResource(Resource):
    def __init__(self):
        super(RNAScopeResource, self).__init__()

        self.resourceName = 'RNAScope'
        # self.route('PUT', ('labels',), self.createLabels)
        # self.route('DELETE', ('labels',), self.deleteLabels)
        self.route('PUT', ('annotations',), self.createAnnotations)
        self.route('DELETE', ('annotations',), self.deleteAnnotations)
        # self.route('PUT', ('annotation', 'thumbnails', ':annotationId',),
        #            self.createAnnotationThumbnails)
        self.route('POST', ('annotation', 'parameters', ':annotationId',),
                   self.createParameters)
        self.route('PUT', ('annotation', 'parameters', ':annotationId',),
                   self.updateParameters)
        self.route('GET', ('annotation', 'parameters', ':annotationId',),
                   self.getParameters)
        self.route('DELETE', ('annotation', 'parameters', ':annotationId',),
                   self.deleteParameters)
        self.route('GET', ('settings',), self.getSettings)

    # @describeRoute(
    #     Description('Create large_image label items.')
    #     .notes('This creates jobs that process all label items.')
    # )
    # @access.admin
    # def createLabels(self, params):
    #     updateLabels(user=self.getCurrentUser(), token=self.getCurrentToken())

    # @describeRoute(
    #     Description('Delete large_image label items.')
    #     .notes('This deletes all large_image label items.')
    # )
    # @access.admin
    # def deleteLabels(self, params):
    #     deleteLabels()

    @describeRoute(
        Description('Create file based annotations.')
        .notes('This creates large_image annotations from files.')
    )
    @access.admin
    def createAnnotations(self, params):
        updateFileAnnotations()

    @describeRoute(
        Description('Delete file based annotations.')
        .notes('This deletes all large_image annotations from files.')
    )
    @access.admin
    def deleteAnnotations(self, params):
        deleteFileAnnotations()

    # @describeRoute(
    #     Description('Create thumbnail images for the annotation')
    #     .param('annotationId', 'The ID of the annotation.', paramType='path')
    #     .param('encoding', 'Thumbnail output encoding', required=False,
    #            enum=['JPEG', 'PNG', 'TIFF'], default='JPEG')
    # )
    # @access.user
    # @loadmodel(map={'annotationId': 'annotation'}, model='annotation',
    #            plugin='RNAScope', level=AccessType.WRITE)
    # @filtermodel(model='annotation', plugin='RNAScope')
    # def createAnnotationThumbnails(self, annotation, params, getElements=False):
    #     createAnnotationThumbnails(annotation, encoding=params['encoding'])
    #     return annotation

    @autoDescribeRoute(
        Description('Create an RNAScope annotation parameters.')
        .responseClass('RNAScopeParameters')
        .param('annotationId', 'The ID of the associated annotation.',
               paramType='path')
        .param('pixelsPerVirion', 'The number of pixels per virion',
               dataType='integer', required=False)
        .param('pixelThreshold',
               'The minimum number of pixels for a productive infection',
               dataType='integer', required=False)
        .param('roundnessThreshold',
               'The minimum roundness of a segment for a produtive infection',
               dataType='float', required=False)
        .errorResponse('ID was invalid.')
        .errorResponse('Write access was denied for the annotation.', 403)
    )
    @access.user
    @loadmodel(map={'annotationId': 'annotation'}, model='annotation',
               plugin='large_image', level=AccessType.WRITE, getElements=False)
    @filtermodel(model='rnascopeparameters', plugin='RNAScope')
    def createParameters(self, annotation, params):
        parameters = {k: v for k, v in params.items() if v is not None}
        try:
            return RNAScopeParameters().createParameters(annotation,
                                                         self.getCurrentUser(),
                                                         parameters)
        except ValidationException as e:
            raise RestException('Validation error: %s' % e)

    @autoDescribeRoute(
        Description('Create an RNAScope annotation parameters.')
        .responseClass('RNAScopeParameters')
        .param('annotationId', 'The ID of the associated annotation.',
               paramType='path')
        .param('pixelsPerVirion', 'The number of pixels per virion',
               dataType='integer', required=False)
        .param('pixelThreshold',
               'The minimum number of pixels for a productive infection',
               dataType='integer', required=False)
        .param('roundnessThreshold',
               'The minimum roundness of a segment for a produtive infection',
               dataType='float', required=False)
        .errorResponse('ID was invalid.')
        .errorResponse('Write access was denied for the annotation.', 403)
    )
    @access.user
    @loadmodel(map={'annotationId': 'annotation'}, model='annotation',
               plugin='large_image', level=AccessType.WRITE, getElements=False)
    @filtermodel(model='rnascopeparameters', plugin='RNAScope')
    def updateParameters(self, annotation, params):
        parameters = {k: v for k, v in params.items() if v is not None}
        try:
            return RNAScopeParameters().updateParameters(annotation,
                                                         self.getCurrentUser(),
                                                         parameters)
        except ValidationException as e:
            raise RestException('Validation error: %s' % e)

    @autoDescribeRoute(
        Description('Get RNAScope annotation parameters.')
        .responseClass('RNAScopeParameters')
        .param('annotationId', 'The ID of the associated annotation.',
               paramType='path')
        .errorResponse('ID was invalid.')
        .errorResponse('Read access was denied for the annotation.', 403)
    )
    @access.user
    @loadmodel(map={'annotationId': 'annotation'}, model='annotation',
               plugin='large_image', level=AccessType.WRITE, getElements=False)
    @filtermodel(model='rnascopeparameters', plugin='RNAScope')
    def getParameters(self, annotation, params):
        return RNAScopeParameters().getParameters(annotation,
                                                  self.getCurrentUser())

    @autoDescribeRoute(
        Description('Delete RNAScope annotation parameters.')
        .param('annotationId', 'The ID of the associated annotation.',
               paramType='path')
        .errorResponse('ID was invalid.')
        .errorResponse('Write access was denied for the annotation.', 403)
    )
    @access.user
    @loadmodel(map={'annotationId': 'annotation'}, model='annotation',
               plugin='large_image', level=AccessType.WRITE, getElements=False)
    def deleteParameters(self, annotation, params):
        creator = self.getCurrentUser()
        query = {
            'annotationId': annotation['_id'],
            'creatorId': creator['_id'],
        }
        # TODO: permissions
        RNAScopeParameters().removeWithQuery(query)

    @describeRoute(
        Description('Get settings for the RNAScope plugin.')
    )
    @access.public
    def getSettings(self, params):
        keys = [
            constants.PluginSettings.RNASCOPE_PIXELS_PER_VIRION,
            constants.PluginSettings.RNASCOPE_PIXEL_THRESHOLD,
            constants.PluginSettings.RNASCOPE_ROUNDNESS_THRESHOLD,
            constants.PluginSettings.RNASCOPE_SINGLE_VIRION_COLOR,
            constants.PluginSettings.RNASCOPE_PRODUCTIVE_INFECTION_COLOR,
            constants.PluginSettings.RNASCOPE_AGGREGATE_VIRIONS_COLOR,
        ]
        return {k: Setting().get(k) for k in keys}
