import Vue from 'vue'
import Router, {createRouter, createWebHistory} from 'vue-router'

const Index = () => import('../views/Index/Index')
const Base = () => import('../views/Base/Base')
const DPDecisionMaker = () => import("../views/DPDecisionMaker/DPDecisionMaker")
const HOPs = () => import("../views/HOPs/HOPs")


const routes = [
  {
    path: '/',
    name: 'Index',
    component: Index,
    redirect: 'Base',
    children: [
      {
        path: '/Base',
        name: 'Base',
        component: Base,
      },
      {
        path: '/DC',
        name: 'DPDecisionMaker',
        component: DPDecisionMaker,
      },
      {
        path: '/HOPs',
        name: 'HOPs',
        component: HOPs,
      },
    ]
  },

]

const router = createRouter({
  routes,
  history: createWebHistory()
})

export default router