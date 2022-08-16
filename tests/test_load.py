import pytest

from girder.plugin import loadedPlugins


@pytest.mark.plugin('rnascope')
def test_import(server):
    assert 'rnascope' in loadedPlugins()
