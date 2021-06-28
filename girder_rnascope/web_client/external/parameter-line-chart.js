import { drag, event, select, selection } from 'd3';
import dc from 'dc';

function clamp(value, min, max) {
    return Math.min(max, Math.max(min, value));
}

dc.parameterLineChart = function (_chart) {
    var VERTICAL_SELECTION_CLASS = 'vertical-selection';

    _chart = dc.lineChart(_chart);

    var _verticalSelections = [];

    var x = _chart.x;

    _chart.x = function (xScale) {
        if (arguments.length) {
            var result = x(xScale);
            _chart._x = xScale;
            return result;
        }
        return x();
    };

    function _renderVerticalSelections(g) {
        if (!g) {
            return;
        }

        var gridLineG = g.select('g.' + VERTICAL_SELECTION_CLASS);

        if (gridLineG.empty()) {
            gridLineG = g.append('g', ':last-child')
                .attr('class', VERTICAL_SELECTION_CLASS)
                .attr('transform', 'translate(' + _chart.margins().left + ',' + _chart.margins().top + ')');
        }

        var lines = gridLineG.selectAll('line').data(_verticalSelections);

        selection.prototype.moveToFront = function () {
            return this.each(function () {
                this.parentNode.appendChild(this);
            });
        };

        var drag_ = drag()
            .on('start', function (d, i) {
                select(this).moveToFront();
            })
            .on('drag', function (d, i) {
                var range = _chart._x.range();
                var x = clamp(event.x, range[0], range[1]);
                d.value(d.clamp()(d.round()(_chart._x.invert(x))));
                select(this).attr('x1', x).attr('x2', x);
            })
            .on('end', function (d, i) {
                var x = _chart._x(d.value());
                select(this).attr('x1', x).attr('x2', x);
                d.redraw();
                d.callback()();
            });

        // enter
        lines.enter()
            .append('line')
            .attr('id', function (d) {
                return d.id();
            })
            .attr('x1', function (d) {
                return _chart._x(d.value());
            })
            .attr('y1', _chart._xAxisY() - _chart.margins().top)
            .attr('x2', function (d) {
                return _chart._x(d.value());
            })
            .attr('y2', 0)
            .attr('style', function (d) {
                return 'stroke:' + d.color() + ';stroke-width:3;cursor:' + d.cursor();
            })
            .each(function (d, i) { d.redraw(); })
            .call(drag_);

        // exit
        lines.exit().remove();
    }

    _chart.renderVerticalSelections = _renderVerticalSelections;

    _chart.verticalSelections = function (_) {
        if (!arguments.length) {
            return _verticalSelections;
        }
        _verticalSelections = _;
        return _chart;
    };

    var _doRender = _chart._doRender;

    _chart._doRender = function () {
        var result = _doRender();

        _renderVerticalSelections(_chart.g());

        return result;
    };

    _chart.redrawVerticalSelections = function () {
        if (!_chart.g()) {
            return;
        }

        var gridLineG = _chart.g().select('g.' + VERTICAL_SELECTION_CLASS);
        gridLineG.selectAll('line')
            .each(function (d) {
                var x = _chart._x(d.value());
                if (x) {
                    select(this).attr('x1', x).attr('x2', x);
                }
                d.redraw();
            });
    };

    return _chart;
};

export default dc.parameterLineChart;
