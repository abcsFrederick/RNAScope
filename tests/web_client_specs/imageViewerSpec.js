girderTest.importPlugin('jobs', 'worker', 'large_image', 'large_image_annotation', 'slicer_cli_web', 'histomicsui', 'rnascope');

// const NUMBER_OF_ELEMENTS = 16;
// var app;
girderTest.addScript('/static/built/plugins/rnascope/ruiTest.js');

girderTest.promise.done(function () {
    ruiTest.startApp();
    describe('Test the RNAScope screen', function () {
        it('login', function () {
            ruiTest.login();
        });
        it('open image', function () {
            ruiTest.openImage('17138051.svs');
        });
    });
});
// girderTest.promise.done(function () {
//     ruiTest.startApp();
//     describe('Annotation tests', function () {

//         describe('setup', function () {
//             it('login', function () {
//                 // ruiTest.login();
//                 expect(1).toBe(1);
//             });

//             // it('open image', function () {
//             //     ruiTest.openImage('image');
//             // });
//         });
//     });
// });

// $(function () {
//     describe('RNAScope image viewer tests', function () {
//         describe('setup', function () {
//             it('login', function () {
//                 histomicsTest.login();
//             });

//             it('open image', function () {
//                 var name = '001.tif';
//                 var imageId;
//                 var deferred = $.Deferred();

//                 runs(function () {
//                     app.bodyView.once('h:viewerWidgetCreated', function (viewerWidget) {
//                         viewerWidget.once('g:beforeFirstRender', function () {
//                             window.geo.util.mockWebglRenderer();
//                         });
//                     });
//                     $('.h-open-image').click();
//                 });

//                 girderTest.waitForDialog();

//                 runs(function () {
//                     var collectionId = $('#g-root-selector option:contains("RNAScope")').val();
//                     $('#g-root-selector').val(
//                         collectionId  // girder.auth.getCurrentUser().id
//                     ).trigger('change');
//                 });

//                 waitsFor(function () {
//                     return $('#g-dialog-container .g-folder-list-link').length > 0;
//                 }, 'Hierarchy widget to render');

//                 runs(function () {
//                     $('.g-folder-list-link:contains("batch")').click();
//                 });

//                 waitsFor(function () {
//                     return $('.g-folder-list-link').length > 0;
//                 }, 'folder list to load');

//                 runs(function () {
//                     $('.g-folder-list-link:contains("image")').click();
//                 });

//                 waitsFor(function () {
//                     return $('.g-folder-list-link').length > 0;
//                 }, 'folder list to load');

//                 runs(function () {
//                     $('.g-folder-list-link:contains("roi")').click();
//                 });

//                 waitsFor(function () {
//                     return $('.g-folder-list-link').length > 0;
//                 }, 'folder list to load');

//                 runs(function () {
//                     $('.g-folder-list-link:contains("original")').click();
//                 });

//                 waitsFor(function () {
//                     return $('.g-item-list-link').length > 0;
//                 }, 'item list to load');

//                 runs(function () {
//                     var $item = $('.g-item-list-link:contains("' + name + '")');
//                     imageId = $item.next().attr('href').match(/\/item\/([a-f0-9]+)\/download/)[1];
//                     expect($item.length).toBe(1);
//                     $item.click();
//                 });
//                 waitsFor(function () {
//                     return $('#g-selected-model').val();
//                 }, 'selection to be set');

//                 girderTest.waitForDialog();
//                 runs(function () {
//                     $('.g-submit-button').click();
//                 });

//                 girderTest.waitForLoad();
//                 waitsFor(function () {
//                     return $('.geojs-layer.active').length > 0;
//                 }, 'image to load');
//                 runs(function () {
//                     expect(girder.plugins.HistomicsTK.router.getQuery('image')).toBe(imageId);
//                     currentImageId = imageId;
//                     deferred.resolve(imageId);
//                 });

