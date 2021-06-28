import HistomicsTKApp from '@girder/histomicsui/app';

import bindRoutes from './routes';

var App = HistomicsTKApp.extend({
    bindRoutes: bindRoutes
});

export default App;
