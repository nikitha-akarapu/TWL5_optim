import asyncio
from datetime import datetime
from playwright.async_api import async_playwright, expect

async def test_employee_creation_fails_designation_blank():
    async with async_playwright() as p:
        # Launch Chromium browser. Set headless=False to watch the test run visually.
        browser = await p.chromium.launch(headless=True) 
        page = await browser.new_page()

        try:
            # Navigate to the application base URL
            await page.goto("https://dev.urbuddi.com/")

            # Pre-condition: User is logged in as an administrator/HR
            # Assuming the login page is the initial landing page or user is redirected there.
            # Replace these with actual administrator/HR credentials for the dev.urbuddi.com site.
            print("Attempting to log in as administrator/HR...")
            await page.fill('input[type="email"]', "admin@example.com") # Placeholder: Replace with actual admin email
            await page.fill('input[type="password"]', "adminpassword") # Placeholder: Replace with actual admin password
            
            # Click the login button. This locator assumes a button with text "Login".
            await page.click('button:has-text("Login")')

            # Wait for successful login by asserting a common element on the dashboard or employee page.
            # This ensures navigation away from the login page.
            await expect(page.locator('text="Dashboard"').or_(page.locator('text="Employees"'))).to_be_visible(timeout=10000)
            print("Logged in successfully.")

            # Test Step 1: Navigate to the 'Add Employee' form.
            # This typically involves clicking an "Employees" link/menu item, then an "Add Employee" button.
            # Locators below are generic and may need adjustment based on the actual UI structure.

            # Click on 'Employees' link or navigation item.
            print("Navigating to the Employees section...")
            await page.click('a:has-text("Employees")') 
            
            # Wait for the Employees list page to load, then click the "Add Employee" button.
            print("Clicking 'Add Employee' button...")
            # Common locators for an 'Add Employee' button, assuming it's a button with specific text.
            await page.click('button:has-text("Add Employee")')
            
            # Wait for the 'Add Employee' form to be visible, e.g., by checking for its main heading.
            await expect(page.locator('h1:has-text("Add Employee")').or_(page.locator('h2:has-text("Add Employee")'))).to_be_visible(timeout=10000)
            print("Successfully navigated to the 'Add Employee' form.")

            # Generate a unique email for the test to avoid conflicts.
            unique_email = f"testuser_{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"

            # Test Step 3: Fill in other mandatory fields with valid data.
            print("Filling other mandatory fields...")
            await page.fill('input[placeholder*="First Name"]', "John")
            await page.fill('input[placeholder*="Email"]', unique_email)
            await page.fill('input[placeholder*="Phone Number"]', "9876543210")
            
            # For Date of Joining: Fill the date input. Assuming it accepts YYYY-MM-DD format directly.
            today_date = datetime.now().strftime('%Y-%m-%d') 
            await page.fill('input[placeholder*="Date of Joining"]', today_date)
            
            # Select Gender from a dropdown or radio buttons.
            # Assuming a <select> element with an ID containing "gender".
            await page.select_option('select[id*="gender"]', 'Male') 

            # Select Department from a dropdown.
            # Assuming a <select> element with an ID containing "department" and an option with text "IT".
            await page.select_option('select[id*="department"]', {label: "IT"}) 

            # Test Step 2: Leave 'Designation' field empty.
            # No action is performed on the 'Designation' field to ensure it remains blank.
            print("Intentionally leaving 'Designation' field blank.")

            # Test Step 4: Click the 'Submit' or 'Create Employee' button.
            print("Clicking 'Create Employee' button...")
            await page.click('button:has-text("Create Employee")') 

            # Expected Result Verification:
            # 1. Employee creation fails. An error message 'Designation is required' is displayed.
            print("Verifying expected results...")
            error_message_locator = page.locator('text="Designation is required"')
            await expect(error_message_locator).to_be_visible(timeout=5000)
            print("PASS: Error message 'Designation is required' is displayed.")

            # 2. The form remains on the screen with input preserved.
            # We can check for the visibility of the submit button and the value of a previously filled field.
            await expect(page.locator('button:has-text("Create Employee")')).to_be_visible()
            print("PASS: Form remains on screen (Create Employee button still visible).")

            # Verify input preservation (e.g., check the 'First Name' field still holds its value).
            await expect(page.locator('input[placeholder*="First Name"]')).to_have_value("John")
            print("PASS: Input data (First Name) is preserved on the form.")

            print("\nTest Case EC-007 PASSED: Employee creation failed as expected when 'Designation' field was left blank.")

        except Exception as e:
            print(f"\nTest Case EC-007 FAILED: {e}")
            # Take a screenshot on failure for debugging purposes.
            await page.screenshot(path="EC-007_failure_screenshot.png")
            raise # Re-raise the exception to indicate a test failure

        finally:
            # Close the browser instance.
            await browser.close()
            print("Browser closed.")

# Standard boilerplate to run the async test function.
if __name__ == "__main__":
    asyncio.run(test_employee_creation_fails_designation_blank())