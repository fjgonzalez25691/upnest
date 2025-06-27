import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/oauth2': {
        target: 'https://eu-south-2winbcddjo.auth.eu-south-2.amazoncognito.com',
        changeOrigin: true,
        secure: false,
      },
    },
  },

})
