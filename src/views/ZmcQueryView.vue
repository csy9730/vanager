<template>
  <div class="zmcquery">
    <h1>{{ message }}</h1>

    <button @click="reverseMessage">Reverse Message</button>
    <button @click="fetchData">fetch Message once</button>
    <button @click="startFetching" :disabled="is_querying">start fetch Message</button>
    <button @click="stopQuerying" :disabled="!is_querying">stop fetch Message</button>
    <button @click="addPath" > add Path</button>
    <input type="checkbox" v-model="is_relative" >
    <input v-model="movePos" >
    <button @click="moveStop" :disabled="!is_running">stop </button>
    <button @click="clearData">clear Message</button>
    <button @click="resetMq">reset Motion</button>
    <br>
    <div><textarea  readonly>{{ content }}</textarea></div>
    <br>
    <div :id="id" :style="{height:height,width:width}"> </div>
  </div>
</template>

<script>
import axios from 'axios';
import * as echarts from 'echarts'

export default {
  data() {
    return {
      message: 'Zmc Query!',
      is_running: false,
      is_querying: false,
      content: '',
      offset: 0,
      is_relative: true,
      movePos: "10,15",
      id: "chartId",
      width: "600px",
      height: "600px",
      chart: null,
      tt: [],
      xx: [],
      yy: [],
      timerId: null
    };
  },
    mounted() {
      this.initChart()
    },
  computed:{
    movePosStr (){
      // return [10, 15]
      const ss2 = this.movePos.split(',')
      var ss3 = []
      for (var i=0;i<ss2.length;i++)
        ss3.push(parseFloat(ss2[i]))
      return ss3
    }
  },
  methods: {
    clearData(){
      this.offset = 0
      this.content = ''
      this.tt = []
      this.xx = []
      this.yy = []
      this.stopQuerying()
    },
    reverseMessage() {
      this.message = this.message.split('').reverse().join('');
      this.initChart()
    },
    fetchData() {
      this.message = this.message.split('').reverse().join('');
      axios.get(`/api/zmcrun/get_state`, {
            params: { offset: this.offset}
        }).then((res) => {
        console.log(res.data)
        this.offset = res.data.next_ofs
        
        let data = res.data.state.sx
        for (let i=0; i<res.data.state.sx.length; i++){
          this.xx.push(res.data.state.sx[i])
          this.yy.push(res.data.state.sy[i])
          this.tt.push(res.data.state.tt[i])
        // data.concat(res.data.state.sx)
        }
        console.log(this.xx, this.tt)
        if (data.length)
          this.content += ',' + data.join(',')

        this.updateChart();

      });
    },
    fetchRunning() {
      this.message = this.message.split('').reverse().join('');
      axios.get('/api/zmcrun/is_running', {
            params: { offset: this.offset }
        }).then((res) => {
        console.log(res.data)
        this.is_running = res.data.is_running
        if ( this.is_querying && !res.data.is_running ){
          window.setTimeout(() => {
            this.fetchData();
            this.stopQuerying()
          }, 1500)
        }
      });
    },
    startFetching() {
      var cnt = 0;
      this.timerId = window.setInterval(()=>{
        this.fetchData();
        if ( cnt++ % 3==2 )
          this.fetchRunning();
      }, 1000);
      this.is_querying = true;
    },

    stopQuerying(){
      if (this.timerId){
        window.clearInterval(this.timerId);
        this.timerId = 0
      }
      this.is_querying = false;
    },
    addPath(){
      this.message = this.message.split('').reverse().join('');
      console.log(this.movePosStr )
      axios.post(`/api/zmcrun/start`, {
            is_relative: this.is_relative, 
            movePos: this.movePosStr 
        }).then((res) => {
          this.is_running = true
          if (!this.is_querying)
            this.startFetching()
      });
    },
    moveStop() {
      axios.post(`/api/zmcrun/stop`, {
            params: {}
        }).then((res) => {
        // this.stopQuerying()
      });
    },
    resetMq() {
      axios.post(`/api/zmcrun/reset`, {
            params: {}
        }).then((res) => {
        this.stopQuerying()
        this.is_running = false
      });
    },
    initChart() {
      this.chart = echarts.init(document.getElementById(this.id))
      const opt =  {
        title: {
          text: 'ROC'
        },
        tooltip: {},
        xAxis: {
          data: [1,2,3]
        },
        yAxis: {
          // data: [1,2,3]
        },
        series: [{
          name: 'loss',
          type: 'line',
          data: [1,4,9]
        }]
      }
      this.chart.setOption(opt)
    },
    updateChart(){
      const opt = {
        title: {
          text: 'ROC'
        },
        tooltip: {},
        xAxis: {
          data: this.tt
        },
        yAxis: {
        },
        series: [{
          name: 'xpos',
          type: 'line',
          data: this.xx
        },
        {
          name: 'ypos',
          type: 'line',
          data: this.yy
        }]
      }
      this.chart.setOption(opt)
    }
  }
};
</script>
