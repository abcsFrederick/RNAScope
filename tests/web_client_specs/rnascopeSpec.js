girderTest.importPlugin('jobs');
girderTest.importPlugin('worker');
girderTest.importPlugin('large_image');
girderTest.importPlugin('slicer_cli_web');
girderTest.importPlugin('HistomicsTK');
girderTest.importPlugin('RNAScope');

girderTest.startApp();

function createFolder(folderName) {
    waitsFor(function () {
        return $('.g-create-subfolder').length > 0;
    }, 'hierarchy widget to load');

    runs(function () {
        return $('.g-create-subfolder').click();
    });
    girderTest.waitForDialog();
    waitsFor(function () {
        return $('.modal-body input#g-name').length > 0;
    }, 'create folder dialog to appear');

    runs(function () {
        $('#g-name').val(folderName);
        $('.g-save-folder').click();
    });
    girderTest.waitForLoad();
    waitsFor(function () {
        return $('.g-folder-list-link').length > 0;
    }, 'new folder to appear in the list');
}

// from larger_image imageViewerSpec.js
function createLargeImage() {
    runs(function () {
        $('a.g-item-list-link').click();
    });
    girderTest.waitForLoad();
    waitsFor(function () {
        return $('.g-large-image-create').length !== 0;
    });
    runs(function () {
        $('.g-large-image-create').click();
    });
    girderTest.waitForLoad();
    // wait for job to complete
    waitsFor(function () {
        return $('.g-item-image-viewer-select').length !== 0;
    }, 15000);
    girderTest.waitForLoad();
}

$(function () {
    describe('Test the RNAScope plugin', function () {
        it('create the admin user', function () {
            girderTest.createUser('admin', 'admin@email.com', 'Admin', 'User', 'password')();
        });
        it('go to collections page', function () {
            runs(function () {
                $("a.g-nav-link[g-target='collections']").click();
            });

            waitsFor(function () {
                return $('.g-collection-create-button:visible').length > 0;
            }, 'navigate to collections page');

            runs(function () {
                expect($('.g-collection-list-entry').length).toBe(0);
            });
        });
        it('create RNAScope collection', girderTest.createCollection('RNAScope', '', 'clientTestBatch'));
        it('create test subdirectories', function () {
            girderTest.waitForLoad();
            runs(function () {
                $('.g-folder-list-link:first').click();
            });
            girderTest.waitForLoad();

            createFolder('testClientImage');

            girderTest.waitForLoad();
            runs(function () {
                $('.g-folder-list-link:first').click();
            });
            girderTest.waitForLoad();

            createFolder('testClientROI');

            girderTest.waitForLoad();
            runs(function () {
                $('.g-folder-list-link:first').click();
            });

            _.each(['csv', 'label', 'original'], createFolder);
        });
        it('upload label test file', function () {
            runs(function () {
                $('.g-folder-list-link:contains(label)').click();
            });
            girderTest.waitForLoad();
            runs(function () {
                girderTest.binaryUpload('plugins/large_image/plugin_tests/test_files/test_L_8.png');
            });
            girderTest.waitForLoad();
            createLargeImage();
            runs(function () {
                $('.g-item-breadcrumb-link[data-type="folder"]:contains(testClientROI)').click();
            });
            girderTest.waitForLoad();
        });
        it('upload image test file', function () {
            runs(function () {
                $('.g-folder-list-link:contains(original)').click();
            });
            girderTest.waitForLoad();
            runs(function () {
                girderTest.binaryUpload('plugins/large_image/plugin_tests/test_files/test_RGB_8.png');
            });
            girderTest.waitForLoad();
            createLargeImage();
            runs(function () {
                $('.g-item-breadcrumb-link[data-type="folder"]:contains(testClientROI)').click();
            });
            girderTest.waitForLoad();
        });
    });
});
