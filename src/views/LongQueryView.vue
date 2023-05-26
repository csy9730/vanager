<template>
  <div class="about">
    <h1>{{ message }}</h1>

    <button @click="reverseMessage">Reverse Message</button>
    <button @click="fetchData">fetch Message once</button>
    <button @click="startFetch" :disabled="is_running">start fetch Message</button>
    <button @click="stopFetch" :disabled="!is_running">stop fetch Message</button>

  </div>
</template>

<script>
import axios from 'axios';
export default {
  data() {
    return {
      message: 'Hello World!',
      is_running: false,
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
      this.is_running = true;
    },
    stopFetch() {
      window.clearInterval(this.timerId);
      this.is_running = false;
    }
  },
  computed: {
    // menuOpen() {
    //   return this.$store.state.menuOpen;
    // }
  }
};
</script>
