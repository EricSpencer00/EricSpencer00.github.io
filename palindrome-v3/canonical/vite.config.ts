import path from "path"
import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"
import tailwindcss from "@tailwindcss/vite"

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: { alias: { "@": path.resolve(__dirname, "./src") } },
  // Dev hits the configured API origin, so streaming
  // behaviour is identical in both.
  server: {
    proxy: {
      "/api": {
        target: process.env.PAL_API || "https://palindrome-api.ericspencer.us",
        changeOrigin: true, secure: true,
      },
    },
  },
})
