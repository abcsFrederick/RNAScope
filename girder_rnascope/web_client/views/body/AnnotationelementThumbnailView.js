import { getApiRoot } from '@girder/core/rest';
import View from '@girder/core/views/View';

import annotationelementThumbnailView from '../../templates/views/annotationelementThumbnailView.pug';

var AnnotationelementThumbnailView = View.extend({
    initialize: function (settings) {
        this.itemId = settings.itemId;
        this.id = settings.id;
        View.prototype.initialize.apply(this, arguments);

        this.render();
    },

    render: function () {
        this.$el.html(annotationelementThumbnailView({
            itemId: this.itemId,
            id: this.id,
            apiRoot: getApiRoot()
        }));

        return this;
    }
});

export default AnnotationelementThumbnailView;
