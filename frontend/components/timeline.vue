<template>
  <div class='timeline'>
    <ul class='messages' v-if='messages.length > 0'>
      <li v-for='message in messages'>
        <message v-bind='message' />
      </li>
    </ul>
    <p v-else>There's no message so far.</p>
  </div>
</template>

<script>
import message from './message'

export default {
  name: 'timeline',
  components: { message },
  props: {
    messages: {
      type: Array,
      required: true,
    }
  },
}
</script>

<style scoped>
.timeline > h1 {
  color: green;
}

.messages {
  list-style: none;
  margin: 0;
  padding: 0;
}
</style>
