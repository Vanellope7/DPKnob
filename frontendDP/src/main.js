import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import Plugin from 'v-fit-columns';
import * as ElIcons from "@element-plus/icons-vue";


const app = createApp(App)


for (const iconName in ElIcons) {
  app.component(iconName, ElIcons[iconName]);
}
app.use(ElementPlus);
app.use(Plugin)
app.use(router)
app.mount('#app')
app.config.warnHandler = (msg, instance, trace) => {}