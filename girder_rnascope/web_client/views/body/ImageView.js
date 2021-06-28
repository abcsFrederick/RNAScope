/* global geo */
import $ from 'jquery';
import _ from 'underscore';

// import GeojsViewer from '@girder/large_image/views/imageViewerWidget/geojs';
import { ViewerWidget } from '@girder/large_image_annotation/views';
import ImageView from '@girder/histomicsui/views/body/ImageView';
import eventStream from '@girder/core/utilities/EventStream';

import imageTemplate from '@girder/histomicsui/templates/body/image.pug';
import events from '@girder/histomicsui/events';
import DrawWidget from '@girder/histomicsui/panels/DrawWidget';
import AnnotationSelector from '../../panels/AnnotationSelectorEx';

import ParametersModel from '../../models/Parameters';
// import StatisticsModel from '../../models/Statistics';

import AnnotationCollection from '../../collections/AnnotationCollectionEx';

import AnnotationFilter from '../../panels/AnnotationFilter';
// import DrawWidget from '../../panels/DrawWidget';
// import Statistics from '../../panels/Statistics';

const MAX_ELEMENTS_LIST_LENGTH = 1000;
const MIN_ZOOM_MAGNIFICATION = 15;

export default ImageView.extend({
    initialize(settings) {
        ImageView.prototype.initialize.apply(this, arguments);

        this.annotations = new AnnotationCollection();

        if (this.annotationSelector) {
            this.annotationSelector.destroy();
        }
        this.annotationSelector = new AnnotationSelector({
            parentView: this,
            collection: this.annotations,
            image: this.model
        });

        this.annotationSelector.stopListening(eventStream, 'g:eventStream.start');
        this.listenTo(this.annotationSelector.collection, 'sync remove reset change:loading', this.setViewBox);
        this.listenTo(this.annotationSelector.collection, 'add update change:displayed', this.toggleAnnotation);

        this.listenTo(this.annotationSelector, 'h:toggleLabels', this.toggleLabels);
        this.listenTo(this.annotationSelector, 'h:toggleInteractiveMode', this._toggleInteractiveMode);
        this.listenTo(this.annotationSelector, 'h:editAnnotation', this._editAnnotation);
        this.listenTo(this.annotationSelector, 'h:deleteAnnotation', this._deleteAnnotation);
        this.listenTo(this.annotationSelector, 'h:annotationOpacity', this._setAnnotationOpacity);
        this.listenTo(this.annotationSelector, 'h:annotationFillOpacity', this._setAnnotationFillOpacity);
        this.listenTo(this.annotationSelector, 'h:redraw', this._redrawAnnotation);

        // $('<div/>').addClass('h-statistics s-panel hidden')
        //     .appendTo(this.$('#h-annotation-selector-container'));
        $('<div/>').addClass('h-annotation-filter s-panel hidden')
            .appendTo(this.$('#h-annotation-selector-container'));

        // this.annotationSelector._writeAccess = function (annotation) {
        //     return annotation.get('_accessLevel') >= AccessType.ADMIN &&
        //         !annotation.get('fileId');
        // };

        // this.render();
    },
    render() {
        // this._removeStatistics();
        this._removeAnnotationFilter();

        // Ensure annotations are removed from the popover widget on rerender.
        // This can happen when opening a new image while an annotation is
        // being hovered.
        this.mouseResetAnnotation();
        this._removeDrawWidget();

        if (this.model.id === this._openId) {
            this.controlPanel.setElement('.h-control-panel-container').render();
            return;
        }
        this.$el.html(imageTemplate());
        this.contextMenu.setElement(this.$('#h-annotation-context-menu')).render();

        if (this.model.id) {
            this._openId = this.model.id;
            if (this.viewerWidget) {
                this.viewerWidget.destroy();
            }
            /* eslint-disable new-cap */
            this.viewerWidget = new ViewerWidget.geojs({
                parentView: this,
                el: this.$('.h-image-view-container'),
                itemId: this.model.id,
                hoverEvents: true,
                // it is very confusing if this value is smaller than the
                // AnnotationSelector MAX_ELEMENTS_LIST_LENGTH
                highlightFeatureSizeLimit: 5000,
                scale: {position: {bottom: 20, right: 10}}
            });
            this.trigger('h:viewerWidgetCreated', this.viewerWidget);

            // handle annotation mouse events
            this.listenTo(this.viewerWidget, 'g:mouseOverAnnotation', this.mouseOverAnnotation);
            this.listenTo(this.viewerWidget, 'g:mouseOutAnnotation', this.mouseOutAnnotation);
            this.listenTo(this.viewerWidget, 'g:mouseOnAnnotation', this.mouseOnAnnotation);
            this.listenTo(this.viewerWidget, 'g:mouseOffAnnotation', this.mouseOffAnnotation);
            this.listenTo(this.viewerWidget, 'g:mouseClickAnnotation', this.mouseClickAnnotation);
            this.listenTo(this.viewerWidget, 'g:mouseResetAnnotation', this.mouseResetAnnotation);

            this.viewerWidget.on('g:imageRendered', () => {
                events.trigger('h:imageOpened', this.model);
                // store a reference to the underlying viewer
                this.viewer = this.viewerWidget.viewer;

                this.imageWidth = this.viewer.maxBounds().right;
                this.imageHeight = this.viewer.maxBounds().bottom;
                // this.viewBoxWidth = 2500; // Math.min(this.imageWidth, this.imageHeight)/5;
                // this.viewBox = {'top': 0, 'bottom': 0, 'left': 0, 'right': 0};
                // allow panning off the image slightly
                var extraPanWidth = 0.1, extraPanHeight = 0;
                this.viewer.maxBounds({
                    left: -this.imageWidth * extraPanWidth,
                    right: this.imageWidth * (1 + extraPanWidth),
                    top: -this.imageHeight * extraPanHeight,
                    bottom: this.imageHeight * (1 + extraPanHeight)
                });

                // set the viewer bounds on first load
                this.setImageBounds();

                // also set the query string
                this.setBoundsQuery();

                if (this.viewer) {
                    this.viewer.zoomRange({max: this.viewer.zoomRange().max + this._increaseZoom2x});

                    // update the query string on pan events
                    this.viewer.geoOn(geo.event.pan, () => {
                        this.setBoundsQuery();
                    });

                    this.viewer.geoOn(geo.event.actionup, (evt) => {
                        this.showAnnotations(evt);
                    });
                    // update the coordinate display on mouse move
                    this.viewer.geoOn(geo.event.mousemove, (evt) => {
                        this.showCoordinates(evt);
                    });

                    this.viewer.geoOn(geo.event.zoom, (evt) => {
                        clearTimeout($.data(this, 'timer'));
                        $.data(this, 'timer', setTimeout(_.bind(function () {
                            this.showAnnotations(evt);
                        }, this), 250));
                    });
                    $('<div/>').addClass('h-workflow-selector s-panel')
                        .insertAfter(this.$('#h-metadata-panel'));
                    // remove the hidden class from the coordinates display
                    this.$('.h-image-coordinates-container').removeClass('hidden');

                    // show the right side control container
                    this.$('#h-annotation-selector-container').removeClass('hidden');

                    this.overviewWidget
                        .setViewer(this.viewerWidget)
                        .setElement('.h-overview-widget').render();

                    this.zoomWidget
                        .setViewer(this.viewerWidget)
                        .setElement('.h-zoom-widget').render();

                    this.metadataWidget
                        .setItem(this.model)
                        .setElement('.h-metadata-widget').render();

                    this.annotationSelector
                        .setViewer(this.viewerWidget)
                        .setElement('.h-annotation-selector').render();

                    if (this.workflowSelector !== undefined) {
                        this.workflowSelector
                            .setViewer(this.viewerWidget)
                            .setElement('.h-workflow-selector');
                    }

                    if (this.drawWidget) {
                        this.$('.h-draw-widget').removeClass('hidden');
                        this.drawWidget
                            .setViewer(this.viewerWidget)
                            .setElement('.h-draw-widget').render();
                    }
                    // let layer = this.viewerWidget.annotationLayer;
                    // let map = this.viewerWidget.viewer;
                    // this.coordinates = [{x: 0, y: 0}, {x: 0, y: this.viewBoxWidth}, {x: this.viewBoxWidth, y: this.viewBoxWidth}, {x: this.viewBoxWidth, y: 0}];
                    // let rect = geo.annotation.rectangleAnnotation({
                    //     name: 'Loading...',
                    //     layer: layer,
                    //     corners: this.coordinates,
                    //     style: {
                    //         fill: false,
                    //         strokeWidth: 1
                    //     },
                    //     editStyle: {
                    //         strokeWidth: 2,
                    //         fill: true
                    //     } });
                    // layer.addAnnotation(rect);
                    // layer.options('clickToEdit', true);
                    // layer._update();
                    // map.geoOn(geo.event.actionup, _.bind(function (evt) {
                    //     let newCoordinates = rect.coordinates()
                    //     if (this.coordinates[0].x !== newCoordinates[0].x || this.coordinates[0].y !== newCoordinates[0].y ||
                    //         this.coordinates[2].x !== newCoordinates[2].x || this.coordinates[2].y !== newCoordinates[2].y) {
                    //         this.coordinates = rect.coordinates();
                    //         this.viewBox = {'top': this.coordinates[0].y, 'bottom': this.coordinates[2].y, 'left': this.coordinates[0].x, 'right': this.coordinates[2].x};
                    //         this.setViewBox();
                    //         if (this.annotation) {
                    //             layer.options('showLabels', true);
                    //             this.annotation.fetch().done(() => {
                    //                 // FIXME: move to paramter update
                    //                 if (this.annotation.get('annotation').elements.length > MAX_ELEMENTS_LIST_LENGTH) {
                    //                     events.trigger('g:alert', {
                    //                         text: 'This annotation has too many elements to be edited.',
                    //                         type: 'warning',
                    //                         timeout: 5000,
                    //                         icon: 'info'
                    //                     });
                    //                     this._removeAnnotationFilter();
                    //                 }
                    //                 if (this.annotationFilter) {
                    //                     this.annotationFilter.renderParameters();
                    //                 }
                    //                 layer.options('showLabels', false);
                    //             });
                    //         }
                    //     }
                    // }, this));
                    // this.viewerWidget.annotationLayer.addAnnotation(states)

                    // if (this.drawWidget) {
                    //     this.$('.h-draw-widget').removeClass('hidden');
                    //     this.drawWidget
                    //         .setViewer(this.viewerWidget)
                    //         .setElement('.h-draw-widget').render();
                    // }
                }
            });
            this.annotationSelector.setItem(this.model);

            this.annotationSelector
                .setViewer(null)
                .setElement('.h-annotation-selector').render();

            if (this.drawWidget) {
                this.$('.h-draw-widget').removeClass('hidden');
                this.drawWidget
                    .setViewer(null)
                    .setElement('.h-draw-widget').render();
            }
        }
        this.controlPanel.setElement('.h-control-panel-container').render();
        this.popover.setElement('#h-annotation-popover-container').render();

        // $('<div/>').addClass('h-statistics s-panel hidden')
        //     .appendTo(this.$('#h-annotation-selector-container'));
        $('<div/>').addClass('h-annotation-filter s-panel hidden')
            .appendTo(this.$('#h-annotation-selector-container'));

        if (this.model.id) {
            this.viewerWidget.on('g:imageRendered', () => {
                if (this.viewer) {
                    if (this.annotationFilter) {
                        this.$('.h-annotation-filter').removeClass('hidden');
                        this.annotationFilter
                            .setViewer(this.viewerWidget)
                            .setElement('.h-annotation-filter')
                            .render();
                    }
                    // if (this.statistics) {
                    //     this.$('.h-statistics').removeClass('hidden');
                    //     this.statistics
                    //         .setViewer(this.viewerWidget)
                    //         .setElement('.h-statistics')
                    //         .render();
                    // }
                }
            });

            if (this.annotationFilter) {
                this.$('.h-annotation-filter').removeClass('hidden');
                this.annotationFilter
                    .setViewer(null)
                    .setElement('.h-annotation-filter')
                    .render();
            }
            // if (this.statistics) {
            //     this.$('.h-statistics').removeClass('hidden');
            //     this.statistics
            //         .setViewer(null)
            //         .setElement('.h-statistics')
            //         .render();
            // }
        }

        return this;
    },

    toggleAnnotation(annotation) {
        console.log('toggleAnnotation');
        // When delete annotation, [annotation models] will trigger that as well
        if (!this.viewerWidget || annotation.length !== undefined) {
            // We may need a way to queue annotation draws while viewer
            // initializes, but for now ignore them.
            return;
        }

        // Keep annotation for rnascope annotaions rather than others like aperio
        // ERROR
        // description is not defined when delete annotation
        if (annotation.get('annotation')['description'].includes('Generated from file')) { // ==Generated from file
            this.annotation = annotation;
        }

        let zoom = this.viewer.zoom();
        let val = this.zoomWidget._maxMag * Math.pow(2, zoom - this.zoomWidget._maxZoom);

        let description = annotation.get('annotation')['description'];
        if (description.includes('Generated from file') && 
            parseInt(description.substring(description.indexOf('#elements: ') + '#elements: '.length)) > MAX_ELEMENTS_LIST_LENGTH) {
            if (val < MIN_ZOOM_MAGNIFICATION) {
                this.viewerWidget.removeAnnotation(annotation);
                events.trigger('g:alert', {
                    text: 'Please zoom in to at last ' + MIN_ZOOM_MAGNIFICATION + ' to view annotations.',
                    type: 'warning',
                    timeout: 5000,
                    icon: 'info'
                });
                return;
            }
        }
        if (annotation.get('displayed')) {
            var viewer = this.viewerWidget.viewer || {};
            if (viewer.zoomRange && annotation._pageElements === true) {
                annotation.setView(viewer.bounds(), viewer.zoom(), viewer.zoomRange().max, true);
            }
            annotation.set('loading', true);
            annotation.once('g:fetched', () => {
                annotation.unset('loading');
            });
            annotation.fetch().then(() => {
                // abandon this if the annotation should not longer be shown
                // or we are now showing a different image.
                if (!annotation.get('displayed') || annotation.get('itemId') !== this.model.id) {
                    return null;
                }
                this.viewerWidget.drawAnnotation(annotation);
                return null;
            });
        } else {
            this.viewerWidget.removeAnnotation(annotation);
        }
    },
    _removeAnnotationFilter() {
        if (this.annotationFilter) {
            this.stopListening(this.annotationFilter);
            this.annotationFilter.remove();
            this.annotationFilter = null;
            $('<div/>').addClass('h-annotation-filter s-panel hidden')
                .appendTo(this.$('#h-annotation-selector-container'));
        }
    },

    _removeStatistics() {
        if (this.statistics) {
            this.stopListening(this.statistics);
            this.statistics.remove();
            this.statistics = null;
            $('<div/>').addClass('h-statistics s-panel hidden')
                .appendTo(this.$('#h-annotation-selector-container'));
        }
    },

    _editAnnotation(model) {
        console.log('_editAnnotation');
        this.activeAnnotation = model;

        this._removeAnnotationFilter();
        this._removeDrawWidget();
        let description = this.activeAnnotation.get('annotation').description;
        if (this.activeAnnotation && this.activeAnnotation.has('fileId') && description.indexOf('Generated from file') !== -1) {
            this.parametersModel = new ParametersModel({
                annotationId: this.activeAnnotation ? this.activeAnnotation.id : undefined
            });
            let zoom = this.viewer.zoom();
            let val = this.zoomWidget._maxMag * Math.pow(2, zoom - this.zoomWidget._maxZoom);

            if (val >= MIN_ZOOM_MAGNIFICATION || parseInt(description.substring(description.indexOf('#elements: ') + '#elements: '.length)) < MAX_ELEMENTS_LIST_LENGTH) {
                this.annotationFilter = new AnnotationFilter({
                    parentView: this,
                    annotation: this.activeAnnotation,
                    parameters: this.parametersModel,
                    el: this.$('.h-annotation-filter'),
                    viewer: this.viewerWidget
                }).render();
                this.$('.h-annotation-filter').removeClass('hidden');

                this.listenTo(this.annotationFilter, 'r:parametersUpdated',
                    (annotationId, statistics) => {
                        if (this.activeAnnotation && this.activeAnnotation.id === this.annotationFilter.annotation.id) {
                            this.activeAnnotation.fetch().done(() => {
                                // FIXME: move to paramter update
                                this.annotationFilter.renderParameters();
                            });
                        }
                    });
            }
        } else {
            if (model) {
                this.drawWidget = new DrawWidget({
                    parentView: this,
                    image: this.model,
                    annotation: this.activeAnnotation,
                    drawingType: this._lastDrawingType,
                    el: this.$('.h-draw-widget'),
                    viewer: this.viewerWidget
                }).render();
                this.listenTo(this.drawWidget, 'h:redraw', this._redrawAnnotation);
                this.$('.h-draw-widget').removeClass('hidden');
            }
        }
    },

    _deleteAnnotation(model) {
        ImageView.prototype._deleteAnnotation.apply(this, arguments);
        // if (this.activeAnnotation && this.activeAnnotation.id === model.id)
        if (this.activeAnnotation !== undefined) {
            // if (this.activeAnnotation.id === this.statistics.annotation.id) {
            //     this._removeStatistics();
            // }
            if (this.annotationFilter && this.activeAnnotation.id === this.annotationFilter.annotation.id) {
                this._removeAnnotationFilter();
            }
        }
    },

    _highlightAnnotationForInteractiveMode(annotation, element) {
        ImageView.prototype._highlightAnnotationForInteractiveMode.apply(this, arguments);
        if (!Array.isArray(element) && this.annotationFilter) {
            this.annotationFilter._highlightAnnotationForInteractiveMode(annotation, element);
        }
    },

    _toggleInteractiveMode(interactive) {
        ImageView.prototype._toggleInteractiveMode.apply(this, arguments);
        if (this.annotationFilter) {
            this.annotationFilter._toggleInteractiveMode(interactive);
        }
    },

    setViewBox() {
        if (this.annotationSelector.collection.length && this.viewBox) {
            for (let i = 0; i < this.annotationSelector.collection.models.length; i++) {
                if (this.annotationSelector.collection.models[i].get('annotation').description.indexOf('Generated from file') === -1) continue;
                this.annotationSelector.collection.models[i].setViewBox(this.viewBox);
            }
        }
    },

    showAnnotations(evt) {
        if (!this.zoomWidget || !this.annotation) return;
        let zoom = this.viewer.zoom();
        let val = this.zoomWidget._maxMag * Math.pow(2, zoom - this.zoomWidget._maxZoom);
        let description = this.annotation.get('annotation').description;
        if (val >= MIN_ZOOM_MAGNIFICATION || parseInt(description.substring(description.indexOf('#elements: ') + '#elements: '.length)) < MAX_ELEMENTS_LIST_LENGTH) {
            let bounds = this.viewer.bounds();
            let left = bounds.left < 0 ? 0 : Math.round(bounds.left),
                top = bounds.top < 0 ? 0 : Math.round(bounds.top),
                right = bounds.right < 0 ? 0 : Math.round(bounds.right),
                bottom = bounds.bottom < 0 ? 0 : Math.round(bounds.bottom);
            this.viewBox = {'top': top, 'bottom': bottom, 'left': left, 'right': right};
            this.setViewBox();
            if (this.annotation) {
                this.annotation.fetch().done(() => {
                    // FIXME: move to paramter update
                    if (this.annotation.get('annotation').elements.length > MAX_ELEMENTS_LIST_LENGTH) {
                        events.trigger('g:alert', {
                            text: 'This annotation has too many elements to be edited.',
                            type: 'warning',
                            timeout: 5000,
                            icon: 'info'
                        });
                        this._removeAnnotationFilter();
                    }
                    if (this.annotationFilter) {
                        this.annotationFilter.renderParameters();
                    }
                });
            }
        } else {
            this._removeAnnotationFilter();
        }
    }
});
