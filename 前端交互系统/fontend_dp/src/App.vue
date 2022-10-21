<template>

</template>

<script>

import axios from "axios";

export default {
  name: 'App',
  components: {

  },
  mounted() {
    axios({
      url: 'http://127.0.0.1:8000/baseDp/',
      method: 'post',
      data: {
        'mechanism': 'laplace',
        'searchWay': 'sum',
        'epsilon': 1.0
      }
    }).then((data) => {
      console.log(data.data);
    })
  }
}
</script>

<style>

</style>
