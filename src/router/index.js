import Vue from 'vue'
import VueRouter from 'vue-router'
import HomeView from '../views/HomeView.vue'
import NotFound from '@/views/NotFound'
Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/about',
    name: 'about',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "about" */ '../views/AboutView.vue')
  },
  {
    path: '/demo',
    name: 'demo',
    component: () => import('../views/DemoView.vue')
  },
  {
    path: '/longquery',
    name: 'longquery',
    component: () => import('../views/LongQueryView.vue')
  },
  {
    path: '/longquery2',
    name: 'longquery2',
    component: () => import('../views/LongQueryView2.vue')
  },
  {
    path: '/zmcquery',
    name: 'zmcquery',
    component: () => import('../views/ZmcQueryView.vue')
  },
  {
    path: '/chart',
    name: 'chart',
    component: () => import('../views/LineView.vue')
  },
  {
    path: '/todo',
    name: 'todos',
    component: () => import('../views/TodoView.vue'),
    children: [{
      path: '/todo/:id',
      name: 'todo',
      component: () => import('../components/Todo/TodoItem.vue')
    }]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound
  }
]

const router = new VueRouter({
  mode:  'hash', // 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
