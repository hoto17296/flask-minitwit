const path = require('path');

module.exports = {
  context: path.resolve(__dirname, 'frontend'),
  entry: {
    timeline: './timeline.js',
  },
  output: {
    path: path.resolve(__dirname, 'server/static'),
    filename: '[name].js',
  },
  resolve: {
    extensions: ['.js', '.vue']
  },
  module: {
    rules: [
      {
        enforce: 'pre',
        test: /.(js|vue)$/,
        loader: 'eslint-loader',
        exclude: /node_modules/
      },
      {
        test: /\.js$/,
        loader: 'babel-loader',
        exclude: /node_modules/
      },
      {
        test: /\.vue$/,
        use: 'vue-loader',
      },
    ],
  },
}
