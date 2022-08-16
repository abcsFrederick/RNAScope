import $ from 'jquery';
import _ from 'underscore';

function parameterCall(parameter) {
    var _object = {};

    var _text = parameter[0].toUpperCase() + parameter.slice(1) + ': ';
    var _color = '#fff';
    var _value;
    var _id = parameter.replace(/ /g, '-').toLowerCase();
    var _cursor = 'col-resize';

    _object.id = function (id) {
        if (!arguments.length) {
            return _id;
        }
        _id = id;
        return _object;
    };

    _object.text = function (text) {
        if (!arguments.length) {
            return _text;
        }
        _text = text;
        return _object;
    };

    _object.color = function (color) {
        if (!arguments.length) {
            return _color;
        }
        _color = color;
        return _object;
    };

    _object.cursor = function (cursor) {
        if (!arguments.length) {
            return _cursor;
        }
        _cursor = cursor;
        return _object;
    };

    _object.value = function (value) {
        if (!arguments.length) {
            return _value;
        }
        _value = value;
        return _object;
    };

    var _round = function (value) {
        return value;
    };

    _object.round = function (round) {
        if (!arguments.length) {
            return _round;
        }
        _round = round;
        return _object;
    };

    var _clamp = function (value) {
        return value;
    };

    _object.clamp = function (clamp) {
        if (!arguments.length) {
            return _clamp;
        }
        _clamp = clamp;
        return _object;
    };

    var _format = function (value) {
        return value;
    };

    _object.format = function (format) {
        if (!arguments.length) {
            return _format;
        }
        _format = format;
        return _object;
    };

    var _callback = _.constant(true);
    /*
    function () {
        return true;
    };
     */

    _object.callback = function (callback) {
        if (!arguments.length) {
            return _callback;
        }
        _callback = callback;
        return _object;
    };

    _object.render = function () {
        $('#' + _id).style = 'color:' + _color;
    };

    _object.redraw = function () {
        return _text + (_value === null ? '' : _format(_value));
    };

    return _object;
}

export default parameterCall;
