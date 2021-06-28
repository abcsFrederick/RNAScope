import os
import pytest

from girder.models.file import File
from girder.models.item import Item
from girder.models.folder import Folder

from girder_large_image_annotation.models.annotation import Annotation

from . import girder_utilities as utilities


@pytest.mark.plugin('rnascope')
class TestEventBind(object):
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

    def testOnFileSave(self, server, fsAssetstore, admin):
        self.init(admin)
        # upload file is not a csv file
        wsifile = utilities.uploadExternalFile(
            self.wsiPath, name='test1', user=admin, assetstore=fsAssetstore,
            reference='None')

        wsiitem = Item().load(wsifile['itemId'], user=admin)
        assert Annotation().findOne({'itemId': wsiitem['_id']}) is None

        # parent collection is not a folder
        csvfile = utilities.uploadExternalFile(
            self.csvPath, name='csv1', user=admin, assetstore=fsAssetstore,
            reference='None')
        assert Annotation().findOne({'itemId': wsiitem['_id']}) is None

        # parent folder name not contain wsi
        Folder().createFolder(
            parent=self.folder, name='test', parentType='folder', reuseExisting=True, creator=admin)
        Folder().createFolder(
            parent=self.folder, name='CSV', parentType='folder', reuseExisting=True, creator=admin)
        csvfile = utilities.uploadExternalFile(
            self.csvPath, name='csv2', folderName='CSV', user=admin, assetstore=fsAssetstore,
            reference='None')

        assert Annotation().findOne({'itemId': wsiitem['_id']}) is None

        # csv, wsi name not match
        Folder().createFolder(
            parent=self.folder, name='WSI', parentType='folder', reuseExisting=True, creator=admin)
        wsifile = utilities.uploadExternalFile(
            self.wsiPath, name='test2', folderName='WSI', user=admin, assetstore=fsAssetstore,
            reference='None')
        wsiitem = Item().load(wsifile['itemId'], user=admin)

        csvfile = utilities.uploadExternalFile(
            self.csvPath, name='csv3', folderName='CSV', user=admin, assetstore=fsAssetstore,
            reference='None')
        assert Annotation().findOne({'itemId': wsiitem['_id']}) is None

        wsiitem, wsifile, csvfile = utilities.uploadVaildCSV(
            self.wsiPath, self.csvPath, self.folder, admin, fsAssetstore)

        assert Annotation().findOne({'itemId': wsiitem['_id']})['itemId'] == wsiitem['_id']

    def testOnFileRemove(self, server, fsAssetstore, admin):
        self.init(admin)
        wsiitem, wsifile, csvfile = utilities.uploadVaildCSV(
            self.wsiPath, self.csvPath, self.folder, admin, fsAssetstore)
        File().remove(csvfile)
        assert Annotation().findOne({'itemId': wsiitem['_id']}) is None
