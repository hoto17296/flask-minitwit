import Vue from 'vue'
import timeline from './components/timeline.vue'
import fecha from 'fecha'

Vue.filter('format_datetime', function (timestamp) {
  return fecha.format(new Date(timestamp * 1000),'YYYY-MM-DD hh:mm');
})

const messages = JSON.parse(document.getElementById('data_messages').textContent);

new Vue({
  el: '#timeline',
  render: h => h(timeline, { props: { messages } }),
});
