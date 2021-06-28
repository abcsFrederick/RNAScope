import View from '@girder/core/views/View';

import events from '../../events';

import BatchModel from '../../models/Batch';

import headerDownloadTemplate from '../../templates/layout/headerDownload.pug';
import '../../stylesheets/layout/headerDownload.styl';

var HeaderDownloadView = View.extend({
    events: {
        'click .r-download-statistics': function (evt) {
            events.trigger('r:downloadStatistics', {
                batch: this.batch,
                images: [this.image]
            });
        }
    },

    initialize() {
        this.largeImage = null;
        this.listenTo(events, 'h:imageOpened', (largeImage) => {
            this.largeImage = largeImage;
            if (this.largeImage) {
                this.largeImage.getRootPath((resp) => {
                    this.batch = new BatchModel(resp[1].object);
                    // this.image = new FolderModel(resp[2].object);
                });
            }

            this.render();
        });
    },

    render() {
        if (this.largeImage && !this.$('.r-csv-download-wrapper').length) {
            // console.log(this.$('.r-csv-download-wrapper'))
            // $('.r-csv-download-wrapper').removeClass('hidden');
            this.$el.append(headerDownloadTemplate({
                image: this.largeImage
            }));
        } else {
            // this.$el.addClass('hidden');
        }
        return this;
    }
});

export default HeaderDownloadView;
