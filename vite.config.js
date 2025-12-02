import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import Components from "unplugin-vue-components/vite";
import { AntDesignVueResolver } from "unplugin-vue-components/resolvers";
import { loadEnv } from "vite";
import * as path from "path";

// export default 的定义函数
export default defineConfig(({ mode }) => {
  // 加载环境变量
  const env = loadEnv(mode, process.cwd()); // 推荐使用 process.cwd()
  return {
    // 插件配置
    plugins: [
      vue(), // 使用 Vue 插件
      Components({
        resolvers: [
          AntDesignVueResolver({
            importStyle: "less", // 指定 Ant Design Vue 样式以 less 格式引入
          }),
        ],
      }),
    ],
    // 公共路径配置，适合打包后的相对路径
    base: env.VITE_MODE === "production" ? "/sewage/" : "/", // Vite 中使用 'base' 而不是 'publicPath'
    resolve: {
      // 配置路径别名
      alias: {
        "@": path.resolve(__dirname, "src"), // 将 '@' 映射到 'src' 目录
      },
    },

    // 定义 Vue 特性标志，消除控制台警告
    define: {
      __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: "false",
    },

    // 代理配置
    server: {
      proxy: {
        "/api": {
          target: "http://192.168.3.51:8000", // Flask 运行地址
          changeOrigin: true,
          // 不重写路径，保持 /api 前缀
        },
        // 给 .91 那台后端走代理
        "/alt": {
          target: "http://192.168.3.91:8000", // 直接配置后端地址
          changeOrigin: true,
          secure: false,
          rewrite: (p) => p.replace(/^\/alt/, ""),
          configure: (proxy, options) => {
            proxy.on("error", (err, req, res) => {
              console.log("proxy error", err);
            });
            proxy.on("proxyReq", (proxyReq, req, res) => {
              console.log(
                "Sending Request to the Target:",
                req.method,
                req.url
              );
            });
            proxy.on("proxyRes", (proxyRes, req, res) => {
              console.log(
                "Received Response from the Target:",
                proxyRes.statusCode,
                req.url
              );
            });
          },
        },
      },
    },
    build: {
      sourcemap: false, // 不生成 source map
      terserOptions: {
        compress: {
          // 打包时清除 console 和 debug 相关代码
          drop_console: true,
          drop_debugger: true,
        },
      },
    },
  };
});
