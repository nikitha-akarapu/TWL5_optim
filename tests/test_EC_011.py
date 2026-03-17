from playwright.async_api import async_playwright, expect
import asyncio
import random
import string

# Define constants for better readability and easier modification
BASE_URL = "https://dev.urbuddi.com/"
ADMIN_EMAIL = "admin@example.com" # IMPORTANT: Replace with actual administrator/HR email for the dev environment
ADMIN_PASSWORD = "password123"    # IMPORTANT: Replace with actual administrator/HR password for the dev environment

async def test_invalid_phone_number_employee_creation():
    """
    Test Case ID: EC-011
    Description: Verify employee creation fails with non-numeric input in 'Phone Number' field.
    """
    async with async_playwright() as p:
        # Launch a Chromium browser instance. Set headless=False to watch the browser actions.
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            # --- Pre-conditions: User is logged in as an administrator/HR and is on the 'Add Employee' form. ---

            print("--- Starting Test EC-011 ---")

            # 1. Navigate to the login page
            print(f"Navigating to login page: {BASE_URL}")
            await page.goto(BASE_URL)
            # Ensure we are on the login page before proceeding
            await expect(page).to_have_url(f"{BASE_URL}login")

            # 2. Perform login as administrator/HR
            print("Attempting to log in as administrator/HR...")
            # Fill email field (using placeholder as a robust locator)
            await page.fill('input[placeholder="Email"]', ADMIN_EMAIL)
            # Fill password field (using placeholder as a robust locator)
            await page.fill('input[placeholder="Password"]', ADMIN_PASSWORD)
            # Click the 'Sign In' button
            await page.click('button:has-text("Sign In")')

            # Wait for navigation after login. Assuming it redirects to the employees listing page.
            # Adjust URL if it goes to a dashboard first, then requires a click to 'Employees'.
            await page.wait_for_url(f"{BASE_URL}employees")
            print("Login successful. Now on employees page.")

            # 3. Navigate to the 'Add Employee' form.
            # Click the 'Create Employee' button to open the add employee form/modal
            print("Clicking 'Create Employee' button to open the form...")
            await page.click('button:has-text("Create Employee")')

            # Wait for the "Create Employee" form/modal to become visible.
            # Assuming there's a header with 'Create Employee' text within the form.
            await expect(page.locator('h1:has-text("Create Employee")')).to_be_visible()
            print("Successfully navigated to 'Create Employee' form.")

            # --- Test Steps ---

            # Generate unique data for other mandatory fields to avoid conflicts
            unique_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            first_name = f"TestFN_{unique_id}"
            last_name = f"TestLN_{unique_id}"
            email = f"test_{unique_id}@example.com" # Use a unique email
            job_title = "Automation QA"
            department = "Engineering"

            # Fill in all other mandatory fields with valid data.
            print("Filling in other mandatory fields with valid data...")
            await page.fill('input[name="firstName"]', first_name)
            await page.fill('input[name="lastName"]', last_name)
            await page.fill('input[name="email"]', email)
            await page.fill('input[name="jobTitle"]', job_title)
            await page.fill('input[name="department"]', department)

            # Enter non-numeric characters in the 'Phone Number' field.
            non_numeric_phone_input = 'abc1234567'
            print(f"Entering non-numeric phone number: '{non_numeric_phone_input}'")
            # Using 'name="phoneNumber"' as a probable locator for the phone number input.
            await page.fill('input[name="phoneNumber"]', non_numeric_phone_input)

            # Click the 'Submit' or 'Create Employee' button.
            print("Clicking 'Create Employee' button to submit the form...")
            await page.click('button:has-text("Create Employee")')

            # --- Expected Result ---
            # Employee creation fails.
            # An error message 'Phone Number must be numeric' or 'Invalid phone number format' is displayed.
            # The form remains on the screen with input preserved.

            # 1. Verify employee creation fails and an error message is displayed.
            print("Verifying error message for phone number field...")
            # Look for the error message text. Using regex for flexibility (case-insensitive and common variations).
            # The locator `page.locator('text=/.../i')` searches the entire page for the text.
            # For a more precise check, one might target a specific error element near the input,
            # e.g., `page.locator('input[name="phoneNumber"] ~ .error-message')` if its structure is known.
            await expect(page.locator('text=/Phone Number must be numeric|Invalid phone number format/i')).to_be_visible()
            print("Error message 'Phone Number must be numeric' or 'Invalid phone number format' is displayed.")

            # 2. Verify the form remains on the screen.
            # Check for the presence of the form's main header, indicating it did not close/navigate away.
            await expect(page.locator('h1:has-text("Create Employee")')).to_be_visible()
            print("The 'Create Employee' form remains visible on the screen.")

            # 3. Verify input is preserved in the 'Phone Number' field.
            await expect(page.locator('input[name="phoneNumber"]')).to_have_value(non_numeric_phone_input)
            print(f"The non-numeric phone number '{non_numeric_phone_input}' is preserved in the input field.")

            print("--- Test EC-011 PASSED: Employee creation failed as expected with non-numeric phone number. ---")

        except Exception as e:
            print(f"--- Test EC-011 FAILED: {e} ---")
            # Take a screenshot on failure for debugging
            await page.screenshot(path="failure_screenshot_EC-011.png")
            raise # Re-raise the exception to indicate test failure

        finally:
            # Close the browser instance
            await browser.close()

# To run this script directly (without pytest, for standalone execution):
if __name__ == "__main__":
    asyncio.run(test_invalid_phone_number_employee_creation())