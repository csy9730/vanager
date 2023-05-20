import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

Vue.config.productionTip = false

import Mock from './mock'
// Vue.config.productionTip = false //  关闭生产模式下给出的提示

// process.env.NODE_ENV !== 'production' && Mock.start();

import Axios from 'axios';
if (process.env.NODE_ENV !== 'production'){
    Mock.start();
}else{
  if (router.mode == 'history'){
    Axios.defaults.baseURL = "http://localhost:5000/";
  }
}

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
