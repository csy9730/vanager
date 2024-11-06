<template>
  <div class="longquery">
    <h1>Command Run log {{ message }}</h1>
    <label>command </label>
    <input type="text" ref="getCmdline" placeholder="ping localhost" value="ping localhost" style="width: 80%;">
    <br>
    <label>cwd </label>
    <input type="text" ref="getCwd" placeholder="" value="">
    <label> use gbk </label>
    <input type="checkbox" ref="getEncoding" checked="true">
    <label> use shell</label>
    <input type="checkbox" ref="getShell" checked="true">
    <br>
    <button @click="startFetch" :disabled="is_running">start </button>
    <button @click="stopFetch" :disabled="!is_running">stop </button>
    <button @click="fetchData">fetch Message once</button>
    <button @click="clearData">clear Message</button>
    <br>
    <br>
    <div >
      <textarea id="txtMeta" style="width: 90%;height:600px;">{{ content }}</textarea>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
export default {
  data() {
    return {
      message: '',
      is_running: false,
      content: '',
      offset: 0,
      r_id: 0,
      is_gbk: true,
      timerId: null
    };
  },
  methods: {
    clearData() {
      this.offset = 0
      this.content = ''
      this.stopQuerying()
    },
    reverseMessage() {
      console.log();
      // this.message = this.message.split('').reverse().join('');
    },
    fetchData() {
      var enc = "utf8"
      if (this.is_gbk)
        enc = "gbk"
      axios.get(`/runlog/api/data`, {
        params: { offset: this.offset, id: this.r_id, encoding: enc}
      }).then((res) => {
        console.log(res.data)
        if (res.data.errCode != 0) {
          console.log("errCode != 0!");
          this.stopQuerying();
          return;
        }
        if (this.is_running && !res.data.is_running) {
          window.setTimeout(() => {
            this.fetchData();
            this.stopQuerying()
          }, 500)
        }
        this.offset = res.data.data.ends
        for (let i = 0; i < res.data.data.lines.length; i++) {
          // data.push(res.data.state[i].data)
          this.content += res.data.data.lines[i] + "\n";
        }
        // resolve();
      }, (res) => {this.stopQuerying();});
    },
    startFetch() {
      var cnt = 0;
      // this.message = this.message.split('').reverse().join('');
      let cmdline = this.$refs.getCmdline.value;
      this.is_gbk = this.$refs.getEncoding.checked;
      var params = {
        cmds: cmdline,
        shell: this.$refs.getShell.checked
      }
      if (cmdline == '') return;
      if (this.$refs.getCwd.value != '')
        params.cwd = this.$refs.getCwd.value;
      // console.log(params);

      axios.post(`/runlog/api/start`, params).then((res) => {
        this.r_id = res.data.id;
        this.offset = 0;
        this.timerId = window.setInterval(() => {
          this.fetchData();
        }, 1000);
        this.is_running = true;
      });
    },
    stopFetch() {
      axios.put(`/runlog/api/stop`, {
        params: { id: this.r_id }
      }).then((res) => {
        this.stopQuerying()
      });
    },
    stopQuerying() {
      if (this.timerId) {
        window.clearInterval(this.timerId);
        this.timerId = 0;
        this.r_id = 0;
        // this.offset = 0;
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
