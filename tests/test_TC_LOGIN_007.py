import asyncio
from playwright.async_api import async_playwright, expect

# Constants for the test environment
BASE_URL = "https://dev.urbuddi.com/"
LOGIN_URL = "https://dev.urbuddi.com/login"
DASHBOARD_URL = "https://dev.urbuddi.com/dashboard"  # Assuming this is the URL after successful login

# Login Credentials provided for the script
TEST_EMAIL = "srikanth123@optimworks.com"
TEST_PASSWORD = "Srikanth@123"

async def test_login_with_empty_fields(page):
    """
    Test Case ID: TC-LOGIN-007
    Description: Login with both Email and Password fields empty
    Pre-conditions: User is on the login page.
    Expected Result: System should display client-side validation error messages
                     for both missing email and missing password fields.
                     User should remain on the login page.
    """
    print("\n--- Executing Test Case: TC-LOGIN-007 (Login with empty fields) ---")

    # Navigate to the base URL, which should redirect to the login page.
    await page.goto(BASE_URL)
    # Pre-condition check: Ensure the user is on the login page.
    # The application typically redirects from BASE_URL to /login.
    await expect(page).to_have_url(LOGIN_URL)
    print("Pre-condition met: User is on the login page.")

    # Test Steps:
    # Step 1: Leave Email field empty.
    # Step 2: Leave Password field empty.
    # These fields are left empty by not interacting with them after navigation.
    print("Steps 1 & 2: Email and Password fields are left empty by default.")

    # Step 3: Click 'Login' button.
    # Using the exact locator provided: page.get_by_text("Login")
    login_button = page.get_by_text("Login")
    await login_button.click()
    print("Step 3: Clicked 'Login' button.")

    # Expected Result Assertions:
    # 1. User should remain on the login page.
    await expect(page).to_have_url(LOGIN_URL)
    print("Assertion Passed: User remained on the login page.")

    # 2. System should display client-side validation error messages.
    # NOTE: Specific locators for client-side validation error messages (e.g., their text or specific HTML elements)
    # are NOT provided in the 'Form JSON DOM Representation: {}' or 'Extracted Available Exact Locators'.
    # As per strict instructions ("DO NOT HALLUCINATE OR GUESS LOCATORS"),
    # specific assertions for their visibility or text content cannot be performed.
    print("Assertion Note: Cannot verify specific client-side validation error messages due to missing locator information for them.")

    print("--- Test Case TC-LOGIN-007 Completed ---")


async def perform_successful_login_and_open_leave_application(page, email, password):
    """
    Helper function to demonstrate successful login using provided credentials.
    This addresses the overall feature context and Requirement 3.
    """
    print("\n--- Demonstrating Automatic Successful Login (Requirement 3) ---")

    # Navigate to the login page
    await page.goto(BASE_URL)
    await expect(page).to_have_url(LOGIN_URL)
    print("Navigated to login page for successful login demonstration.")

    # Fill email field using the exact locator provided: page.locator("#userEmail")
    await page.locator("#userEmail").fill(email)
    print(f"Filled Email field with: {email}")

    # Fill password field using the exact locator provided: page.locator("#userPassword")
    await page.locator("#userPassword").fill(password)
    print("Filled Password field.")

    # Click login button using the exact locator provided: page.get_by_text("Login")
    await page.get_by_text("Login").click()
    print("Clicked 'Login' button.")

    # Assert navigation to the dashboard after successful login.
    # It's good practice to wait for the URL change explicitly.
    await page.wait_for_url(DASHBOARD_URL)
    await expect(page).to_have_url(DASHBOARD_URL)
    print("Assertion Passed: Successfully logged in and landed on the dashboard.")

    # Open Leave Application (as mentioned in the overall feature description)
    # NOTE: The prompt mentions "then open Leave Application", but no specific
    # locators or DOM representation for the 'Leave Application' link/button are provided.
    # Therefore, this specific step cannot be automated as per the strict requirements
    # ("DO NOT HALLUCINATE OR GUESS LOCATORS").
    print("Note: 'Open Leave Application' step cannot be fully automated as no locators were provided for it.")
    # If a locator were available, it might look like:
    # await page.get_by_text("Leave Application").click()
    # await expect(page).to_have_url("https://dev.urbuddi.com/leave-application") # Assuming a URL for Leave Application

    print("--- Successful Login Demonstration Completed ---")


async def main():
    """
    Main function to execute the test script.
    Launches browser in headed mode as required.
    """
    async with async_playwright() as p:
        # Launch browser in headed mode
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # First, execute the specific test case TC-LOGIN-007 (Login with empty fields).
        # This test ensures its pre-conditions (being on the login page) are met independently.
        await test_login_with_empty_fields(page)

        # Then, demonstrate the automatic successful login using provided credentials (Requirement 3).
        # This also addresses the broader feature context of "Login... then open Leave Application".
        # This will navigate to the login page again, effectively resetting the state.
        await perform_successful_login_and_open_leave_application(page, TEST_EMAIL, TEST_PASSWORD)

        # Close the browser after all tests are done
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())