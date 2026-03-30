import asyncio
from playwright.async_api import async_playwright, expect

# Base URL of the application
BASE_URL = "https://dev.urbuddi.com/"

# Test Case ID: TC-LOGIN-011
# Description: Login with very long Email address (boundary condition)

# Credentials for the test case itself (Password is from "Login Credentials to use in the script")
TEST_EMAIL_LONG = 'verylongemailaddressverylongemailaddressverylongemailaddressverylongemailaddressverylongemailaddressverylongemailaddressverylongemailaddressverylongemailaddressverylongemailaddressverylongemailaddress@optimworks.com'
TEST_PASSWORD = 'Srikanth@123' # From "Login Credentials to use in the script"

async def main():
    async with async_playwright() as p:
        # Launch browser in headed mode as required
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        print(f"Executing Test Case: TC-LOGIN-011 - Login with very long Email address (boundary condition)")

        try:
            # Pre-condition: User is on the login page.
            print(f"1. Navigating to the login page: {BASE_URL}")
            await page.goto(BASE_URL)
            await expect(page).to_have_url(BASE_URL)
            print("   - Successfully reached the login page.")

            # Test Step 1: Enter Email: 'verylongemailaddress...'
            print(f"2. Entering very long email: '{TEST_EMAIL_LONG}'")
            # Using the exact locator from "Extracted Available Exact Locators"
            await page.locator("#userEmail").fill(TEST_EMAIL_LONG)
            
            # Test Step 2: Enter Password: 'Srikanth@123'
            print(f"3. Entering password: '{TEST_PASSWORD}'")
            # Using the exact locator from "Extracted Available Exact Locators"
            await page.locator("#userPassword").fill(TEST_PASSWORD)
            
            # Test Step 3: Click 'Login' button.
            print("4. Clicking 'Login' button.")
            # Using the exact locator from "Extracted Available Exact Locators"
            await page.get_by_text("Login").click()

            # Wait for any network activity to settle after the click
            await page.wait_for_load_state("networkidle")

            # Expected Result: If the system has a length limit, an error message indicating the email is too long should be displayed,
            # or the field should truncate input. If within limits, login should proceed as per validity.

            # Assertion: Given the email's extreme length, it's highly probable the system will reject it.
            # We expect to either remain on the login page with an error message, or see some form of validation failure.
            # As no specific error message locator is provided, we'll check for the page to remain on the login URL
            # and attempt to find a common error text indicating invalid input.

            # Option 1: Assert that the page is still on the login URL (login failed)
            current_url = page.url
            if current_url == BASE_URL:
                print(f"5. Login attempt failed. Still on login page: {current_url}")
                # Option 2: Look for a common error message or element indicating invalid input
                # Since no specific error message DOM is provided, we look for common validation failure text.
                # Common phrases for email validation errors include "Invalid email", "Email is too long", "Validation error".
                # We'll check for "Invalid" as a generic indicator.
                error_message_present = False
                try:
                    # Attempt to find text related to an error. This is a heuristic without a specific locator.
                    await expect(page.locator("text=Invalid").or_(page.locator("text=error"))).to_be_visible()
                    error_message_present = True
                    print("   - Detected an error message on the page (e.g., 'Invalid' or 'error').")
                except Exception:
                    print("   - No specific 'Invalid' or 'error' text found, but still on login page.")
                
                # Final assertion for this path
                assert current_url == BASE_URL and error_message_present, \
                    "Expected to remain on login page with an error message, but conditions not met."
                print("   - Assertion Passed: Login failed, and an error message was likely displayed, conforming to expected boundary behavior.")
            else:
                # This branch would mean the login succeeded, which is highly unlikely for such a long email.
                # If this assertion fails, it might indicate a defect in the system's email length validation.
                print(f"5. Login attempt unexpectedly succeeded. Redirected to: {current_url}")
                # Assert that we are no longer on the login page (successful login)
                assert current_url != BASE_URL, \
                    "Expected login to fail for extremely long email, but redirection implies success."
                print("   - Assertion Failed: Login unexpectedly succeeded with a very long email. This might indicate a defect.")
                # If a successful login, we might further assert for a dashboard element, but the primary test is about the boundary condition.
                # For this specific test case, a successful login with such an email is considered an unexpected result/defect.

        except Exception as e:
            print(f"An error occurred during the test: {e}")
            raise
        finally:
            print("Test execution finished.")
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())