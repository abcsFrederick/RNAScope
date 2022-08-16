import _ from 'underscore';

import router from '@girder/histomicsui/router';
import { Layout } from '@girder/core/constants';

import Config from './views/Config';
import events from './events';
import AnnotationelementThumbnailView from './views/body/AnnotationelementThumbnailView';

router.route('plugins/rnascope/config', 'RNAScopeConfig', function () {
    events.trigger('g:navigateTo', Config);
});

router.route('item/:itemId/tiles/annotationelement/thumbnail/:id/view',
    'annotationElementThumbnailView',
    function (itemId, id, params) {
        events.trigger('g:navigateTo', AnnotationelementThumbnailView,
            _.extend({ itemId: itemId, id: id }, params || {}),
            { layout: Layout.EMPTY });
    }
);

export default router;
