import asyncio
from playwright.async_api import async_playwright, expect

async def test_employee_creation_fails_first_name_blank():
    """
    Test Case ID: EC-002
    Description: Verify employee creation fails when 'First Name' field is left blank (mandatory field).
    Pre-conditions: User is logged in as an administrator/HR and is on the 'Add Employee' form.
    """
    async with async_playwright() as p:
        # Launch browser in headless mode (set headless=False to see the browser UI)
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            print("Starting test: EC-002 - Verify employee creation fails with blank First Name.")

            # --- Pre-condition: User is logged in as an administrator/HR ---
            await page.goto("https://dev.urbuddi.com/")
            print("1. Navigated to the login page.")

            # Fill in login credentials.
            # NOTE: These are generic placeholder credentials.
            #       Replace with actual valid administrator/HR credentials for dev.urbuddi.com
            #       for the login step to succeed.
            await page.fill('[placeholder="Email"]', "admin@example.com") # Using placeholder as locator
            await page.fill('[placeholder="Password"]', "Password123!") # Using placeholder as locator
            await page.click('button:has-text("Login")') # Using button text as locator
            print("2. Attempted to log in with provided credentials.")

            # Wait for successful login by checking for a common element on the dashboard/main page.
            # Assuming 'Employees' link is visible after login.
            await expect(page.locator('a:has-text("Employees")')).to_be_visible(timeout=10000)
            print("3. Successfully logged in (validated by 'Employees' link visibility).")

            # --- Pre-condition: User is on the 'Add Employee' form ---
            # Test Step 1: Navigate to the 'Add Employee' form.
            await page.click('a:has-text("Employees")')
            print("4. Clicked on 'Employees' navigation link.")

            # Wait for the employee list page to load and the 'Add Employee' button to appear.
            await expect(page.locator('button:has-text("Add Employee")')).to_be_visible()
            await page.click('button:has-text("Add Employee")')
            print("5. Clicked on 'Add Employee' button.")

            # Verify that the 'Add Employee' form is loaded and visible.
            await expect(page.locator('h2:has-text("Add Employee")')).to_be_visible()
            await expect(page).to_have_url("https://dev.urbuddi.com/employee/create")
            print("6. Verified navigation to 'Add Employee' form.")

            # --- Test Steps for EC-002 ---

            # Test Step 2: Leave 'First Name' field empty.
            # No action is performed on the First Name field, effectively leaving it blank.
            print("7. Leaving 'First Name' field empty as required by the test case.")

            # Test Step 3: Fill in other mandatory fields with valid data.
            # (Email, Phone Number, Date of Joining, Gender, Designation, Department)
            # Using generic locators (placeholders or name attributes) for form fields.
            await page.fill('[placeholder="Last name"]', "Test")
            await page.fill('[placeholder="Email"]', "test.employee.ec002@example.com") # Unique email
            await page.fill('[placeholder="Phone number"]', "1234567890")
            
            # For Date of Joining, directly fill the input field.
            await page.fill('[placeholder="DD/MM/YYYY"]', "01/01/2023") 
            
            # For Gender, select an option from the dropdown.
            # Assuming 'Male' is a valid option value or label in the select element.
            await page.select_option('select[name="gender"]', 'Male') 
            
            await page.fill('[placeholder="Designation"]', "Automation QA Engineer")
            await page.fill('[placeholder="Department"]', "IT")
            print("8. Filled in other mandatory fields with valid data.")

            # Test Step 4: Click the 'Submit' or 'Create Employee' button.
            await page.click('button:has-text("Create Employee")')
            print("9. Clicked the 'Create Employee' button.")

            # --- Expected Result Assertions ---

            # Expected Result 1: Employee creation fails. An error message 'First name is required' is displayed.
            # Looking for a generic text locator for the error message.
            error_message_locator = page.locator('text="First name is required"')
            await expect(error_message_locator).to_be_visible(timeout=5000)
            print("10. ASSERTION PASSED: Error message 'First name is required' is displayed.")

            # Expected Result 2: The form remains on the screen with input preserved.
            # Verify the URL remains on the 'Add Employee' form.
            await expect(page).to_have_url("https://dev.urbuddi.com/employee/create")
            print("11. ASSERTION PASSED: Form remains on the screen (URL unchanged).")

            # Verify input preservation for one of the filled fields (e.g., Last Name).
            await expect(page.locator('[placeholder="Last name"]')).to_have_value("Test")
            print("12. ASSERTION PASSED: Input for 'Last name' field is preserved.")

            print("Test EC-002 completed successfully: Employee creation failed as expected.")

        except Exception as e:
            print(f"Test EC-002 FAILED: {e}")
            # Take a screenshot on failure for debugging purposes
            await page.screenshot(path="EC002_failure_screenshot.png")
            print("Screenshot 'EC002_failure_screenshot.png' taken.")
            raise # Re-raise the exception to indicate test failure

        finally:
            await browser.close()
            print("Browser closed.")

# To run the test script
if __name__ == "__main__":
    asyncio.run(test_employee_creation_fails_first_name_blank())