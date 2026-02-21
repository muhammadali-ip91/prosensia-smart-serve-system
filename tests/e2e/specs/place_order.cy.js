/**
 * Order Placement E2E Tests
 */

describe("Place Order Flow", () => {
    beforeEach(() => {
        cy.loginAsEngineer();
    });

    it("should display menu items", () => {
        cy.url().should("include", "/menu");
        cy.contains("h1", "Menu").should("be.visible");
        cy.contains("button", "Add to Cart").should("be.visible");
    });

    it("should add item to cart", () => {
        cy.contains("button", "Add to Cart").first().click();
        cy.get('a[href="/cart"]').find("span").contains("1").should("be.visible");
    });

    it("should show cart summary before placing order", () => {
        cy.contains("button", "Add to Cart").first().click();
        cy.get('a[href="/cart"]').click();
        cy.contains("h3", "Order Summary").should("be.visible");
    });

    it("should place order successfully", () => {
        cy.contains("button", "Add to Cart").first().click();
        cy.get('a[href="/cart"]').click();
        cy.get('input[placeholder="e.g., Bay-12"]').clear().type("Bay-1");
        cy.contains("button", "Place Order").click();
        cy.contains("Order Placed").should("be.visible");
    });

    it("should show error for empty cart", () => {
        cy.visit("/cart");
        cy.contains("Your cart is empty").should("be.visible");
    });
});