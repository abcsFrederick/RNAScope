import { wrap } from '@girder/core/utilities/PluginUtils';

import HeaderView from '@girder/histomicsui/views/layout/HeaderImageView';

// import HeaderDownloadView from './HeaderDownloadView';

wrap(HeaderView, 'render', function (render) {
    render.call(this);
    // if (!this.headerDownloadView) {
    //     this.headerDownloadView = new HeaderDownloadView({
    //         el: this.$('.h-open-annotated-image').parent(),
    //         // el: this.$('.r-csv-download-wrapper'),
    //         parentView: this
    //     });
    // }
    // this.headerDownloadView.render();
    return this;
});

export default HeaderView;
