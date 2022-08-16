import _ from 'underscore';

import { restRequest } from '@girder/core/rest';

import AccessControlledModel from '@girder/core/models/AccessControlledModel';

export default AccessControlledModel.extend({
    altUrl: 'RNAScope/annotation/parameters',
    idAttribute: 'annotationId',

    save: function () {
        if (this.altUrl === null && this.resourceName === null) {
            throw new Error('An altUrl or resourceName must be set on the Model.');
        }

        var path, type;
        if (this.has(this.idAttribute)) {
            path = (this.altUrl || this.resourceName) + '/' + this.get(this.idAttribute);
            type = 'PUT';
        } else {
            path = (this.altUrl || this.resourceName);
            type = 'POST';
        }

        var params = _.reduce(this.get('parameters'),
            function (string, value, key) {
                return string + (string.length ? '&' : '?') + key + '=' + value;
            }, '');

        return restRequest({
            url: path + params,
            method: type
        }).done((resp) => {
            this.set(resp);
            this.trigger('g:saved');
        }).fail((err) => {
            this.trigger('g:error', err);
        });
    }
});
