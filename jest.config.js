/** @type {import('jest').Config} */
const config = {
  testEnvironment: 'jsdom',
  roots: ['<rootDir>/viewer'],
  collectCoverageFrom: ['viewer/**/*.js', '!viewer/model-viewer.min.js', '!viewer/coverage/**'],
  coverageDirectory: '<rootDir>/viewer/coverage',
  coverageReporters: ['text', 'lcov'],
};

module.exports = config;
