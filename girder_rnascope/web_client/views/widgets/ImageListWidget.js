import _ from 'underscore';
import FolderListWidget from '@girder/core/views/widgets/FolderListWidget';

var ImageListWidget = FolderListWidget.extend({
    initialize(settings) {
        this._checked = settings.checked;
        FolderListWidget.prototype.initialize.call(this, settings);
    },

    render() {
        FolderListWidget.prototype.render.apply(this, arguments);
        _.each(this._checked, (image) => {
            var collectionImage = this.collection.get(image.get('_id'));
            if (collectionImage) {
                var cid = collectionImage.cid;
                this.checked.push(cid);
                this.$('.g-list-checkbox[g-folder-cid="' + cid + '"]').prop('checked', true);
            }
        }, this);
    }
});

export default ImageListWidget;
