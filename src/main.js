import { createApp } from "vue";
import "./style.css";
import App from "./App.vue";
import router from "./modules/router";
import { DatePicker } from "ant-design-vue";
import "ant-design-vue/dist/reset.css";
import axios from "axios";

import { createPinia } from "pinia";

const app = createApp(App);
app.use(router);
app.use(DatePicker);
app.mount("#app");
axios.defaults.baseURL = import.meta.env.VITE_API_BASE;

app.use(createPinia());
// const scaleValue = window.innerWidth / 1920;
// document.body.style.transform = `scale(${scaleValue})`;
