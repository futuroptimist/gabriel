/**
 * Commitlint configuration enforcing Conventional Commits with 100 char body/footer lines.
 * @type {import('@commitlint/types').UserConfig}
 */
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'body-max-line-length': [2, 'always', 100],
    'footer-max-line-length': [2, 'always', 100],
  },
};
