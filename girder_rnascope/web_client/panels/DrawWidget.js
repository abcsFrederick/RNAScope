import _ from 'underscore';

import { getApiRoot } from '@girder/core/rest';

import DrawWidget from '@girder/histomicsui/panels/DrawWidget';

import drawWidget from '../templates/panels/thumbnailDrawWidget.pug';
import '@girder/histomicsui/stylesheets/panels/drawWidget.styl';
import '../stylesheets/panels/drawWidget.styl';

export default DrawWidget.extend({
    events: _.extend(DrawWidget.prototype.events, {
        'click .h-exclude-element': '_excludeElement',
        'click .h-include-element': '_includeElement'
    }),

    _excludeElement(evt) {
        this.collection.get(this._getId(evt)).set('exclude', true);
    },

    _includeElement(evt) {
        this.collection.get(this._getId(evt)).unset('exclude');
    },

    render() {
        this.$('[data-toggle="tooltip"]').tooltip('destroy');
        if (!this.viewer) {
            this.$el.empty();
            return;
        }
        const name = (this.annotation.get('annotation') || {}).name || 'Untitled';
        this.trigger('h:redraw', this.annotation);
        var readOnly = Boolean(this.annotation && this.annotation.get('fileId'));
        this.$el.html(drawWidget({
            title: readOnly ? 'Select' : 'Draw',
            elements: this.collection.models,
            groups: this._groups,
            style: this._style.id,
            highlighted: this._highlighted,
            apiRoot: getApiRoot(),
            imageId: this.image.id,
            readOnly: readOnly,
            name
        }));
        if (this._drawingType) {
            this.$('button.h-draw[data-type="' + this._drawingType + '"]').addClass('active');
            this.drawElement(undefined, this._drawingType);
        }
        this.$('.s-panel-content').collapse({toggle: false});
        this.$('[data-toggle="tooltip"]').tooltip({container: 'body'});
        if (this.viewer.annotationLayer && !this.viewer.annotationLayer._boundHistomicsTKModeChange) {
            this.viewer.annotationLayer._boundHistomicsTKModeChange = true;
            this.viewer.annotationLayer.geoOn(window.geo.event.annotation.mode, (event) => {
                this.$('button.h-draw').removeClass('active');
                if (this._drawingType) {
                    this.$('button.h-draw[data-type="' + this._drawingType + '"]').addClass('active');
                }
                if (event.mode !== this._drawingType && this._drawingType) {
                    /* This makes the draw modes stay on until toggled off.
                     * To turn off drawing after each annotation, add
                     *  this._drawingType = null;
                     */
                    this.drawElement(undefined, this._drawingType);
                }
            });
        }
        return this;
    }
});
