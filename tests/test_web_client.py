import os
import pytest
import shutil

from girder.models.folder import Folder
from girder.constants import STATIC_ROOT_DIR

from pytest_girder.web_client import runWebClientTest

from . import girder_utilities as utilities


def copyRUITest():
    src = os.path.join(os.path.dirname(__file__), 'web_client_specs', 'ruiTest.js')
    dest = os.path.join(STATIC_ROOT_DIR, 'built/plugins/rnascope', 'ruiTest.js')
    if not os.path.exists(dest) or os.path.getmtime(src) != os.path.getmtime(dest):
        shutil.copy2(src, dest)


def makeResources(server, fsAssetstore, admin, user):
    # Create WSI/CSV folders in the user Public folder
    basePath = 'data'
    folder = Folder().find({
        'parentId': user['_id'],
        'name': 'Public',
    })[0]

    # Upload a sample file with csv
    curDir = os.path.dirname(os.path.realpath(__file__))
    wsiPath = os.path.join(basePath, '17138051.svs.sha512')
    wsiPath = os.path.join(curDir, wsiPath)
    csvPath = os.path.join(basePath, '17138051.csv.sha512')
    csvPath = os.path.join(curDir, csvPath)

    utilities.uploadVaildCSV(wsiPath, csvPath, folder, user, fsAssetstore)


@pytest.mark.plugin('rnascope')
@pytest.mark.plugin('histomicsui')
@pytest.mark.parametrize('spec', (
    'imageViewerSpec.js',
    ''
))
def testWebClient(boundServer, fsAssetstore, db, admin, user, spec):  # noqa
    copyRUITest()
    makeResources(boundServer, fsAssetstore, admin, user)
    spec = os.path.join(os.path.dirname(__file__), 'web_client_specs', spec)
    runWebClientTest(boundServer, spec, 15000)
