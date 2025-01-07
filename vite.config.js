import { defineConfig } from "vite";
import litestar from "litestar-vite-plugin";
import vue from '@vitejs/plugin-vue'
import path from 'path'

const ASSET_URL = process.env.ASSET_URL || "/static/";
const VITE_PORT = process.env.VITE_PORT || "5173";
const VITE_HOST = process.env.VITE_HOST || "localhost";
export default defineConfig({
  base: `${ASSET_URL}`,
  server: {
    host: "0.0.0.0",
    port: +`${VITE_PORT}`,
    cors: true,
    hmr: {
      host: `${VITE_HOST}`,
    },
  },
  plugins: [
    litestar({
      input: 'resources/js/app.js',
      ssr: 'resources/js/ssr.js',
      refresh: true,
      assetUrl: `${ASSET_URL}`,
      bundleDirectory: "app/static",
    }),
    vue({
      template: {
          transformAssetUrls: {
              base: null,
              includeAbsolute: false,
          },
      },
    }),
  ],
  resolve: {
		alias: {
			"@/": path.join(__dirname,"resources/js/"),
		},
	},
});
