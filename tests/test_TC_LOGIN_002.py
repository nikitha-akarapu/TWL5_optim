import asyncio
from playwright.async_api import async_playwright, expect

async def main():
    """
    Tests that the system prevents login with an invalid (unregistered) email address.
    Test Case ID: TC-LOGIN-002
    """
    async with async_playwright() as p:
        # Requirement 1: Launch browser in headed mode
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            print("--- Starting Test TC-LOGIN-002: Verify invalid login ---")

            # Pre-condition: User is on the login page.
            # Navigate to the application URL
            print("Navigating to https://dev.urbuddi.com/")
            await page.goto("https://dev.urbuddi.com/")

            # Verify that the login page elements are visible
            # We use `to_be_visible` to ensure the page has loaded and is ready for interaction.
            await expect(page.locator("#userEmail")).to_be_visible(timeout=10000)
            await expect(page.locator("#userPassword")).to_be_visible()
            await expect(page.get_by_text("Login")).to_be_visible()
            print("Successfully navigated to the login page and verified elements.")

            # Note on Requirement 3: "Automatically perform login using the credentials provided above
            # prior to executing the test steps."
            # For TC-LOGIN-002, the test *is* about the login process itself, specifically an *invalid* login attempt.
            # Performing a successful login beforehand would contradict the purpose of this specific test case.
            # Therefore, we proceed directly to the invalid login attempt as per the test steps.

            # Test Step 1: Enter Email: 'invalid@optimworks.com' (any unregistered email) in the Email/Username field.
            invalid_email = 'invalid@optimworks.com'
            print(f"Entering invalid email: '{invalid_email}' into the Email/Username field.")
            await page.locator("#userEmail").fill(invalid_email)

            # Test Step 2: Enter Password: 'Srikanth@123' in the Password field.
            # Using the password specified in the test case details and "Login Credentials" section.
            password = 'Srikanth@123'
            print(f"Entering password: '{password}' into the Password field.")
            await page.locator("#userPassword").fill(password)

            # Test Step 3: Click the 'Login' button.
            print("Clicking the 'Login' button.")
            await page.get_by_text("Login").click()

            # Test Step 4: Verify that an appropriate error message is displayed.
            # Expected Result: System displays an error message indicating invalid credentials or that the email is not registered.
            # As no specific locator for the error message is provided in the DOM,
            # we use Playwright's robust `get_by_text` to locate the expected error message content.
            error_message_text = "Invalid credentials" # One of the example error messages
            print(f"Verifying that the error message '{error_message_text}' is displayed.")
            await expect(page.get_by_text(error_message_text)).to_be_visible(timeout=10000)
            print(f"Assertion Passed: Error message '{error_message_text}' is displayed.")

            # Test Step 5: Verify that the user remains on the login page or is redirected back to it.
            # We verify the URL and the continued presence of login form elements.
            print("Verifying that the user remains on the login page.")
            await expect(page).to_have_url("https://dev.urbuddi.com/")
            await expect(page.locator("#userEmail")).to_be_visible() # Email field should still be present
            await expect(page.locator("#userPassword")).to_be_visible() # Password field should still be present
            print("Assertion Passed: User remains on the login page.")

            print("\nTC-LOGIN-002: Test Passed - Invalid login attempt correctly prevented access, displayed an error message, and kept the user on the login page.")

        except Exception as e:
            print(f"\nTC-LOGIN-002: Test Failed - An unexpected error occurred: {e}")
            # Optionally, take a screenshot on failure for debugging
            await page.screenshot(path="screenshot_on_failure_TC-LOGIN-002.png")
            raise # Re-raise the exception to indicate a test failure

        finally:
            # Close the browser
            print("Closing the browser.")
            await browser.close()

# Requirement 2: The code should be fully self-contained and runnable.
if __name__ == "__main__":
    asyncio.run(main())