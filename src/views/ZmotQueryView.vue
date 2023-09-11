<template>
  <div class="zmotquery">
    <h1>{{ message }}</h1>

    <div>
    <button @click="reverseMessage">Reverse Message</button>
    <button @click="fetchData">fetch Message once</button>
    <button @click="startFetching" :disabled="is_querying">start fetch Message</button>
    <button @click="stopQuerying" :disabled="!is_querying">stop fetch Message</button>
    </div>
    <br>
    <div>
    <button @click="addDefMove" > add DefMove</button>
    <!-- <button @click="addPath" > add Path</button> -->
    <!-- <input type="checkbox" v-model="is_relative" > -->
    <!-- <input v-model="movePos" > -->

    <button @click="addZcode" > add Zcode</button>
    <input v-model="zmovePos" >
    </div>
    <br>
    <div>
    <button @click="moveStop" :disabled="!is_running">stop </button>
    <button @click="movePause" :disabled="!is_running">pause </button>
    <button @click="moveResume" :disabled="!is_running">resume </button>
    <button @click="moveClear" :disabled="!is_running">clear </button>
    <button @click="clearData">clear Message</button>
    <button @click="resetMq">reset Motion</button>
    </div>
    <br>
    <!-- <h4 v-bind:title="currentPosStr"></h4> -->
    <h4  readonly>pos= {{ currentPos }}</h4>
    <br>
    <div>
      <textarea class="content"  readonly>{{ content }}</textarea>
      <textarea class="txtHistory"  readonly>{{ txtHistory }}</textarea>
    </div>
    <br>
    <div class="chart-container">
      <div :id="id" :style="{height:height,width:width}"> </div>
      <!-- <div :id="id" height="100%" width="100%" /> -->
    </div>
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
      txtHistory: '', 
      offset: 0,
      is_relative: true,
      movePos: "10,15",
      zmovePos: "move 10,15",
      id: "chartId",
      // width: "600px",
      width: "100%",
      height: "600px",
      chart: null,
      currentPos: [0, 0],
      tt: [],
      xx: [],
      yy: [],
      ss: [],
      vv: [],
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
    },
    zmovePosStr (){
      return this.zmovePos
    },
    currentPosStr (){
      return this.currentPos.join(',')
    }
  },
  methods: {
    clearData(){
      this.offset = 0
      this.content = ''
      this.txtHistory = ''
      this.tt = []
      this.xx = []
      this.yy = []
      this.vv = []
      this.ss = []
      this.stopQuerying()
      this.updateChart()
    },
    reverseMessage() {
      this.message = this.message.split('').reverse().join('');
      this.initChart()
    },
    fetchData() {
      this.message = this.message.split('').reverse().join('');
      axios.get(`/zmot/api/data`, {
            params: { offset: this.offset}
        }).then((res) => {
        console.log(res.data)
        this.offset = res.data.next_offset
        // tick, x, sc, vc
        let data = res.data.data
        let lines = ''
        
        for (let i=0; i<data.length; i++){
          let N = data[i].length
          this.xx.push(data[i][1])
          this.currentPos[0] = data[i][1]
          if (N>=5){
            this.yy.push(data[i][2])
            this.currentPos[1] = data[i][2]
          }else {
            this.yy.push(this.currentPos[1])
          }
          this.tt.push(data[i][0])
          this.ss.push(data[i][N-2])
          this.vv.push(data[i][N-1])
          lines += data[i].join(',') + '\n'
        // data.concat(res.data.state.sx)
        }
        // console.log(this.xx, this.tt)
        console.log(this.currentPos)
        if (data.length)
          this.content += lines
          // this.content += '\n' + data.join(',')

        this.updateChart();

      });
    },
    fetchRunning() {
      this.message = this.message.split('').reverse().join('');
      axios.get('/zmot/api/is_idle', {
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
    addDefMove(){
      this.message = this.message.split('').reverse().join('');
      console.log(this.movePosStr )
      axios.post(`/zmot/api/move123`, {}).then((res) => {
          this.is_running = true
          if (!this.is_querying)
            this.startFetching()
          this.txtHistory += "move 3,4\n"
      });
    },
    addPath(){
      this.message = this.message.split('').reverse().join('');
      console.log(this.movePosStr )
      axios.post(`/zmot/api/move`, {
            is_relative: this.is_relative, 
            args: this.movePosStr 
        }).then((res) => {
          this.is_running = true
          if (!this.is_querying)
            this.startFetching()
      });
    },
    addZcode(){
      console.log(this.zmovePosStr)
      axios.post(`/zmot/api/zcode`, this.zmovePos ).then((res) => {
          this.is_running = true
          if (!this.is_querying)
            this.startFetching()
          this.txtHistory += this.zmovePosStr + "\n"
      });
    },
    moveStop() {
      axios.post(`/zmot/api/stop`, {
            params: {}
        }).then((res) => {
        // this.stopQuerying()
        this.txtHistory += "stop\n"
      });
    },
    movePause() {
      axios.post(`/zmot/api/pause`, {
            params: {}
        }).then((res) => {
        this.txtHistory += "pause\n"
      });
    },
    moveResume() {
      axios.post(`/zmot/api/resume`, {
            params: {}
        }).then((res) => {
        this.txtHistory += "resume\n"
      });
    },
    moveClear() {
      axios.post(`/zmot/api/clear`, {
            params: {}
        }).then((res) => {
        this.txtHistory += "clear\n"
      });
    },
    resetMq() {
      axios.post(`/zmot/api/reset`, {
            params: {}
        }).then((res) => {
        this.stopQuerying()
        this.is_running = false
        this.currentPos = [0,0]
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
          data: [1,2,3,4]
        },
        yAxis: {
          // data: [1,2,3]
        },
        series: [{
          name: 'loss',
          type: 'line',
          data: [1,4,9,16]
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
        legend: {
          data:['xpos','ypos','spos', 'vel']
        },
        toolbox:{
          show:true,
          feature:{
              dataZoom:{
                  // yAxisIndex: "none"
              }
          }
        },
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
        },
        {
          name: 'spos',
          type: 'line',
          data: this.ss
        },
        {
          name: 'vel',
          type: 'line',
          data: this.vv
        }]
      }
      this.chart.setOption(opt)
    }
  }
};
</script>

<style scoped>
.chart-container{
  position: relative;
  width: 100%;
  height: calc(100vh - 84px);
}
.content{
  position: relative;
  width: 40%;
  height: 500px;
}
.txtHistory{
  position: relative;
  width: 40%;
  height: 500px;
}
</style>