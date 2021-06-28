#!/usr/bin/env python
# -*- coding: utf-8 -*-

from girder.constants import AccessType
from girder.exceptions import ValidationException
from girder.models.setting import Setting

from ..constants import PluginSettings
from .annotationparameters import AnnotationParameters


def _validateInt(value):
    if not isinstance(value, int):
        value = int(value)
    return value


def _validateFloat(value):
    if not isinstance(value, float):
        value = float(value)
    return value


class RNAScopeParameters(AnnotationParameters):
    def _find(self, annotation, creator, **kwargs):
        query = {
            'annotationId': annotation['_id'],
            'creatorId': creator['_id']
        }
        existing = self.find(query, limit=2, **kwargs)
        count = existing.count()
        if count > 1:
            raise ValidationException(
                'there is more than one parameter set for annotation')
        if count:
            return existing.next()  # noqa: B305

    def getParameters(self, annotation, creator, parameters=None, **kwargs):
        self.RNASCOPE_SINGLE_VIRION_COLOR = \
            Setting().get(PluginSettings.RNASCOPE_SINGLE_VIRION_COLOR)
        self.RNASCOPE_PRODUCTIVE_INFECTION_COLOR = \
            Setting().get(PluginSettings.RNASCOPE_PRODUCTIVE_INFECTION_COLOR)
        self.RNASCOPE_AGGREGATE_VIRIONS_COLOR = \
            Setting().get(PluginSettings.RNASCOPE_AGGREGATE_VIRIONS_COLOR)
        if parameters is None:
            parameters = {}
        doc = self._find(annotation, creator)
        if doc is None:
            doc = super(RNAScopeParameters, self).createAnnotationParameters(
                annotation, creator, parameters, **kwargs)
        else:
            self.requireAccess(doc, user=creator, level=AccessType.WRITE)
            doc['parameters'].update(parameters)
            self.save(doc)
        return doc

    def createParameters(self, annotation, creator, parameters=None, **kwargs):
        doc = super(RNAScopeParameters, self).createAnnotationParameters(
            annotation, creator, parameters, **kwargs)
        return doc

    def updateParameters(self, annotation, creator, parameters=None, **kwargs):
        if parameters is None:
            parameters = {}
        doc = self._find(annotation, creator)
        if doc is None:
            doc = super(RNAScopeParameters, self).createAnnotationParameters(
                annotation, creator, parameters, **kwargs)
        else:
            self.requireAccess(doc, user=creator, level=AccessType.WRITE)
            doc['parameters'].update(parameters)
            self.save(doc)
        return doc

    def validate(self, doc):
        parameters = doc['parameters']
        parameters['pixelsPerVirion'] = _validateInt(
            parameters.get('pixelsPerVirion',
                           Setting().get(
                               PluginSettings.RNASCOPE_PIXELS_PER_VIRION)))
        parameters['pixelThreshold'] = _validateInt(
            parameters.get('pixelThreshold',
                           Setting().get(
                               PluginSettings.RNASCOPE_PIXEL_THRESHOLD)))
        parameters['roundnessThreshold'] = _validateFloat(
            parameters.get('roundnessThreshold',
                           Setting().get(
                               PluginSettings.RNASCOPE_ROUNDNESS_THRESHOLD)))

        if parameters['pixelsPerVirion'] < 1:
            raise ValidationException(
                'Pixels per virion cannot be less than 1')

        if parameters['pixelThreshold'] < 1:
            raise ValidationException(
                'Pixel threshold cannot be less than 1')

        if parameters['pixelsPerVirion'] > parameters['pixelThreshold']:
            raise ValidationException(
                'Pixels per virion cannot be greater than productive infection'
                ' threshold')
        return doc

    def classify(self, parameters, pixels, roundness):
        parameters = parameters['parameters']
        if pixels < parameters['pixelsPerVirion']:
            return 'single virion'
        elif (pixels > parameters['pixelThreshold'] and
              roundness > parameters['roundnessThreshold']):
            return 'productive infection'
        return 'aggregate virions'

    def color(self, classification):
        if classification == 'single virion':
            return self.RNASCOPE_SINGLE_VIRION_COLOR
        elif classification == 'productive infection':
            return self.RNASCOPE_PRODUCTIVE_INFECTION_COLOR
        elif classification == 'aggregate virions':
            return self.RNASCOPE_AGGREGATE_VIRIONS_COLOR


Rnascopeparameters = RNAScopeParameters
