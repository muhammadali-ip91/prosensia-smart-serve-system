/**
 * Order Tracking E2E Tests
 */

describe("Order Tracking", () => {
    beforeEach(() => {
        cy.loginAsEngineer();
    });

    it("should show progress bar on tracking page", () => {
        // Place an order first
        cy.contains("button", "Add to Cart").first().click();
        cy.get('a[href="/cart"]').click();
        cy.get('input[placeholder="e.g., Bay-12"]').clear().type("Bay-1");
        cy.contains("button", "Place Order").click();
        cy.contains("a", "Track Order").click();

        cy.contains("Order Progress").should("be.visible");
    });

    it("should show order history", () => {
        cy.visit("/orders");
        cy.get("h1.page-title").should("contain.text", "My Orders");
    });
});