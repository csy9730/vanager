<template>
  <div class="zmcquery">
    <h1>{{ message }}</h1>

    <button @click="reverseMessage">Reverse Message</button>
    <button @click="fetchData">fetch Message once</button>
    <button @click="startFetch" :disabled="is_running">start fetch Message</button>
    <button @click="stopFetch" :disabled="!is_running">stop fetch Message</button>
    <button @click="clearData">clear Message</button>
    <div><textarea  readonly>{{ content }}</textarea></div>
  </div>
</template>

<script>
import axios from 'axios';
export default {
  data() {
    return {
      message: 'Zmc Query!',
      is_running: false,
      content: '',
      offset: 0,
      timerId: null
    };
  },
  methods: {
    clearData(){
      this.offset = 0
      this.content = ''
      this.stopQuerying()
    },
    reverseMessage() {
      this.message = this.message.split('').reverse().join('');
    },
    fetchData() {
      this.message = this.message.split('').reverse().join('');
      axios.get(`/api/zmcrun/get_state`, {
            params: { offset: this.offset }
        }).then((res) => {
        console.log(res.data)
        this.offset = res.data.next_ofs
        
        let data = res.data.state.sx
        // for (let i=0;i<res.data.state.length; i++){
        // data.concat(res.data.state.sx)
        // }
        if (data.length)
          this.content += ',' + data.join(',')
      });
    },
    fetchRunning() {
      this.message = this.message.split('').reverse().join('');
      axios.get('/api/zmcrun/is_running', {
            params: { offset: this.offset }
        }).then((res) => {
        console.log(res.data)
        if ( this.is_running && !res.data.is_running ){
          window.setTimeout(() => {
            this.fetchData();
            this.stopQuerying()
          }, 1500)
        }
      });
    },
    startFetch() {
      var cnt = 0;
      this.message = this.message.split('').reverse().join('');

      axios.post(`/api/zmcrun/start`, {
            params: {}
        }).then((res) => {
          this.timerId = window.setInterval(()=>{
              this.fetchData();
              if ( cnt++ % 3==2 )
                this.fetchRunning();
          }, 1000);
          this.is_running = true;
      });
    },
    stopFetch() {
      axios.post(`/api/zmcrun/stop`, {
            params: {}
        }).then((res) => {
        this.stopQuerying()
      });
    },
    stopQuerying(){
      if (this.timerId){
        window.clearInterval(this.timerId);
        this.timerId = 0
      }
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
