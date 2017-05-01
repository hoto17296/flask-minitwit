<template>
  <div class='message'>
    <img :src='user.icon_url'>
    <p>
      <strong>
        <a :href='user_timeline_path'>{{ user.name }}</a>
      </strong>
      {{ text }}
      <small>&mdash; {{ pub_date | format_datetime }}</small>
    </p>
  </div>
</template>

<script>
export default {
  name: 'message',
  props: {
    text: { type: String, required: true },
    user: { type: Object, required: true },
    pub_date: { type: Number, required: true },
  },
  computed: {
    user_timeline_path: function() {
      return '/' + this.user.name;
    },
  },
}
</script>

<style scoped>
.message {
  margin: 10px 0;
  padding: 5px;
  background: #F0FAF9;
  border: 1px solid #DBF3F1;
  border-radius: 5px;
  min-height: 48px;
}

.message > img {
  float: left;
  padding: 0 10px 0 0;
}

.message > p {
  margin: 0;
}

.message > p > small {
  font-size: 0.9em;
  color: #888;
}
</style>
