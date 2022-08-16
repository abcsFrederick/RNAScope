<!DOCTYPE html>
<html lang="en">
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>${brandName | h}</title>
    <link rel="stylesheet" href="${staticPublicPath}/built/googlefonts.css">
    <link rel="stylesheet" href="${staticPublicPath}/built/fontello/css/fontello.css">
    <link rel="stylesheet" href="${staticPublicPath}/built/fontello/css/animation.css">
    <link rel="stylesheet" href="${staticPublicPath}/built/girder_lib.min.css">
    <link rel="icon" type="image/png" href="${staticPublicPath}/img/Girder_Favicon.png">
    % for plugin in pluginCss:
    <link rel="stylesheet" href="${staticPublicPath}/built/plugins/${plugin}/plugin.min.css">
    % endfor
  </head>
  <body>
    <div id="g-global-info-apiroot" class="hide">${apiRoot}</div>
    <div id="g-global-info-staticroot" class="hide">${staticPublicPath}</div>
    <script src="${staticPublicPath}/built/girder_lib.min.js"></script>
    <script src="${staticPublicPath}/built/girder_app.min.js"></script>
    <script type="text/javascript">
        $(function () {
            $('body').addClass('hui-body');
            // girder.router.enabled(false);
            girder.events.trigger('g:appload.before');
            var app = new girder.plugins.RNAScope.App({
                el: 'body',
                parentView: null,
                brandName: '${pluginBrandName | js}',
                bannerColor: '${pluginBannerColor | js}',
            });
            app.bindRoutes();
            girder.events.trigger('g:appload.after');
        });
    </script>
    % for plugin in pluginJs:
    <script src="${staticPublicPath}/built/plugins/${plugin}/plugin.min.js"></script>
    % endfor
  </body>
</html>
