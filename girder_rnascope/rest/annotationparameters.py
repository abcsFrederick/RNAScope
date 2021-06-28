#!/usr/bin/env python
# -*- coding: utf-8 -*-

from girder.api import access
from girder.api.describe import describeRoute, Description
from girder.api.rest import loadmodel, filtermodel
from girder.constants import AccessType
from girder.exceptions import ValidationException, RestException
from girder.models.user import User

from girder_large_image_annotation.models.annotation import Annotation

from ..models.annotationparameters import AnnotationParameters
from ..rest import AnnotationResource


class AnnotationParametersResource(AnnotationResource):
    def __init__(self, apiRoot):
        super(AnnotationResource, self).__init__()

        self.resourceName = 'annotation'
        apiRoot.annotation.route('POST', (':annotationId', 'parameters'),
                                 self.createParameters)
        apiRoot.annotation.route('GET', (':annotationId', 'parameters'),
                                 self.find)
        apiRoot.annotation.route('PUT', (':annotationId', 'parameters', ':id'),
                                 self.updateParameters)
        apiRoot.annotation.route('DELETE', (':annotationId', 'parameters',
                                            ':id'), self.deleteParameters)

    @describeRoute(
        Description('Create an annotation parameters.')
        .responseClass('AnnotationParameters')
        .param('annotationId', 'The ID of the associated annotation.',
               paramType='path')
        .param('body', 'A JSON object containing the annotation parameters.',
               paramType='body')
        .errorResponse('ID was invalid.')
        .errorResponse('Write access was denied for the annotation.', 403)
        .errorResponse('Invalid JSON passed in request body.')
    )
    @access.user
    @loadmodel(map={'annotationId': 'annotation'}, model='annotation',
               plugin='large_image', level=AccessType.WRITE)
    @filtermodel(model='annotationparameters', plugin='RNAScope')
    def createParameters(self, annotation, params):
        try:
            return AnnotationParameters().createAnnotationParameters(
                annotation, self.getCurrentUser(), self.getBodyJson())
        except ValidationException as e:
            raise RestException('Validation error: %s' % e)

    @describeRoute(
        Description('Search for annotation parameters.')
        .responseClass('AnnotationParameters')
        .param('annotationId', 'List all annotations in this annotation.',
               paramType='path')
        .param('userId',
               'List all annotation parameters created by this user.',
               required=False)
        .errorResponse()
        .errorResponse('Read access was denied on the parent annotation.', 403)
    )
    @access.public
    @filtermodel(model='annotationparameters', plugin='RNAScope')
    def find(self, annotationId, params):
        limit, offset, sort = self.getPagingParameters(params)
        query = {}
        annotation = Annotation().load(annotationId, force=True)
        Annotation().requireAccess(
            annotation, user=self.getCurrentUser(), level=AccessType.READ)
        query['annotationId'] = annotation['_id']
        if 'userId' in params:
            user = User().load(
                params.get('userId'), user=self.getCurrentUser(),
                level=AccessType.READ)
            query['creatorId'] = user['_id']
        annotationparameters = list(
            AnnotationParameters().filterResultsByPermission(
                cursor=AnnotationParameters().find(query, sort=sort),
                user=self.getCurrentUser(), level=AccessType.READ,
                limit=limit, offset=offset))
        return annotationparameters

    @describeRoute(
        Description('Update an annotation parameters or move it to a different annotation.')
        .param('annotationId', 'Pass this to move the annotation parameter to a new annotation.',
               paramType='path')
        .param('id', 'The ID of the annotation parameters.', paramType='path')
        .param('body', 'A JSON object containing the annotation parameters.',
               paramType='body', required=False)
        .errorResponse('Write access was denied for the item.', 403)
        .errorResponse('Invalid JSON passed in request body.')
    )
    @access.user
    @loadmodel(model='annotationparameters', plugin='RNAScope', level=AccessType.WRITE)
    @filtermodel(model='annotationparameters', plugin='RNAScope')
    def updateParameters(self, annotationId, annotationparameters, params):
        user = self.getCurrentUser()
        annotation = Annotation().load(annotationparameters.get('annotationId'), force=True)
        if annotation is not None:
            Annotation().requireAccess(
                annotation, user=user, level=AccessType.WRITE)
        annotationparameters['parameters'] = self.getBodyJson()
        if annotationId != annotation['_id']:
            newannotation = Annotation().load(annotationId, force=True)
            Annotation().requireAccess(
                newannotation, user=user, level=AccessType.WRITE)
            annotationparameters['annotationId'] = newannotation['_id']
        try:
            annotationparameters = \
                AnnotationParameters().save(annotationparameters)
        except ValidationException as e:
            raise RestException('Validation error: %s' % e)
        return annotationparameters

    @describeRoute(
        Description('Delete an annotation parameters.')
        .param('annotationId', 'The ID of the associated annotation.',
               paramType='path')
        .param('id', 'The ID of the annotation parameters.', paramType='path')
        .errorResponse('ID was invalid.')
        .errorResponse('Write access was denied for the annotation parameters.', 403)
    )
    @access.user
    @loadmodel(model='annotationparameters', plugin='RNAScope',
               level=AccessType.WRITE)
    def deleteParameters(self, annotationId, annotationparameters, params):
        if annotationId != str(annotationparameters.get('annotationId')):
            raise RestException('non-matching annotation ID specified')
        # Ensure that we have write access to the parent annotation
        annotation = Annotation().load(annotationId, force=True)
        if annotation is not None:
            Annotation().requireAccess(
                annotation, user=self.getCurrentUser(), level=AccessType.WRITE)
        AnnotationParameters().remove(annotationparameters)
