/**
 * Custom Cypress Commands
 */

// Login command
Cypress.Commands.add("login", (email, password) => {
    cy.visit("/login");
    cy.get('input[type="email"]').type(email);
    cy.get('input[type="password"]').type(password);
    cy.get('button[type="submit"]').click();
    cy.url().should("not.include", "/login");
});

// Login as engineer
Cypress.Commands.add("loginAsEngineer", () => {
    cy.login("engineer1@prosensia.com", "engineer123");
});

// Login as kitchen
Cypress.Commands.add("loginAsKitchen", () => {
    cy.login("kitchen1@prosensia.com", "kitchen123");
});

// Login as runner
Cypress.Commands.add("loginAsRunner", () => {
    cy.login("runner1@prosensia.com", "runner123");
});

// Login as admin
Cypress.Commands.add("loginAsAdmin", () => {
    cy.login("admin@prosensia.com", "admin123");
});

// API login (bypass UI)
Cypress.Commands.add("apiLogin", (email, password) => {
    cy.request({
        method: "POST",
        url: "http://localhost:8000/auth/login",
        body: {
            email,
            password: password || "engineer123",
        },
    }).then((response) => {
        window.localStorage.setItem(
            "access_token",
            response.body.access_token
        );
    });
});