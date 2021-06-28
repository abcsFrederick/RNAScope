import tinycolor from 'tinycolor2';

import View from '@girder/core/views/View';

import PluginConfigBreadcrumbWidget from '@girder/core/views/widgets/PluginConfigBreadcrumbWidget';
import { restRequest } from '@girder/core/rest';
import events from '@girder/core/events';

import configTemplate from '../templates/views/config.pug';
import '../stylesheets/views/config.styl';

var Config = View.extend({
    events: {
        'submit #g-rnascope-form': function (event) {
            event.preventDefault();
            this.$('#g-rnascope-error-message').empty();
            this._saveSettings([{
                key: 'RNAScope.pixels_per_virion',
                value: +this.$('.g-rnascope-pixels-per-virion').val()
            }, {
                key: 'RNAScope.pixel_threshold',
                value: +this.$('.g-rnascope-pixel-threshold').val()
            }, {
                key: 'RNAScope.roundness_threshold',
                value: +this.$('.g-rnascope-roundness-threshold').val()
            }, {
                key: 'RNAScope.single_virion.color',
                value: this.convertColor(this.$('.g-rnascope-single-virion-color').val())
            }, {
                key: 'RNAScope.productive_infection.color',
                value: this.convertColor(this.$('.g-rnascope-productive-infection-color').val())
            }, {
                key: 'RNAScope.aggregate_virions.color',
                value: this.convertColor(this.$('.g-rnascope-aggregate-virions-color').val())
            }]);
        }
    },

    initialize: function () {
        Config.getSettings((settings) => {
            this.settings = settings;
            this.render();
        });
    },

    render: function () {
        this.$el.html(configTemplate({
            settings: this.settings,
            viewers: Config.viewers
        }));
        this.$('.h-colorpicker').colorpicker();
        if (!this.breadcrumb) {
            this.breadcrumb = new PluginConfigBreadcrumbWidget({
                pluginName: 'RNAScope',
                el: this.$('.g-config-breadcrumb-container'),
                parentView: this
            }).render();
        }

        return this;
    },

    convertColor(val) {
        if (!val) {
            return 'rgba(0,0,0,0)';
        }
        return tinycolor(val).toRgbString();
    },

    _saveSettings: function (settings) {
        return restRequest({
            type: 'PUT',
            url: 'system/setting',
            data: {
                list: JSON.stringify(settings)
            },
            error: null
        }).done(() => {
            Config.clearSettings();
            events.trigger('g:alert', {
                icon: 'ok',
                text: 'Settings saved.',
                type: 'success',
                timeout: 4000
            });
        }).fail((resp) => {
            this.$('#g-rnascope-error-message').text(
                resp.responseJSON.message
            );
        });
    }
}, {
    /* Class methods and objects */

    /**
     * Get settings if we haven't yet done so.  Either way, call a callback
     * when we have settings.
     *
     * @param {function} callback a function to call after the settings are
     *      fetched.  If the settings are already present, this is called
     *      without any delay.
     */
    getSettings: function (callback) {
        if (!Config.settings) {
            restRequest({
                type: 'GET',
                url: 'RNAScope/settings'
            }).done((resp) => {
                Config.settings = resp;
                if (callback) {
                    callback(Config.settings);
                }
            });
        } else {
            if (callback) {
                callback(Config.settings);
            }
        }
    },

    /**
     * Clear the settings so that getSettings will refetch them.
     */
    clearSettings: function () {
        delete Config.settings;
    }
});

export default Config;
