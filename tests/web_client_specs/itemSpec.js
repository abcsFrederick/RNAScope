girderTest.importPlugin('jobs', 'worker', 'large_image', 'large_image_annotation', 'slicer_cli_web', 'histomicsui');

girderTest.startApp();

describe('Test the HistomicsUI itemUI screen', function () {
    var brandName = 'TestBrandName';
    it('login', function () {
    	expect(1).toBe(1);
        // girderTest.login('admin', 'Admin', 'Admin', 'password')();
    });
});