import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": {
        target: "http://167.71.179.244:5001",
        changeOrigin: true,
      },
    },
  },
});
