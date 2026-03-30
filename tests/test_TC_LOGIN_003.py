import asyncio
from playwright.async_api import async_playwright, expect

async def main():
    async with async_playwright() as p:
        # 1. Launch the browser in headed mode as required.
        # This opens a visible browser window for the test execution.
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            # Navigate to the application's login page.
            # This fulfills the "Pre-conditions: User is on the login page."
            await page.goto("https://dev.urbuddi.com/")

            # Wait for the page to fully load and ensure network is idle.
            # This helps in mitigating flakiness on slower connections or rendering.
            await page.wait_for_load_state("networkidle")

            # --- Pre-condition Verification ---
            # Assert that the login page elements are visible, confirming we are on the correct page.
            # Using exact locators provided in the "Extracted Available Exact Locators" map.
            await expect(page.locator("#userEmail")).to_be_visible()
            await expect(page.locator("#userPassword")).to_be_visible()
            await expect(page.get_by_text("Login")).to_be_visible()
            print("Pre-conditions met: Login page elements are visible.")

            # --- Test Steps for TC-LOGIN-003: Login with Invalid Password ---

            # Step 1: Enter Email: 'srikanth123@optimworks.com'
            # Using the robust locator for the email input field from the provided options.
            # The email credential from "Login Credentials to use in the script" is used here.
            email_input_locator = page.locator("#userEmail")
            await email_input_locator.fill("srikanth123@optimworks.com")
            print("Step 1: Entered email 'srikanth123@optimworks.com'.")

            # Step 2: Enter Password: 'WrongPassword123'
            # Using the robust locator for the password input field from the provided options.
            # As per TC-LOGIN-003, we use the invalid password here.
            password_input_locator = page.locator("#userPassword")
            await password_input_locator.fill("WrongPassword123")
            print("Step 2: Entered password 'WrongPassword123' (invalid).")

            # Step 3: Click 'Login' button.
            # Using the robust locator for the Login button from the provided options.
            login_button_locator = page.get_by_text("Login")
            await login_button_locator.click()
            print("Step 3: Clicked 'Login' button.")

            # --- Expected Result Assertions ---

            # Expected Result 1: System should display an error message indicating invalid credentials.
            # The error message text "Invalid email or password" is explicitly mentioned in the Expected Result.
            # We use `get_by_text` as no specific locator for the error message element was provided
            # in the "Extracted Available Exact Locators" or "Form JSON DOM Representation".
            error_message_locator = page.get_by_text("Invalid email or password")
            await expect(error_message_locator).to_be_visible()
            print("Assertion Passed: Error message 'Invalid email or password' is displayed.")

            # Expected Result 2: User should remain on the login page.
            # We assert this by checking the current URL. Assuming the URL does not change on invalid login.
            await expect(page).to_have_url("https://dev.urbuddi.com/")
            print("Assertion Passed: User remained on the login page (URL: https://dev.urbuddi.com/).")

            print("\nTest Case TC-LOGIN-003: Login with Invalid Password - PASSED SUCCESSFULLY")

        except Exception as e:
            # If any assertion or step fails, catch the exception and report the failure.
            print(f"\nTest Case TC-LOGIN-003: FAILED due to an error: {e}")
            # Optionally, take a screenshot for debugging purposes on failure.
            await page.screenshot(path="tc_login_003_failure_screenshot.png")
        finally:
            # Ensure the browser is always closed, regardless of test outcome.
            await browser.close()
            print("Browser closed.")

# Run the asynchronous main function.
if __name__ == "__main__":
    asyncio.run(main())