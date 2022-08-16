import os
import pytest

from girder.models.folder import Folder

from girder_large_image_annotation.models.annotation import Annotation

from . import girder_utilities as utilities


@pytest.mark.plugin('rnascope')
@pytest.mark.plugin('histomicsui')
class TestAnnotationParameters(object):
    def init(self, admin):
        basePath = 'data'
        self.folder = Folder().find({
            'parentId': admin['_id'],
            'name': 'Public',
        })[0]

        curDir = os.path.dirname(os.path.realpath(__file__))
        wsiPath = os.path.join(basePath, '17138051.svs.sha512')
        self.wsiPath = os.path.join(curDir, wsiPath)
        csvPath = os.path.join(basePath, '17138051.csv.sha512')
        self.csvPath = os.path.join(curDir, csvPath)

    def testOnGetAnnotation(self, server, fsAssetstore, admin):
        self.init(admin)
        wsiitem, wsifile, csvfile = utilities.uploadVaildCSV(
            self.wsiPath, self.csvPath, self.folder, admin, fsAssetstore)
        annotation = Annotation().findOne({'itemId': wsiitem['_id']})

        resp = server.request(
            path='/annotation/' + str(annotation['_id']), user=admin)
        assert utilities.respStatus(resp) == 200
        elements = resp.json['annotation']['elements']
        groups = resp.json['groups']

        infection = list(filter(lambda x: x['label']['value'] == '10', elements))[0]
        virion = list(filter(lambda x: x['label']['value'] == '100', elements))[0]

        assert infection['group'] == 'productive infection'
        assert virion['group'] == 'single virion'
        assert len(groups) == 3
