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
  module: {
    rules: [
      {
        test: /\.js$/,
        use: 'babel-loader',
        exclude: /node_modules/,
      },
    ],
  },
}
