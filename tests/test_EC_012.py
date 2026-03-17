import asyncio
from playwright.async_api import async_playwright, expect
import datetime
import random
import string

# --- Configuration ---
# Base URL of the application
BASE_URL = "https://dev.urbuddi.com/"
# Administrator/HR login credentials (REPLACE with actual credentials)
# IMPORTANT: For real-world scenarios, these should be loaded from secure environment variables
# or a configuration management system, not hardcoded.
LOGIN_EMAIL = "your_admin_email@example.com"
LOGIN_PASSWORD = "your_admin_password"

async def test_invalid_phone_number_length():
    """
    Test Case ID: EC-012
    Description: Verify employee creation fails with 'Phone Number' that is too short or too long.
    Pre-conditions: User is logged in as an administrator/HR and is on the 'Add Employee' form.
    """
    async with async_playwright() as playwright:
        # Launch a Chromium browser instance. Set headless=False to watch the test run.
        browser = await playwright.chromium.launch(headless=True)
        # Create a new page within the browser context
        page = await browser.new_page()

        try:
            # --- Pre-conditions: Login as administrator/HR ---
            print("TEST STEP: Navigating to login page and logging in as admin.")
            await page.goto(BASE_URL)

            # Assert that the email input field is visible before interacting
            await expect(page.get_by_placeholder("Email")).to_be_visible()

            # Fill in the login credentials
            await page.get_by_placeholder("Email").fill(LOGIN_EMAIL)
            await page.get_by_placeholder("Password").fill(LOGIN_PASSWORD)

            # Click the login button. Assuming its text is "Log in".
            await page.get_by_role("button", name="Log in").click()

            # Assert successful login by checking for a redirection to the dashboard or a key element.
            # Adjust the URL or locator if the post-login page is different.
            await expect(page).to_have_url(f"{BASE_URL}dashboard", timeout=10000)
            print("Pre-condition met: Successfully logged in as administrator.")

            # --- Test Step 1: Navigate to the 'Add Employee' form. ---
            print("TEST STEP: Navigating to 'Add Employee' form.")
            # Assuming there's a navigation link for "Employees" on the dashboard.
            await page.get_by_role("link", name="Employees").click()
            # Assert that we are on the employees listing page.
            await expect(page).to_have_url(f"{BASE_URL}employees")

            # Assuming there's an "Add Employee" button on the employees listing page.
            await page.get_by_role("button", name="Add Employee").click()
            # Assert that we are now on the 'Add Employee' form page.
            await expect(page).to_have_url(f"{BASE_URL}employees/add")
            print("TEST STEP: Successfully navigated to 'Add Employee' form.")

            # --- Generate unique test data for other mandatory fields ---
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            # Generate a random string for uniqueness
            unique_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
            first_name = f"TestFN_{unique_suffix}"
            last_name = f"TestLN_{unique_suffix}"
            valid_email = f"test.employee.{timestamp}.{unique_suffix}@example.com"
            job_title = "Automation QA"
            # Format start date as MM/DD/YYYY
            start_date = datetime.date.today().strftime("%m/%d/%Y")

            # --- Define locators for the 'Add Employee' form fields ---
            first_name_field = page.get_by_placeholder("First Name")
            last_name_field = page.get_by_placeholder("Last Name")
            email_field = page.get_by_placeholder("Email Address") # Common placeholder for email
            phone_number_field = page.get_by_placeholder("Phone Number")
            # Assuming Department is a custom dropdown; interact by clicking label then option.
            department_label = page.get_by_label("Department")
            job_title_field = page.get_by_placeholder("Job Title")
            start_date_field = page.get_by_placeholder("Start Date")
            submit_button = page.get_by_role("button", name="Create Employee") # Assuming button text

            # --- Test Step 2 (Part 1): Enter a phone number with less than 10 digits ---
            print("TEST STEP: Entering a short phone number and filling other fields.")
            invalid_short_phone = "12345" # Less than 10 digits
            await phone_number_field.fill(invalid_short_phone)
            await first_name_field.fill(first_name)
            await last_name_field.fill(last_name)
            await email_field.fill(valid_email)
            
            # Interact with the Department dropdown: click the label, then select an option.
            await department_label.click()
            # Assuming 'Sales' is a visible option in the dropdown list that appears.
            await page.get_by_role("option", name="Sales").click()

            await job_title_field.fill(job_title)
            await start_date_field.fill(start_date) # Directly fill for simplicity.
            
            # --- Test Step 3: Click the 'Submit' or 'Create Employee' button. ---
            print("TEST STEP: Clicking 'Create Employee' button for short phone number.")
            await submit_button.click()

            # --- Expected Result 1: Employee creation fails. Error message displayed. Form remains. ---
            print("EXPECTED RESULT: Asserting validation error for short phone number.")
            # Locate the error message. This locator assumes the text "Phone Number must be 10 digits"
            # or similar is directly visible somewhere, likely near the phone number field.
            # Adjust the locator if the error message is in a specific div/span with a class.
            error_message_locator = page.get_by_text("Phone Number must be 10 digits", exact=False) 
            
            # Assert that the error message is visible.
            await expect(error_message_locator).to_be_visible()
            # Print the actual error message content for debugging/logging
            print(f"VALIDATION: Error message displayed: '{await error_message_locator.text_content()}'")

            # Assert that the form remains on the screen (e.g., the submit button is still visible).
            await expect(submit_button).to_be_visible()
            # Assert that the entered invalid phone number value is preserved in the field.
            await expect(phone_number_field).to_have_value(invalid_short_phone)
            print("VALIDATION: Form remained on screen and short phone number input preserved.")

            # --- Test Step 2 (Part 2): Enter a phone number with more than 10 digits ---
            print("TEST STEP: Entering a long phone number.")
            invalid_long_phone = "1234567890123" # More than 10 digits

            # Clear the phone number field and fill with the new invalid value.
            await phone_number_field.fill(invalid_long_phone)
            # Other fields should still be populated from the previous attempt, no need to refill.
            
            # --- Test Step 3: Click the 'Submit' or 'Create Employee' button again. ---
            print("TEST STEP: Clicking 'Create Employee' button for long phone number.")
            await submit_button.click()

            # --- Expected Result 2: Employee creation fails. Error message displayed. Form remains. ---
            print("EXPECTED RESULT: Asserting validation error for long phone number.")
            # The same error message locator should apply for exceeding length.
            await expect(error_message_locator).to_be_visible()
            print(f"VALIDATION: Error message displayed: '{await error_message_locator.text_content()}'")

            # Assert that the form remains on the screen.
            await expect(submit_button).to_be_visible()
            # Assert that the entered invalid phone number value is preserved.
            await expect(phone_number_field).to_have_value(invalid_long_phone)
            print("VALIDATION: Form remained on screen and long phone number input preserved.")

            print("Test 'EC-012: Verify employee creation fails with invalid phone number length' PASSED successfully.")

        except Exception as e:
            # If any assertion or operation fails, catch the exception.
            print(f"\nTEST FAILED: {e}")
            # Optional: Take a screenshot on failure for debugging.
            await page.screenshot(path="failure_screenshot_EC-012.png")
            # Re-raise the exception to indicate a test failure to the caller.
            raise

        finally:
            # Ensure the browser is closed even if the test fails.
            await browser.close()
            print("Browser closed.")

# Entry point for running the test script.
if __name__ == "__main__":
    # Use asyncio.run to execute the async test function.
    asyncio.run(test_invalid_phone_number_length())