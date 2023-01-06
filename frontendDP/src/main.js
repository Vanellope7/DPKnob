import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import Plugin from 'v-fit-columns';


const app = createApp(App)

app.use(ElementPlus)
app.use(Plugin)
app.use(router)
app.mount('#app')
app.config.warnHandler = (msg, instance, trace) => {}