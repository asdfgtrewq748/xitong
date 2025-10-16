let viteEnv;
try {
  // eslint-disable-next-line no-undef
  viteEnv = import.meta && import.meta.env ? import.meta.env : null;
} catch (error) {
  viteEnv = null;
}

export function getApiBase() {
  if (viteEnv && viteEnv.VITE_API_BASE_URL) {
    return viteEnv.VITE_API_BASE_URL;
  }
  if (typeof process !== 'undefined' && process.env) {
    if (process.env.VUE_APP_API_BASE_URL) {
      return process.env.VUE_APP_API_BASE_URL;
    }
    if (process.env.VITE_API_BASE_URL) {
      return process.env.VITE_API_BASE_URL;
    }
  }
  return '/api';
}
