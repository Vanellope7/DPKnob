import Vue from 'vue'
import Router, {createRouter, createWebHashHistory} from 'vue-router'

const Base = () => import('../components/Base')

const routes = [
  {
    path: '/',
    name: 'Base',
    component: Base,
  }
]

const router = createRouter({
  routes,
  history: createWebHashHistory()
})

export default router