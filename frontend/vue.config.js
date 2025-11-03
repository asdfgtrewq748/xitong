const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  
  // 生产构建优化
  productionSourceMap: false,
  
  // 确保代码分割正常工作
  configureWebpack: {
    optimization: {
      splitChunks: {
        chunks: 'all',
        cacheGroups: {
          // 第三方库单独打包
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'chunk-vendors',
            priority: 10,
          },
          // Element Plus 单独打包
          elementPlus: {
            test: /[\\/]node_modules[\\/]element-plus[\\/]/,
            name: 'chunk-element-plus',
            priority: 20,
          },
          // ECharts 单独打包（体积大）
          echarts: {
            test: /[\\/]node_modules[\\/]echarts[\\/]/,
            name: 'chunk-echarts',
            priority: 20,
          },
        },
      },
    },
  },
  
  devServer: {
    proxy: {
      '/api': {
        target: process.env.VUE_APP_API_PROXY || 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
