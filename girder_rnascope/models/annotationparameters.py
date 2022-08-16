#!/usr/bin/env python
# -*- coding: utf-8 -*-

from girder.constants import AccessType
from girder.models.model_base import AccessControlledModel


class AnnotationParameters(AccessControlledModel):
    def initialize(self):
        self.name = 'annotationparameters'
        self.ensureIndices([
            'annotationId',
        ])

        self.exposeFields(AccessType.READ, (
            '_id', '_version', 'annotationId', 'creatorId', 'parameters'))

    def createAnnotationParameters(self, annotation, creator, parameters, public=None):
        doc = {
            'annotationId': annotation['_id'],
            'creatorId': creator['_id'],
            'parameters': parameters,
        }

        # copy access control from the annotation
        self.copyAccessPolicies(src=annotation, dest=doc, save=False)

        if public is None:
            public = annotation.get('public', False)
        self.setPublic(doc, public, save=False)

        # give the current user admin access
        self.setUserAccess(doc, user=creator, level=AccessType.ADMIN, save=False)

        return self.save(doc)

    def validate(self, doc):
        return doc


Annotationparameters = AnnotationParameters
