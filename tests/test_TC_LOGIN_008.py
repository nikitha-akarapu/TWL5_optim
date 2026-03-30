import asyncio
from playwright.async_api import async_playwright, expect

async def test_login_with_malformed_email():
    """
    Test Case ID: TC-LOGIN-008
    Description: Login with Malformed Email (e.g., missing '@' or domain)
    Pre-conditions: User is on the login page.
    Test Steps:
    1. Enter Email: 'srikanth123optimworks.com'
    2. Enter Password: 'Srikanth@123'
    3. Click 'Login' button.
    Expected Result: System should display a client-side validation error message
                     for invalid email format (e.g., 'Please enter a valid email address').
                     User should remain on the login page.
    """
    async with async_playwright() as p:
        # Launch browser in headed mode as required
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            # Navigate to the login page
            # The base URL https://dev.urbuddi.com/ is assumed to be the login page
            await page.goto("https://dev.urbuddi.com/")
            print("Navigated to the login page.")

            # --- Test Steps for Malformed Email Login ---

            # Step 1: Enter Malformed Email 'srikanth123optimworks.com'
            # Using the exact locator provided: page.locator("#userEmail")
            email_input = page.locator("#userEmail")
            await email_input.fill("srikanth123optimworks.com")
            print("Entered malformed email.")

            # Step 2: Enter Password 'Srikanth@123'
            # Using the exact locator provided: page.locator("#userPassword")
            password_input = page.locator("#userPassword")
            await password_input.fill("Srikanth@123")
            print("Entered password.")

            # Step 3: Click 'Login' button
            # Using the exact locator provided: page.get_by_text("Login")
            login_button = page.get_by_text("Login")
            await login_button.click()
            print("Clicked Login button.")

            # --- Assertions for Expected Result ---

            # Assertion 1: System should display a client-side validation error message
            # for invalid email format ('Please enter a valid email address').
            # Since no specific locator for error messages is provided and the DOM is empty,
            # we use Playwright's robust get_by_text to locate the error message.
            error_message = page.get_by_text("Please enter a valid email address")
            await expect(error_message).to_be_visible()
            print("Assertion Passed: Client-side validation error message 'Please enter a valid email address' is displayed.")

            # Assertion 2: User should remain on the login page.
            # We can check if the URL is still the login page's URL
            await expect(page).to_have_url("https://dev.urbuddi.com/")
            print("Assertion Passed: User remains on the login page.")

            # Also, verify the email input field is still visible, confirming we haven't navigated away.
            await expect(email_input).to_be_visible()
            print("Assertion Passed: Email input field is still visible, confirming user is on login page.")

            print("\nTest Case TC-LOGIN-008: Login with Malformed Email - PASSED")

        except Exception as e:
            print(f"\nTest Case TC-LOGIN-008: Login with Malformed Email - FAILED: {e}")
            # Optionally take a screenshot on failure
            await page.screenshot(path="malformed_email_login_failure.png")
        finally:
            await browser.close()
            print("Browser closed.")

if __name__ == "__main__":
    # Run the asynchronous test function
    asyncio.run(test_login_with_malformed_email())