import AnnotationSelector from '@girder/histomicsui/panels/AnnotationSelector';
import events from '@girder/histomicsui/events';


const MAX_ELEMENTS_LIST_LENGTH = 1000;
const MIN_ZOOM_MAGNIFICATION = 15;

export default AnnotationSelector.extend({
    editAnnotation(model) {
        // deselect the annotation if it is already selected
        if (this._activeAnnotation && model && this._activeAnnotation.id === model.id) {
            this._activeAnnotation = null;
            this.trigger('h:editAnnotation', null);
            this._debounceRender();
            return;
        }

        if (!this._writeAccess(model)) {
            events.trigger('g:alert', {
                text: 'You do not have write access to this annotation.',
                type: 'warning',
                timeout: 2500,
                icon: 'info'
            });
            return;
        }
        let description = model.get('annotation').description;
        let zoom = this.parentView.viewer.zoom();
        let val = this.parentView.zoomWidget._maxMag * Math.pow(2, zoom - this.parentView.zoomWidget._maxZoom);
        if (description.indexOf('Generated from file') !== -1) {
            if (val >= MIN_ZOOM_MAGNIFICATION || parseInt(description.substring(description.indexOf('#elements: ') + '#elements: '.length)) < MAX_ELEMENTS_LIST_LENGTH) {
                var viewer = this.parentView.viewerWidget.viewer || {};
                model.setView(viewer.bounds(), viewer.zoom(), viewer.zoomRange().max, true);
                this._setActiveAnnotation(model);
            } else {
                events.trigger('g:alert', {
                    text: 'This annotation has too many elements to be edited.',
                    type: 'warning',
                    timeout: 5000,
                    icon: 'info'
                });
            }
        } else {
            this._setActiveAnnotation(model);
        }
        
    }
});