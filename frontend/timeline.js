import Vue from 'vue';
import fecha from 'fecha';
import timeline from './components/timeline.vue';

Vue.filter('format_datetime', timestamp => fecha.format(new Date(timestamp * 1000), 'YYYY-MM-DD hh:mm'));

const messages = JSON.parse(document.getElementById('data_messages').textContent);

new Vue({ // eslint-disable-line no-new
  el: '#timeline',
  render: h => h(timeline, { props: { messages } }),
});
