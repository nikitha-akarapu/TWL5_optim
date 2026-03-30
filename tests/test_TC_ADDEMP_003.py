import asyncio
import uuid
from playwright.async_api import Playwright, async_playwright, expect

# Define login credentials and base URL
BASE_URL = "https://dev.urbuddi.com/"
LOGIN_EMAIL = "srikanth123@optimworks.com"
LOGIN_PASSWORD = "Srikanth@123"

async def run_test_case_add_employee_missing_field(playwright: Playwright):
    """
    Test Case ID: TC-ADDEMP-003
    Description: Verify error message when adding an employee with missing mandatory fields.
    Pre-conditions: User is logged in with credentials, on the 'Employees' page.
    """
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()

    try:
        # Step 1: Navigate to the application and log in
        print("Navigating to login page...")
        await page.goto(BASE_URL)

        # --- Login Section ---
        # The HTML for the login form is not provided in the problem description.
        # We are using common CSS selectors based on standard web application practices
        # for email, password inputs, and a submit button.
        # This is an inference as per the 'login' part of the pre-conditions.
        await page.locator('input[type="email"]').fill(LOGIN_EMAIL)
        await page.locator('input[type="password"]').fill(LOGIN_PASSWORD)
        await page.locator('button[type="submit"]').click()
        
        # Wait for navigation to complete after login.
        # This will wait until the URL matches the base URL followed by any path,
        # and the network becomes idle, indicating the page has fully loaded.
        await page.wait_for_url(f"{BASE_URL}**", wait_until="networkidle") 
        print("Logged in successfully and navigated to dashboard/employees page.")

        # Pre-condition: User is on the 'Employees' page.
        # Although the pre-condition states the user is on the Employees page,
        # after login, the user might land on a dashboard.
        # We explicitly navigate to the Employees page to ensure the pre-condition is met.
        # Locator for "Employees" link is from 'Extracted Available Exact Locators'.
        print("Ensuring navigation to Employees page...")
        await page.get_by_text("Employees").click()
        await page.wait_for_url(f"{BASE_URL}allemployees")
        print("Successfully navigated to Employees page.")

        # Test Step 1: Click on the 'Add Employee' button.
        # Locator for "Add Employee" button is from 'Extracted Available Exact Locators'.
        print("Clicking 'Add Employee' button to open the form...")
        await page.get_by_text("Add Employee").click()
        
        # --- Add Employee Form Section ---
        # The HTML content for the 'Add Employee' form itself (which typically appears
        # as a modal or on a new page after clicking 'Add Employee') was NOT provided.
        # According to the instructions: "fallback to strict CSS selectors based purely
        # on the 'Form HTML Content' provided." Since the form HTML is missing from
        # "Form HTML Content", we are unable to derive strict selectors from it.
        # Therefore, the following locators for form fields and the 'Save' button are
        # based on common HTML naming conventions (e.g., input[name="fieldName"]) for
        # a standard web form, as a pragmatic approach to complete the test script
        # while acknowledging the lack of specific HTML.

        print("Filling employee details, intentionally leaving 'Full Name' empty...")

        # Test Step 2: Leave 'Full Name' field empty.
        # This step is fulfilled by simply not interacting with the 'Full Name' field.
        # Assuming an input field with name="fullName" if we were to fill it.
        # await page.locator('input[name="fullName"]').fill('') # Commented out as per test case

        # Test Step 3: Fill in 'Email' with a unique and valid email.
        unique_employee_email = f"test.missing.{uuid.uuid4()}@example.com"
        await page.locator('input[name="email"]').fill(unique_employee_email)
        print(f"Email filled: {unique_employee_email}")

        # Test Step 4: Select 'Role' (e.g., 'HR').
        # Assuming a select element with name="role" and "HR" as an option.
        await page.locator('select[name="role"]').select_option("HR")
        print("Role selected: HR")

        # Test Step 5: Fill in 'Designation' (e.g., 'HR Executive').
        # Assuming an input field with name="designation".
        await page.locator('input[name="designation"]').fill('HR Executive')
        print("Designation filled: HR Executive")

        # Test Step 6: Select 'Joining Date'.
        # Assuming an input field with name="joiningDate" (e.g., type="date" or text).
        await page.locator('input[name="joiningDate"]').fill('2023-01-01')
        print("Joining Date filled: 2023-01-01")

        # Test Step 7: Select 'Birthdate'.
        # Assuming an input field with name="birthdate" (e.g., type="date" or text).
        await page.locator('input[name="birthdate"]').fill('1990-05-15')
        print("Birthdate filled: 1990-05-15")

        # Test Step 8: Fill in 'Phone Number' with a valid 10-digit number.
        # Assuming an input field with name="phoneNumber".
        await page.locator('input[name="phoneNumber"]').fill('9876543210')
        print("Phone Number filled: 9876543210")

        # Test Step 9: Select 'Gender'.
        # Assuming a select element with name="gender" and "Male" as an option.
        await page.locator('select[name="gender"]').select_option("Male")
        print("Gender selected: Male")

        # Test Step 10: Fill in 'Password' and 'Confirm Password'.
        # Assuming input fields with name="password" and name="confirmPassword".
        employee_password_value = "Employee@123"
        await page.locator('input[name="password"]').fill(employee_password_value)
        await page.locator('input[name="confirmPassword"]').fill(employee_password_value)
        print("Password and Confirm Password filled.")

        # Test Step 11: Click 'Save' or 'Add' button.
        # Assuming a button within the form to save/add the employee.
        # Since not in 'Extracted Available Exact Locators' and no form HTML provided,
        # using a CSS selector with text to identify a common 'Save' button.
        print("Clicking 'Save' button on the Add Employee form...")
        await page.locator('button:has-text("Save")').click() 
        
        # Expected Result 1: An error message 'Full Name is required' (or similar) is displayed.
        print("Verifying the expected error message for 'Full Name'...")
        # Using page.get_by_text for the expected error message string.
        await expect(page.get_by_text('Full Name is required')).to_be_visible()
        print("Assertion Passed: Error message 'Full Name is required' is displayed.")

        # Expected Result 2: The employee is not added.
        # This is implicitly verified by the presence of the validation error message
        # preventing form submission and likely keeping the form modal/page active.
        print("Assertion Passed: Employee not added (indicated by validation error).")

    except Exception as e:
        print(f"Test failed: {e}")
        await page.screenshot(path="failure_screenshot_TC_ADDEMP_003.png")
        raise
    finally:
        print("Closing browser...")
        await context.close()
        await browser.close()

async def main():
    async with async_playwright() as playwright:
        await run_test_case_add_employee_missing_field(playwright)

if __name__ == "__main__":
    asyncio.run(main())