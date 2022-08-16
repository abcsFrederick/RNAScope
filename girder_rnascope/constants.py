#!/usr/bin/env python
# -*- coding: utf-8 -*-

LABEL_DIRECTORY = 'label'  # 'relabel'
IMAGE_DIRECTORY = '.*wsi.*'
LABEL_DIRECTORIES = [
    'label',
    'relabel',
]
LABEL_FILENAME = 'label.tiff'
MASKED_IMAGE_FILENAME = 'masked.tiff'


# Constants representing the setting keys for this plugin
class PluginSettings(object):
    RNASCOPE_PIXELS_PER_VIRION = 'RNAScope.pixels_per_virion'
    RNASCOPE_PIXEL_THRESHOLD = 'RNAScope.pixel_threshold'
    RNASCOPE_ROUNDNESS_THRESHOLD = 'RNAScope.roundness_threshold'
    RNASCOPE_SINGLE_VIRION_COLOR = 'RNAScope.single_virion.color'
    RNASCOPE_PRODUCTIVE_INFECTION_COLOR = 'RNAScope.productive_infection.color'
    RNASCOPE_AGGREGATE_VIRIONS_COLOR = 'RNAScope.aggregate_virions.color'