//                 return deferred.promise();
//             });
//         });
//         describe('select annotation', function () {
//             it('select annotation', function () {
//                 waitsFor(function () {
//                     return $('.h-annotation-selector .h-annotation-group-name').length > 0;
//                 }, 'annotations groups to be visible');
//                 runs(function () {
//                     $('.h-annotation-selector .h-annotation-group-name')[0].click();
//                 });
//                 waitsFor(function () {
//                     return $('.h-annotation-selector .h-annotation .h-annotation-name').length > 0;
//                 }, 'annotations to be visible');
//                 runs(function () {
//                     $('.h-annotation-selector .h-annotation .h-annotation-name').click();
//                 });
//                 waitsFor(function () {
//                     return $('.h-elements-container .h-element').length > 0;
//                 }, 'elements to be visible');
//                 runs(function () {
//                     expect($('.h-elements-container .h-element').length).toBe(NUMBER_OF_ELEMENTS);
//                 });
//             });
//         });
//         describe('verify statistics', function () {
//             it('verify statistics', function () {
//                 waitsFor(function () {
//                     return $('.h-statistics').length > 0;
//                 }, 'has statistics panel');
//                 waitsFor(function () {
//                     return $('#SINGLE_VIRION.h-statistic').length > 0 && $('#SINGLE_VIRION.h-statistic .number-display').text().length > 0 && $('#SINGLE_VIRION.h-statistic .number-display').text() === '20,396 single virions selected';
//                 }, 'has single virion statistic');
//                 waitsFor(function () {
//                     return $('#PRODUCTIVE_INFECTION.h-statistic').length > 0 && $('#PRODUCTIVE_INFECTION.h-statistic .number-display').text().length > 0 && $('#PRODUCTIVE_INFECTION.h-statistic .number-display').text() === '7 productive infections selected';
//                 }, 'has productive infection statistic');
//                 runs(function () {
//                     expect($('#SINGLE_VIRION.h-statistic .number-display').text()).toBe('20,396 single virions selected');
//                 });
//                 runs(function () {
//                     expect($('#PRODUCTIVE_INFECTION.h-statistic .number-display').text()).toBe('7 productive infections selected');
//                 });
//             });
//         });
//         describe('verify parameters', function () {
//             it('verify parameters', function () {
//                 waitsFor(function () {
//                     return $('.h-annotation-filter').length > 0;
//                 }, 'has annotation filter panel');
//                 waitsFor(function () {
//                     return $('#h-annotation-filter-pixel .vertical-selection').length > 0 && $('#h-annotation-filter-pixel .vertical-selection line').length === 2;
//                 }, 'has pixel vertical selections');
//                 runs(function () {
//                     // $('#h-annotation-filter-pixel .vertical-selection line').click();
//                     $('#h-annotation-filter-pixel .vertical-selection line').mousedown().mousemove().mouseup();
//                 });
//                 girderTest.waitForLoad();
//             });
//         });
//         describe('download statistics', function () {
//             it('download statistics', function () {
//                 waitsFor(function () {
//                     return $('.r-download-statistics').length > 0;
//                 }, 'has download statistics button');
//                 runs(function () {
//                     $('.r-download-statistics').click();
//                 });
//                 girderTest.waitForDialog();
//                 waitsFor(function () {
//                     return $('#g-dialog-container .g-folder-list-entry .g-list-checkbox').length > 0 && $('#g-dialog-container .g-folder-list-entry .g-list-checkbox').prop('checked');
//                 }, 'image folder selection dialog to render');
//                 runs(function () {
//                     $('#g-dialog-container .g-folder-list-entry .g-list-checkbox').click();
//                 });
//                 waitsFor(function () {
//                     return !$('#g-dialog-container .g-folder-list-entry .g-list-checkbox').prop('checked');
//                 }, 'image folder selection to change');
//                 runs(function () {
//                     $('#image-select-all').click();
//                 });
//                 waitsFor(function () {
//                     return $('#g-dialog-container .g-folder-list-entry .g-list-checkbox').prop('checked');
//                 }, 'image folder selection (all) to change');
//                 runs(function () {
//                     $('.g-submit-button').click();
//                 });
//                 // girderTest.waitForLoad();
//             });
//         });
//     });
// });
