import Vue from 'vue'
import Vuex from 'vuex'

import * as actions from './actions';
import * as getters from './getters';
Vue.use(Vuex)

// 创建初始应用全局状态变量
const state = {
  todoList: [],  // 指我们的待办事项列表数据
  menuOpen: false // 移动端的时候菜单是否开启
};

// 定义所需的 mutations
const mutations = {
  EDITTODOLIST(state, data) { // 定义名为 EDITTODE函数用作改变todoList的值
    state.todoList = data;
  },
  MENUSWITCH(state) { // 定义名为 MENUOPEN函数用作改变menuOpen的值
    state.menuOpen = !state.menuOpen;
  }
};

export default new Vuex.Store({
  actions,
  getters,
  state,
  mutations,
  modules: {
  }
})
