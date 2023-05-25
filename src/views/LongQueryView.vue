<template>
  <div class="about">
    <h1>{{ message }}</h1>

    <button @click="reverseMessage">Reverse Message</button>
    <button @click="fetchData">fetch Message once</button>
    <button @click="startFetch">start fetch Message</button>
    <button @click="stopFetch">stop fetch Message</button>

  </div>
</template>

<script>
import axios from 'axios';
export default {
  data() {
    return {
      message: 'Hello World!',
      timerId: null
    };
  },
  methods: {
    reverseMessage() {
      this.message = this.message.split('').reverse().join('');
    },
    fetchData() {
      this.message = this.message.split('').reverse().join('');
      let ss = axios.get(`/api/todo/list`, {
            params: {}
        }).then((res) => {
        console.log(res.data.todos)
        // resolve();
        });
      
    },
    startFetch() {
      this.message = this.message.split('').reverse().join('');
      this.timerId = window.setInterval(()=>{
            this.fetchData();
        }, 3000);
    },
    stopFetch() {
      window.clearInterval(this.timerId);
    }
  },
  computed: {
    // menuOpen() {
    //   return this.$store.state.menuOpen;
    // }
  }
};
</script>
