import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  test: {
    globals: true,
    environment: 'happy-dom',
    setupFiles: './src/test/setup.ts',
  },
  build: {
    // Optimize chunk size
    chunkSizeWarningLimit: 1000,
    rollupOptions: {
      output: {
        manualChunks: {
          // React core libraries
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          // AWS Amplify and authentication
          'aws-vendor': ['aws-amplify'],
          // UI libraries
          'ui-vendor': ['lucide-react'],
          // State management
          'state-vendor': ['zustand'],
          // Radix UI components (used by shadcn)
          'radix-vendor': [
            '@radix-ui/react-alert-dialog',
            '@radix-ui/react-avatar',
            '@radix-ui/react-label',
            '@radix-ui/react-scroll-area',
            '@radix-ui/react-slot',
          ],
        },
      },
    },
  },
})
