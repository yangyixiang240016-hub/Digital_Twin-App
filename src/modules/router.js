import {
  createRouter,
  createWebHistory,
  createWebHashHistory,
} from "vue-router";

const router = createRouter({
  // history: createWebHistory(),
  history: createWebHashHistory(
    import.meta.env.VITE_MODE === "production" ? "/sewage/" : "/"
  ),
  routes: [
    {
      path: "/",
      name: "首页",
      component: () => import("@/view/shouye/index.vue"),
    },
    {
      path: "/history",
      name: "历史数据",
      component: () => import("@/view/history/HistoryDataPage.vue"),
    },
    {
      path: "/trend",
      name: "进出水趋势",
      component: () => import("@/view/trend/TrendPage.vue"),
    },
    {
      path: "/offline/:process/:mode",
      name: "offline-runner",
      component: () => import("/src/modules/offline/pages/OfflineRunner.vue"),
    },
    {
      path: "/offline/result/:taskId",
      name: "offline-result",
      component: () => import("/src/modules/offline/pages/OfflineResult.vue"),
    },
  ],
  // routes: [{
  //     name: '首页',
  //     'component': () => import('@/view/test.vue')
  // }],
});

export default router;
