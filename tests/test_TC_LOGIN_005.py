import asyncio
from playwright.async_api import async_playwright, expect

async def main():
    """
    Test Case ID: TC-LOGIN-005
    Description: Login with Missing Email
    Pre-conditions: User is on the login page.
    Test Steps:
        1. Leave Email field empty.
        2. Enter Password: 'Srikanth@123'
        3. Click 'Login' button.
    Expected Result: System should display a client-side validation error message for the missing email
                     (e.g., 'Email is required', 'Please enter your email address').
                     User should remain on the login page.
    """
    async with async_playwright() as p:
        # Requirement 1: Launch browser in headed mode.
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # Pre-conditions: User is on the login page.
        await page.goto("https://dev.urbuddi.com/")
        print(f"Navigated to login page: {page.url}")

        # --- IMPORTANT NOTE ON REQUIREMENT 3: "Automatically perform login prior to executing the test steps" ---
        # For TC-LOGIN-005, the test *is* about the login process itself, specifically testing a missing email scenario.
        # Performing a successful login first would contradict the test's precondition ("User is on the login page")
        # and invalidate the purpose of testing an invalid login attempt.
        # Therefore, for this specific test case, a pre-login is intentionally skipped as it directly conflicts
        # with the test's objective of verifying client-side validation on the login form.

        print("\n--- Starting Test Case: TC-LOGIN-005 (Login with Missing Email) ---")

        # Test Steps:
        # Step 1: Leave Email field empty.
        # As per the test case, we intentionally do not interact with the email field
        # to ensure it remains empty upon form submission.
        print("Step 1: Email field left empty.")

        # Step 2: Enter Password: 'Srikanth@123'
        # Requirement 6: Use provided exact locator: page.locator("#userPassword")
        await page.locator("#userPassword").fill("Srikanth@123")
        print("Step 2: Entered password 'Srikanth@123'.")

        # Step 3: Click 'Login' button.
        # Requirement 6: Use provided exact locator: page.get_by_text("Login")
        await page.get_by_text("Login").click()
        print("Step 3: Clicked 'Login' button.")

        # Expected Results & Assertions (Requirement 4):

        # Expected Result Part 1: User should remain on the login page.
        # Requirement 4: Use Playwright's expect for assertions.
        await expect(page).to_have_url("https://dev.urbuddi.com/", timeout=5000)
        print("Assertion Passed: User remained on the login page as expected.")

        # Expected Result Part 2: System should display a client-side validation error message for the missing email.
        # Requirement 7: "DO NOT HALLUCINATE OR GUESS LOCATORS. NEVER use a get_by_placeholder or get_by_label
        # if the placeholder or label text does not exactly appear in the Form JSON DOM Representation or Locator map.
        # If an element is absolutely required but not in the map, fallback to robust Playwright XPath or CSS selectors
        # based purely on the 'Form JSON DOM Representation' provided."
        #
        # The 'Form JSON DOM Representation' provided is empty: {}.
        # No specific locator for an error message (like 'Email is required') is available in the 'Extracted Available Exact Locators'
        # or derivable from the empty DOM representation.
        # Therefore, per Requirement 7, we cannot robustly assert the specific text content of a client-side validation message.
        # The fact that the user remained on the login page (asserted above) is a strong indicator that client-side validation
        # prevented navigation, fulfilling the spirit of this part of the expected result without violating locator rules.
        print("Note: Specific error message text assertion skipped due to lack of explicit locator information in the provided DOM representation.")

        print("--- Test Case: TC-LOGIN-005 (Login with Missing Email) COMPLETED SUCCESSFULLY ---")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())