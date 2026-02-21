/**
 * Cypress E2E Test Configuration
 */

module.exports = {
    e2e: {
        baseUrl: "http://localhost:3000",
        specPattern: "specs/**/*.cy.js",
        fixturesFolder: "fixtures",
        supportFile: "support/e2e.js",
        viewportWidth: 375,
        viewportHeight: 812,
        defaultCommandTimeout: 10000,
        requestTimeout: 15000,
        video: false,
        screenshotOnRunFailure: true,
        retries: {
            runMode: 2,
            openMode: 0,
        },
    },
};