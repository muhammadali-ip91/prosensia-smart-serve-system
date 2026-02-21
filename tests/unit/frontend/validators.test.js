/**
 * Validator Utility Tests
 * ========================
 * Tests for form input validation functions.
 *
 * Run: cd frontend && npx jest tests/unit/frontend/validators.test.js
 */

const validateEmail = (email) => {
    const pattern = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/;
    return pattern.test(email);
};

const validateEmployeeId = (id) => {
    const pattern = /^(ENG|KIT|RUN|ADM)-\d{3}$/;
    return pattern.test(id);
};

const validatePassword = (password) => {
    return password && password.length >= 6;
};

const validateRating = (rating) => {
    return Number.isInteger(rating) && rating >= 1 && rating <= 5;
};

const validateQuantity = (qty) => {
    return Number.isInteger(qty) && qty >= 1 && qty <= 10;
};

describe("Email Validator", () => {
    test("accepts valid email", () => {
        expect(validateEmail("user@prosensia.com")).toBe(true);
    });

    test("rejects empty string", () => {
        expect(validateEmail("")).toBe(false);
    });

    test("rejects missing @", () => {
        expect(validateEmail("userprosensia.com")).toBe(false);
    });

    test("rejects missing domain", () => {
        expect(validateEmail("user@")).toBe(false);
    });
});

describe("Employee ID Validator", () => {
    test("accepts valid engineer ID", () => {
        expect(validateEmployeeId("ENG-001")).toBe(true);
    });

    test("accepts valid kitchen ID", () => {
        expect(validateEmployeeId("KIT-001")).toBe(true);
    });

    test("accepts valid runner ID", () => {
        expect(validateEmployeeId("RUN-010")).toBe(true);
    });

    test("accepts valid admin ID", () => {
        expect(validateEmployeeId("ADM-001")).toBe(true);
    });

    test("rejects lowercase", () => {
        expect(validateEmployeeId("eng-001")).toBe(false);
    });

    test("rejects invalid prefix", () => {
        expect(validateEmployeeId("USR-001")).toBe(false);
    });

    test("rejects wrong digit count", () => {
        expect(validateEmployeeId("ENG-01")).toBe(false);
        expect(validateEmployeeId("ENG-0001")).toBe(false);
    });
});

describe("Password Validator", () => {
    test("accepts valid password", () => {
        expect(validatePassword("test123")).toBe(true);
    });

    test("rejects short password", () => {
        expect(validatePassword("abc")).toBe(false);
    });

    test("rejects empty password", () => {
        expect(validatePassword("")).toBe(false);
    });

    test("rejects null", () => {
        expect(validatePassword(null)).toBe(false);
    });
});

describe("Rating Validator", () => {
    test("accepts 1-5", () => {
        for (let i = 1; i <= 5; i++) {
            expect(validateRating(i)).toBe(true);
        }
    });

    test("rejects 0", () => {
        expect(validateRating(0)).toBe(false);
    });

    test("rejects 6", () => {
        expect(validateRating(6)).toBe(false);
    });

    test("rejects decimal", () => {
        expect(validateRating(3.5)).toBe(false);
    });
});

describe("Quantity Validator", () => {
    test("accepts 1-10", () => {
        expect(validateQuantity(1)).toBe(true);
        expect(validateQuantity(5)).toBe(true);
        expect(validateQuantity(10)).toBe(true);
    });

    test("rejects 0", () => {
        expect(validateQuantity(0)).toBe(false);
    });

    test("rejects > 10", () => {
        expect(validateQuantity(11)).toBe(false);
    });

    test("rejects negative", () => {
        expect(validateQuantity(-1)).toBe(false);
    });
});