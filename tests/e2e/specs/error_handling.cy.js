/**
 * Error Handling E2E Tests
 */

describe("Error Handling", () => {
    it("should show 404 for invalid routes", () => {
        cy.visit("/nonexistent-page", {
            failOnStatusCode: false,
        });
        cy.contains("Page Not Found").should("be.visible");
    });

    it("should handle network errors gracefully", () => {
        cy.on("uncaught:exception", () => false);
        cy.loginAsEngineer();
        cy.intercept("GET", "http://localhost:8000/menu*", {
            forceNetworkError: true,
        });
        cy.visit("/menu");
        cy.get("h1.page-title").should("contain.text", "Menu");
    });

    it("should redirect to login when not authenticated", () => {
        cy.clearLocalStorage();
        cy.visit("/menu");
        cy.url().should("include", "/login");
    });
});