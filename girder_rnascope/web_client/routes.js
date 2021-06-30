// import _ from 'underscore';

// import { Layout } from '@girder/core/constants';
// import router from '@girder/core/router';
import { exposePluginConfig } from '@girder/core/utilities/PluginUtils';

import router from './router';

import events from './events';
// import AnnotationelementThumbnailView from './views/body/AnnotationelementThumbnailView';
import ImageView from './views/body/ImageView';
// import Config from './views/Config';

exposePluginConfig('rnascope', 'plugins/rnascope/config');

// router.route('plugins/rnascope/config', 'RNAScopeConfig', function () {
//     events.trigger('g:navigateTo', Config);
// });

// router.route('item/:itemId/tiles/annotationelement/thumbnail/:id/view',
//     'annotationElementThumbnailView',
//     function (itemId, id, params) {
//         events.trigger('g:navigateTo', AnnotationelementThumbnailView,
//             _.extend({ itemId: itemId, id: id }, params || {}),
//             { layout: Layout.EMPTY });
//     }
// );

function bindRoutes() {
    router.route('', 'index', function () {
        events.trigger('g:navigateTo', ImageView, {});
    });
    return router;
}

export default bindRoutes;
