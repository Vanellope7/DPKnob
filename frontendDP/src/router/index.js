import Vue from 'vue'
import Router, {createRouter, createWebHistory} from 'vue-router'

const Index = () => import('../views/Index/Index')
const Base = () => import('../views/Base/Base')
const DPRisk = () => import('../views/DPRisk/DPRisk')
const DPDecisionMaker = () => import("../views/DPDecisionMaker/DPDecisionMaker")
const HOPs = () => import("../views/HOPs/HOPs")
const Tree = () => import("../views/Tree/Tree")
const Main = () => import("../views/Main/Main")


const routes = [
  {
    path: '/',
    name: 'Index',
    component: Index,
    redirect: 'Main',
    children: [
      {
        path: '/Base',
        name: 'Base',
        component: Base,
      },
      {
        path: '/DPRisk',
        name: 'DPRisk',
        component: DPRisk,
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
      {
        path: '/Tree',
        name: 'Tree',
        component: Tree,
      },
    ],

  },
  {
    path: '/Main',
    name: 'Main',
    component: Main,
  },

]

const router = createRouter({
  routes,
  history: createWebHistory()
})

export default router