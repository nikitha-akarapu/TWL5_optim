import asyncio
from playwright.async_api import async_playwright, expect

async def main():
    async with async_playwright() as p:
        # Requirement 1: Launch browser in headed mode
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # Pre-conditions: User is on the login page.
        # Navigate to the application's base URL which is the login page.
        await page.goto("https://dev.urbuddi.com/")

        # --- Test Case ID: TC-LOGIN-006 - Login with Missing Password ---

        # Step 1: Enter Email: 'srikanth123@optimworks.com'
        # Using the exact locator provided: page.locator("#userEmail")
        await page.locator("#userEmail").fill("srikanth123@optimworks.com")
        print("Entered email: srikanth123@optimworks.com")

        # Step 2: Leave Password field empty.
        # No action needed as the field is already empty by default.
        # We explicitly verify it's empty by not interacting with page.locator("#userPassword") to fill it.
        print("Password field left empty.")

        # Step 3: Click 'Login' button.
        # Using the exact locator provided: page.get_by_text("Login")
        await page.get_by_text("Login").click()
        print("Clicked 'Login' button.")

        # Expected Result:
        # System should display a client-side validation error message for the missing password
        # (e.g., 'Password is required', 'Please enter your password').

        # Assertion 1: Check for the visibility of the password required error message.
        # As per the prompt, example error messages are 'Password is required', 'Please enter your password'.
        # We will check for 'Password is required' as a representative example.
        # Since no specific locator for the error message is provided, we use get_by_text
        # which is robust for text content.
        password_error_message = page.get_by_text("Password is required", exact=True)
        await expect(password_error_message).to_be_visible()
        print("Assertion Passed: 'Password is required' error message is visible.")

        # Assertion 2: User should remain on the login page.
        # The URL should still be the base URL if the login was unsuccessful due to client-side validation.
        await expect(page).to_have_url("https://dev.urbuddi.com/")
        print("Assertion Passed: User remained on the login page.")

        print("Test Case TC-LOGIN-006: Login with Missing Password - PASSED")

        await browser.close()
        print("Browser closed.")

if __name__ == "__main__":
    asyncio.run(main())