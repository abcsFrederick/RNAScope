#!/usr/bin/env python
# -*- coding: utf-8 -*-
# import time
import json
import ujson

import cherrypy

from girder.api import access
from girder.api.rest import setResponseHeader
from girder.constants import AccessType
from girder.exceptions import ValidationException, RestException
from girder.utility import JsonEncoder
from girder.api.describe import describeRoute, Description
from girder.api.rest import filtermodel

import girder_large_image_annotation.models.annotation as annotation_module
from girder_large_image_annotation.models.annotation import Annotation
from girder_large_image_annotation.rest.annotation import AnnotationResource as \
    LargeImageAnnotationResource

from ..models.annotationelement import Annotationelement
from ..models.rnascopeparameters import RNAScopeParameters


annotation_module.Annotation.baseFields = \
    annotation_module.Annotation.baseFields + ('fileId',)

annotation_module.Annotationelement = Annotationelement
rectangleShapeSchema = annotation_module.AnnotationSchema.rectangleShapeSchema
rectangleShapeSchema['allOf'][-1]['properties'].update({
    'exclude': {
        'type': 'boolean'
    },
    'pixels': {
        'type': 'number',
        'minimum': 0
    },
    'roundness': {
        'type': 'number',
        'minimum': 0
    },
})


class AnnotationResource(LargeImageAnnotationResource):
    @describeRoute(
        Description('Search for annotations.')
        .responseClass('Annotation')
        .param('itemId', 'List all annotations in this item.', required=False)
        .param('userId', 'List all annotations created by this user.',
               required=False)
        .param('text', 'Pass this to perform a full text search for '
               'annotation names and descriptions.', required=False)
        .param('name', 'Pass to lookup an annotation by exact name match.',
               required=False)
        .pagingParams(defaultSort='lowerName')
        .errorResponse()
        .errorResponse('Read access was denied on the parent item.', 403)
    )
    @access.public
    @filtermodel(model='annotation', plugin='large_image')
    def find(self, params):
        annotations = super().find(params)
        # for annotation in annotations:
        #     if '(file generated)' not in annotation['groups']:
        #         continue
        #     user = self.getCurrentUser()
        #     parameters = RNAScopeParameters().getParameters(annotation, user)
        #     groups = set()

        #     for element in Annotationelement().yieldElements(annotation):
        #         element['bbox'] = Annotationelement()._boundingBox(element)
        #         pixels = element['bbox']['pixels']
        #         roundness = element['bbox']['roundness']
        #         element['group'] = RNAScopeParameters().classify(parameters,
        #                                                          pixels,
        #                                                          roundness)
        #         groups.add(element['group'])
        #         element['lineColor'] = \
        #             RNAScopeParameters().color(element['group'])
        #     annotation['groups'] = list(groups)
        return annotations

    # FIXME: copypasta, but it's too much trouble extend
    def _getAnnotation(self, user, id, params):
        """
        Get a generator function that will yield the json of an annotation.

        :param user: the user that needs read access on the annoation and its
            parent item.
        :param id: the annotation id.
        :param params: paging and region parameters for the annotation.
        :returns: a function that will return a generator.
        """
        annotation = Annotation().load(
            id, region=params, user=user, level=AccessType.READ, getElements=False)
        if annotation is None:
            raise RestException('Annotation not found', 404)
        # Ensure that we have read access to the parent item.  We could fail
        # faster when there are permissions issues if we didn't load the
        # annotation elements before checking the item access permissions.
        #  This had been done via the filtermodel decorator, but that doesn't
        # work with yielding the elements one at a time.
        annotation = Annotation().filter(annotation, self.getCurrentUser())

        groups = None
        parameters = None
        if '(file generated)' in annotation['groups']:
            groups = set(annotation.pop('groups'))
            groups.remove('(file generated)')
            user = self.getCurrentUser()
            parameters = RNAScopeParameters().getParameters(annotation, user)

        annotation['annotation']['elements'] = []
        breakStr = b'"elements": ['
        base = json.dumps(annotation, sort_keys=True, allow_nan=False,
                          cls=JsonEncoder).encode('utf8').split(breakStr)

        def generateResult():
            info = {}
            idx = 0
            yield base[0]
            yield breakStr
            collect = []
            for element in Annotationelement().yieldElements(annotation, params, info):
                # The json conversion is fastest if we use defaults as much as
                # possible.  The only value in an annotation element that needs
                # special handling is the id, so cast that ourselves and then
                # use a json encoder in the most compact form.
                element['id'] = str(element['id'])

                # FIXME: begin add bounding box
                if None not in (groups, parameters):
                    element['bbox'] = Annotationelement()._boundingBox(element)
                    pixels = element['bbox']['pixels']
                    roundness = element['bbox']['roundness']
                    element['group'] = RNAScopeParameters().classify(parameters,
                                                                     pixels,
                                                                     roundness)
                    groups.add(element['group'])
                    element['lineColor'] = \
                        RNAScopeParameters().color(element['group'])
                # FIXME: end add bounding box

                # Use ujson; it is much faster.  The standard json library
                # could be used in its most default mode instead like so:
                #   result = json.dumps(element, separators=(',', ':'))
                # Collect multiple elements before emitting them.  This
                # balances using less memoryand streaming right away with
                # efficiency in dumping the json.  Experimentally, 100 is
                # significantly faster than 10 and not much slower than 1000.
                collect.append(element)
                if len(collect) >= 100:
                    yield (b',' if idx else b'') + ujson.dumps(collect).encode('utf8')[1:-1]
                    idx += 1
                    collect = []
            if len(collect):
                yield (b',' if idx else b'') + ujson.dumps(collect).encode('utf8')[1:-1]
            yield base[1].rstrip().rstrip(b'}')
            if groups is not None:
                yield b', "groups": '
                yield json.dumps(list(groups), sort_keys=True, allow_nan=False,
                                 cls=JsonEncoder).encode('utf8')
            yield b', "_elementQuery": '
            yield json.dumps(
                info, sort_keys=True, allow_nan=False, cls=JsonEncoder).encode('utf8')
            yield b'}'

        setResponseHeader('Content-Type', 'application/json')
        return generateResult

    def updateAnnotation(self, *args, **kwargs):
        annotation = Annotation().load(kwargs['id'], force=True)
        user = self.getCurrentUser()
        Annotation().requireAccess(annotation, user=user,
                                   level=AccessType.WRITE)
        if annotation.get('fileId'):
            elements = annotation.get('annotation', {}).get('elements')
            if not (elements and cherrypy.request.body.length):
                return annotation
            newElements = self.getBodyJson().get('elements', [])
            exclude = [e['id'] for e in newElements if e.get('exclude')]
            groups = {e['id']: e['group'] for e in newElements}
            for element in elements:
                if element['id'] in exclude:
                    element['exclude'] = True
                else:
                    element.pop('exclude', None)
            try:
                annotation = Annotation().updateAnnotation(annotation,
                                                           updateUser=user)
            except ValidationException as exc:
                raise RestException(
                    "Validation Error: JSON doesn\'t follow schema (%r)." %
                    (exc.args,))
            for element in elements:
                element['group'] = groups.get(element['id'], element['group'])
            annotation['groups'] = list(set(groups.values()))
            return annotation
        return super(AnnotationResource, self).updateAnnotation(*args,
                                                                **kwargs)
