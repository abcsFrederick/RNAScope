import _ from 'underscore';

import { format } from 'd3';
import dc from 'dc';

import Panel from '@girder/slicer_cli_web/views/Panel';

import { CATEGORIES } from '../constants';

import statisticsWidget from '../templates/panels/statistics.pug';
import '../stylesheets/panels/statistics.styl';

var Statistics = Panel.extend({
    displays() {
        return {
            SINGLE_VIRION: {
                html: {
                    one: '%number single virion selected',
                    some: '%number single virions selected',
                    none: 'no single virions selected'
                },
                valueAccessor: (p) => {
                    var n = p[CATEGORIES.SINGLE_VIRION].n;
                    var aggregatePixels = p[CATEGORIES.AGGREGATE_VIRIONS].pixels;
                    var parameters = this.parameters.get('parameters');
                    if (!parameters || !parameters.pixelsPerVirion) {
                        return 0;
                    }
                    n += Math.floor(aggregatePixels / parameters.pixelsPerVirion);
                    return n;
                }
            },
            PRODUCTIVE_INFECTION: {
                html: {
                    one: '%number productive infection selected',
                    some: '%number productive infections selected',
                    none: 'no productive infections selected'
                },
                valueAccessor: (p) => {
                    var parameters = this.parameters.get('parameters');
                    if (!parameters) {
                        return 0;
                    }
                    return p[CATEGORIES.PRODUCTIVE_INFECTION].n;
                }
            }
            /*
            },
            AGGREGATE_VIRIONS: {
                html: {
                    one: '%number aggregate virion selected',
                    some: '%number aggregate virions selected',
                    none: 'no aggregate virions selected'
                },
                valueAccessor: (p) => {
                    var aggregatePixels = p[CATEGORIES.AGGREGATE_VIRIONS].pixels;
                    return Math.floor(aggregatePixels / PIXELS_PER_VIRION);
                }
            }
             */
        };
    },

    initialize(settings) {
        this.model = settings.model;
        this.parameters = settings.parameters;
        this.group = settings.group;
        this.setViewer(settings.viewer);

        this.listenTo(this.model, 'change', this.render);
    },

    render() {
        if (!this.viewer) {
            this.$el.empty();
            return;
        }

        if (this.numberDisplays) {
            _.each(this.numberDisplays, (numberDisplay) => {
                numberDisplay.redraw();
            });
            return;
        }

        this.$el.html(statisticsWidget({
            id: 'statistics-container',
            title: 'Statistics',
            labels: _.keys(CATEGORIES),
            _
        }));

        this.numberDisplays = _.map(this.displays(), (value, label) => {
            return dc.numberDisplay('#' + label)
                .formatNumber(format(',d'))
                .html(value.html)
                .group(this.group)
                .valueAccessor(value.valueAccessor);
        });

        return this;
    },

    setViewer(viewer) {
        this.viewer = viewer;
        return this;
    }
});

export default Statistics;
