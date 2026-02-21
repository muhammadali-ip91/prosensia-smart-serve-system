/**
 * Login Flow E2E Tests
 */

describe("Login Page", () => {
    beforeEach(() => {
        cy.visit("/login");
    });

    it("should display login form", () => {
        cy.get('input[type="email"]').should("be.visible");
        cy.get('input[type="password"]').should("be.visible");
        cy.get('button[type="submit"]').should("be.visible");
    });

    it("should login as engineer successfully", () => {
        cy.get('input[type="email"]').type("engineer1@prosensia.com");
        cy.get('input[type="password"]').type("engineer123");
        cy.get('button[type="submit"]').click();
        cy.url().should("include", "/menu");
    });

    it("should show error for invalid credentials", () => {
        cy.get('input[type="email"]').type("engineer1@prosensia.com");
        cy.get('input[type="password"]').type("wrong");
        cy.get('button[type="submit"]').click();
        cy.url().should("include", "/login");
    });

    it("should not submit empty form", () => {
        cy.get('button[type="submit"]').click();
        cy.url().should("include", "/login");
    });
});