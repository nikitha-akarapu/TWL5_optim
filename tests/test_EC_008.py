import asyncio
from playwright.async_api import async_playwright, expect

async def test_ec_008_verify_department_blank_fails_creation():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True) # Set headless=False to watch the browser
        page = await browser.new_page()

        try:
            # --- Pre-conditions: User is logged in as an administrator/HR ---
            # 1. Navigate to the login page
            await page.goto("https://dev.urbuddi.com/")
            await page.wait_for_load_state('networkidle')
            print("Navigated to login page.")

            # Assume administrator/HR login credentials. These might need to be updated
            # based on actual test environment configurations.
            # Using common placeholder locators for email, password, and sign-in button.
            await page.fill('input[placeholder="Email"]', "admin@example.com") # Replace with actual admin email
            await page.fill('input[placeholder="Password"]', "password123") # Replace with actual admin password
            await page.click('button:has-text("Sign In")')
            
            # Wait for navigation after login. A common sign of successful login
            # is navigation to a dashboard or a different URL.
            await page.wait_for_url("**/dashboard", timeout=10000) # Adjust URL or wait for a common dashboard element
            print("Logged in successfully.")

            # --- Test Steps: Navigate to the 'Add Employee' form. ---
            # This usually involves clicking an "Employees" link/menu item and then an "Add Employee" button.
            # Using generic locators, adjust if the UI differs.
            
            # Click on 'Employees' navigation link (assuming it's a sidebar item or top nav)
            await page.click('a:has-text("Employees")')
            await page.wait_for_load_state('networkidle')
            print("Navigated to Employees list page.")

            # Click on 'Add Employee' button
            # This button might be inside a card, a floating action button, or a regular button.
            await page.click('button:has-text("Add Employee")')
            await page.wait_for_load_state('networkidle')
            # Verify we are on the Add Employee form. Check for a heading like "Add New Employee"
            await expect(page.locator('h1, h2, h3').filter(has_text="Add New Employee")).to_be_visible()
            print("Navigated to 'Add Employee' form.")

            # --- Test Steps: Leave 'Department' field empty. ---
            # --- Test Steps: Fill in other mandatory fields with valid data. ---
            # Using generic locators like placeholders. Adjust if specific IDs or names are available.

            # First Name
            await page.fill('input[placeholder="First Name"]', "Test")
            # Email (unique for employee)
            await page.fill('input[placeholder="Email"]', "test.employee.deptblank@example.com")
            # Phone Number
            await page.fill('input[placeholder="Phone Number"]', "1234567890")
            # Date of Joining (assuming direct input is allowed, otherwise use a date picker logic)
            await page.fill('input[placeholder="Date of Joining"]', "01/15/2023")
            # Gender (assuming a select dropdown)
            await page.locator('select[name="gender"], select:has-label("Gender")').select_option("Male")
            # Designation (assuming a select dropdown)
            await page.locator('select[name="designation"], select:has-label("Designation")').select_option("Software Engineer")

            # Intentionally leaving the 'Department' field blank as per test case EC-008.
            print("Filled mandatory fields, leaving Department blank.")

            # --- Test Steps: Click the 'Submit' or 'Create Employee' button. ---
            # Using a generic locator for the submit button.
            await page.click('button:has-text("Submit"), button:has-text("Create Employee")')
            print("Clicked submit button.")

            # --- Expected Result: Employee creation fails. ---
            # --- Expected Result: An error message 'Department is required' is displayed. ---
            # --- Expected Result: The form remains on the screen with input preserved. ---

            # Verify the error message for 'Department' is displayed
            department_error_message_locator = page.locator('text="Department is required"')
            await expect(department_error_message_locator).to_be_visible(timeout=5000)
            print("Verified 'Department is required' error message is displayed.")

            # Verify the form remains on the screen (e.g., the 'Add New Employee' heading is still visible)
            await expect(page.locator('h1, h2, h3').filter(has_text="Add New Employee")).to_be_visible()
            print("Verified the 'Add Employee' form remains on the screen.")
            
            # Optionally, verify some input fields still contain their values (e.g., First Name)
            await expect(page.locator('input[placeholder="First Name"]')).to_have_value("Test")
            print("Verified input data is preserved.")

            print("Test EC-008 PASSED: Employee creation failed as expected when 'Department' was left blank.")

        except Exception as e:
            print(f"Test EC-008 FAILED due to an error: {e}")
            # Optionally, take a screenshot on failure
            await page.screenshot(path="ec_008_failure_screenshot.png")
            raise # Re-raise the exception to indicate test failure
        finally:
            await browser.close()
            print("Browser closed.")

# Run the test
if __name__ == "__main__":
    asyncio.run(test_ec_008_verify_department_blank_fails_creation())