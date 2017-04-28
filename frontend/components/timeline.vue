<template>
  <div class='timeline'>
    <h1>{{ msg }}</h1>
  </div>
</template>

<script>
export default {
  name: 'timeline',
  data() {
    return {
      msg: 'Welcome to Your Vue.js App',
    };
  },
};
</script>

<style scoped>
.timeline > h1 {
  color: green;
}
</style>
