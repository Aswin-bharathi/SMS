module.exports = {
  root: true,
  env: {
    browser: true,
    es2021: true,
    node: true,
  },
  extends: [
    'plugin:vue/vue3-essential',
  ],
  rules: {
    // ✅ Disable multi-word component name rule
    'vue/multi-word-component-names': 'off',
    // ✅ Disable unused vars warning
    'no-unused-vars': 'warn',
  },
}
