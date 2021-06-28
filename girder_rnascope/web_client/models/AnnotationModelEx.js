import AnnotationModel from '@girder/large_image_annotation/models/AnnotationModel';

export default AnnotationModel.extend({
    setViewBox(bbox) {
        this._region.left = bbox.left;
        this._region.top = bbox.top;
        this._region.right = bbox.right;
        this._region.bottom = bbox.bottom;
    }
});
