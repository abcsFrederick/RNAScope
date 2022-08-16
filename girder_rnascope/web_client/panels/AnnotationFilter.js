import $ from 'jquery';
import _ from 'underscore';

import { curveStepAfter, scaleLinear, scaleLog, schemeSet1 } from 'd3';
import crossfilter from 'crossfilter2';
import dc from 'dc';

import Panel from '@girder/slicer_cli_web/views/Panel';

import parameter from '../external/parameter';
import '../external/parameter-line-chart';

import annotationFilterWidget from '../templates/panels/annotationFilter.pug';
import '../stylesheets/panels/annotationFilter.styl';

import { CATEGORIES } from '../constants';

function round(digits, roundResult) {
    return (value) => {
        var divisor = Math.pow(10, Math.ceil(Math.log10(value)) - digits);
        var result = Math.round(value / divisor) * divisor;
        if (roundResult) {
            return Math.round(result);
        }
        return result;
    };
}

function format(digits) {
    return (value) => {
        if (value) return value.toFixed(digits).replace(/\.?0+$/, '');
    };
}

function clamp(value, min, max) {
    return Math.min(max, Math.max(min, value));
}

var AnnotationFilter = Panel.extend({
    initialize(settings) {
        this.annotation = settings.annotation;
        this.collection = this.annotation.elements();
        this.parametersModel = settings.parameters;
        this.setViewer(settings.viewer);

        this.parameters = {};
        // Green
        var title = 'pixels per virion';
        this.parameters.pixelsPerVirion = parameter(title)
            .callback(this._pixelsPerVirion())
            .color('#1DA475')
            .round(round(2, true))
            .format(format(2))
            .clamp((v) => {
                return clamp(v, 1, this.parameters.pixelThreshold.value() - 1);
            });
        // Orange
        title = 'pixel threshold';
        this.parameters.pixelThreshold = parameter(title)
            .callback(this._pixelThreshold())
            .color('#ED952A')
            .round(round(2, true))
            .format(format(2))
            .clamp((v) => {
                return Math.max(v, this.parameters.pixelsPerVirion.value() + 1);
            });
        title = 'roundness threshold';
        this.parameters.roundnessThreshold = parameter(title)
            .callback(this._roundnessThreshold())
            .color('#D48CF8')
            .round(round(3))
            .format(format(3));

        this.ndx = crossfilter(this.collection.models);
        this.dimensions = {
            id: this.ndx.dimension((e) => e.id),
            pixels: this.ndx.dimension((e) => +e.get('pixels')),
            roundness: this.ndx.dimension((e) => +e.get('roundness'))
        };
        this.groups = {
            pixels: this.dimensions.pixels.group(),
            roundness: this.dimensions.roundness.group(),
            statistics: this.ndx.groupAll().reduce(this._reduceAdd(), this._reduceRemove(), this._reduceInitial())
        };
        // this.ndx.onChange(this._selectFilteredAnnotations);
        this.ndx.onChange(() => {
            var value = this.groups.statistics.value();
            var statistics = {};
            _.each(CATEGORIES, (index, key) => {
                statistics[key] = value[index];
            });

            this.trigger(
                'r:statisticsUpdated',
                this.annotation.id,
                statistics
            );
        });

        this.listenTo(this.collection, 'add', this._addAnnotationElement);
        this.listenTo(this.collection, 'remove', this._removeAnnotationElement);
        this.listenTo(this.collection, 'change:exclude', this._excludeElement);
        this.listenTo(this.collection, 'reset', this._resetAnnotation);
        this.listenTo(this.collection, 'change update reset', () => {
            this.render();
            this.renderParameters();
        });

        this.parametersModel.fetch().then(() => {
            this.renderParameters();
            this._updateStatistics(true);
            return null;
        });
    },

    _classifyData(d, parameters) {
        var pixelsPerVirion = parameters.pixelsPerVirion.value();
        var pixelThreshold = parameters.pixelThreshold.value();
        var roundnessThreshold = parameters.roundnessThreshold.value();
        if (d.has('exclude')) {
            return CATEGORIES.EXCLUDED;
        } else if (+d.get('pixels') < pixelsPerVirion) {
            return CATEGORIES.SINGLE_VIRION;
        } else if (+d.get('pixels') > pixelThreshold &&
                +d.get('roundness') > roundnessThreshold) {
            return CATEGORIES.PRODUCTIVE_INFECTION;
        } else {
            return CATEGORIES.AGGREGATE_VIRIONS;
        }
    },

    _reduceAdd() {
        var parameters = this.parameters;
        return (p, v) => {
            var classification = this._classifyData(v, parameters);
            p[classification].n += 1;
            p[classification].pixels += +v.get('pixels');
            return p;
        };
    },

    _reduceRemove() {
        var parameters = this.parameters;
        return (p, v) => {
            var classification = this._classifyData(v, parameters);
            p[classification].n -= 1;
            p[classification].pixels -= +v.get('pixels');
            return p;
        };
    },

    _reduceInitial() {
        return () => {
            var p = {};
            for (var property in CATEGORIES) {
                p[CATEGORIES[property]] = { n: 0, pixels: 0 };
            }
            return p;
        };
    },

    _addAnnotationElement(element) {
        this.ndx.add(element);
    },

    _removeAnnotationElement(element) {
        var filterMap = _.mapObject(this.dimensions, (dimension, name) => {
            var filterValue = dimension.currentFilter();
            if (name === 'id') {
                dimension.filter(element.id);
            } else {
                dimension.filter();
            }
            return filterValue;
        });

        this.ndx.remove();

        _.each(this.dimensions, (dimension, name) => {
            dimension.filter(filterMap[name]);
        });
    },

    _excludeElement(evt) {
        this._updateStatistics(true);
    },

    _resetAnnotation(collection) {
        this.dimensions.id.filter();
        _.each(this.charts, (chart) => { chart.filter(null); });
        this.ndx.remove();
        this.ndx.add(collection.models);
    },

    _selectFilteredAnnotations() {
        if (!this.viewer) {
            return;
        }

        var ids = this.dimensions.id.top(Infinity);
        ids = this.parentView.selectedElements.set(ids, {silent: true});
        _.each(ids, (elementModel) => {
            elementModel.originalAnnotation = this.collection.annotation;
        });
        this.parentView._redrawSelection();
        this.parentView.trigger(
            'h:highlightAnnotation',
            this.annotation.id,
            this.parentView.selectedElements.pluck('id')
        );
    },

    _highlightAnnotationForInteractiveMode(annotation, element) {
        this.dimensions.id.filter(element);
        _.each(this.charts, (chart) => { chart.filter(null); });
        dc.redrawAll();
    },

    _toggleInteractiveMode(interactive) {
        _.each(this.charts, (chart) => {
            chart.brushOn(interactive);
            chart.filter(null);
        });
        dc.renderAll();
    },

    _updateStatistics(refresh) {
        if (refresh) {
            this.groups.statistics.reduce(
                this._reduceAdd(),
                this._reduceRemove(),
                this._reduceInitial());
        }
        var value = this.groups.statistics.value();
        var statistics = {};
        _.each(CATEGORIES, (index, key) => {
            statistics[key] = value[index];
        });
        this.trigger(
            'r:statisticsUpdated',
            this.annotation.id,
            statistics
        );
        return statistics;
    },

    _pixelsPerVirion() {
        return () => {
            if (this.parametersModel) {
                var value = this.parameters.pixelsPerVirion.value();
                this.parametersModel.set(
                    'parameters', { 'pixelsPerVirion': value }
                ).save().done(() => {
                    this.trigger('r:parametersUpdated');
                });
            }
            this._updateStatistics(true);
        };
    },

    _pixelThreshold() {
        return () => {
            if (this.parametersModel) {
                var value = this.parameters.pixelThreshold.value();
                this.parametersModel.set(
                    'parameters', { 'pixelThreshold': value }
                ).save().done(() => {
                    this.trigger('r:parametersUpdated');
                });
            }
            this._updateStatistics(true);
            // this.trigger('r:parametersUpdated');
        };
    },

    _roundnessThreshold() {
        return () => {
            if (this.parametersModel) {
                var value = this.parameters.roundnessThreshold.value();
                this.parametersModel.set(
                    'parameters', { 'roundnessThreshold': value }
                ).save().done(() => {
                    this.trigger('r:parametersUpdated');
                });
            }
            this._updateStatistics(true);
            // this.trigger('r:parametersUpdated');
        };
    },

    render() {
        if (!this.viewer) {
            this.$el.empty();
            return;
        }

        this.$el.html(annotationFilterWidget({
            id: 'annotation-filter-container',
            title: 'Filter',
            _
        }));

        var maxPixels = 0;
        var maxRoundness = 0;
        _.each(this.collection.models, (element) => {
            maxPixels = Math.max(maxPixels, +element.get('pixels'));
            maxRoundness = Math.max(maxRoundness, +element.get('roundness'));
        });

        dc.config.defaultColors(schemeSet1);

        this.charts = {};

        $('<div/>').attr('id', 'h-annotation-filter-pixel')
            .appendTo(this.$('.s-panel-content'));
        this.charts.pixels = dc.parameterLineChart('#h-annotation-filter-pixel');
        this.charts.pixels.parent = this;
        this.charts.pixels
            .curve(curveStepAfter)
            .renderArea(true)
            .width(283)
            .height(150)
            .x(scaleLog().domain([1, maxPixels]))
            // .elasticX(true)
            .elasticY(true)
            // .useViewBoxResizing(true)
            // .controlsUseVisibility(true)
            .xAxisLabel('Pixels')
            .dimension(this.dimensions.pixels)
            .group(this.groups.pixels)
            .brushOn(this.parentView.annotationSelector.interactiveMode())
            .on('filtered', () => { this._selectFilteredAnnotations(); });
        this.charts.pixels.xAxis().tickFormat((d) => {
            return Math.log10(d) % 1 ? '' : d;
        });
        // workaround for scroll capture
        this.charts.pixels._disableMouseZoom = () => {};
        this.charts.pixels.render();

        $('<div/>').attr('id', 'h-annotation-filter-roundness')
            .appendTo(this.$('.s-panel-content'));
        this.charts.roundness = dc.parameterLineChart('#h-annotation-filter-roundness');
        this.charts.roundness.parent = this;

        this.charts.roundness
            .curve(curveStepAfter)
            .renderArea(true)
            .width(283)
            .height(150)
            .x(scaleLinear().domain([0, maxRoundness]))
            // .elasticX(true)
            .elasticY(true)
            .xAxisLabel('Roundness')
            .dimension(this.dimensions.roundness)
            .group(this.groups.roundness)
            .brushOn(this.parentView.annotationSelector.interactiveMode())
            .on('filtered', () => { this._selectFilteredAnnotations(); });
        // workaround for scroll capture
        this.charts.roundness._disableMouseZoom = () => {};
        this.charts.roundness.render();

        return this;
    },

    renderParameters() {
        var parameters = this.parametersModel.get('parameters');
        if (!parameters) {
            return;
        }
        this.parameters.pixelsPerVirion.value(parameters['pixelsPerVirion']);
        this.parameters.pixelThreshold.value(parameters['pixelThreshold']);
        this.parameters.roundnessThreshold.value(parameters['roundnessThreshold']);

        var maxPixels = parameters['pixelThreshold'];
        var maxRoundness = parameters['roundnessThreshold'];
        _.each(this.collection.models, (element) => {
            maxPixels = Math.max(maxPixels, +element.get('pixels'));
            maxRoundness = Math.max(maxRoundness, +element.get('roundness'));
        });

        this.charts.pixels.verticalSelections([
            this.parameters.pixelsPerVirion,
            this.parameters.pixelThreshold
        ]).x(scaleLog().domain([1, maxPixels])).render();
        this.charts.roundness.verticalSelections([
            this.parameters.roundnessThreshold
        ]).x(scaleLinear().domain([0, maxRoundness])).render();
    },

    setViewer(viewer) {
        this.viewer = viewer;
        return this;
    }
});

export default AnnotationFilter;
