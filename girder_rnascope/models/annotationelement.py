#!/usr/bin/env python
# -*- coding: utf-8 -*-

from girder.constants import SortDir, AccessType

from girder_large_image_annotation.models.annotationelement import \
    Annotationelement as LargeImageAnnotationelement


class Annotationelement(LargeImageAnnotationelement):
    def initialize(self):
        super(Annotationelement, self).initialize()
        self.ensureIndices([
            ([
                ('annotationId', SortDir.ASCENDING),
                ('bbox.pixels', SortDir.ASCENDING),
                ('bbox.roundness', SortDir.ASCENDING),
            ], {}),
        ])
        self.exposeFields(AccessType.READ, (
            '_id', '_version', 'annotationId', 'created', 'element', 'bbox'))

    def _boundingBox(self, element):
        bbox = super(Annotationelement, self)._boundingBox(element)
        if 'pixels' in element:
            bbox['pixels'] = element['pixels']
        if 'roundness' in element:
            bbox['roundness'] = element['roundness']
        return bbox
