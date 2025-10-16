const { config } = require('@commitlint/config-conventional');

module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: config.rules,
  ignores: [(message) => message.startsWith('Merge pull request')],
};
