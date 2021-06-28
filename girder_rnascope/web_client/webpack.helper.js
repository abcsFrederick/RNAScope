module.exports = function (config) {
    config.module.rules.push({
        resource: {
            test: /\.js$/
        },
        use: [
            {
                loader: 'babel-loader',
                options: {
                    presets: ['env']
                }
            }
        ]
    });
    return config;
};
