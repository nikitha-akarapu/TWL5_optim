import asyncio
import datetime
import time
from playwright.async_api import async_playwright, expect

async def main():
    """
    Automates the test case: Verify employee creation fails when 'Phone Number' field is left blank.
    """
    async with async_playwright() as p:
        browser = None
        try:
            # Launch a Chromium browser in headful mode for better visibility during development,
            # switch to headless=True for CI/CD environments.
            browser = await p.chromium.launch(headless=False, args=["--start-maximized"])
            page = await browser.new_page()

            # Set viewport to a large size, or use `--start-maximized` args above
            await page.set_viewport_size({"width": 1920, "height": 1080})

            # --- Pre-condition: User is logged in as an administrator/HR ---
            print("Navigating to login page...")
            await page.goto("https://dev.urbuddi.com/")

            # Expect the login page title
            await expect(page).to_have_title("Login | urBuddi")

            print("Entering login credentials...")
            # Assuming these are valid admin/HR credentials for the dev environment
            # Replace with actual credentials or environment variables if needed.
            await page.get_by_placeholder("Email").fill("admin@urbuddi.com")
            await page.get_by_placeholder("Password").fill("password")

            # Click the Sign In button
            await page.get_by_role("button", name="Sign In").click()

            # Wait for navigation to the dashboard or employees page
            # Expecting the URL to change or a specific element to appear
            await expect(page).to_have_url("https://dev.urbuddi.com/dashboard")
            print("Successfully logged in.")

            # --- Pre-condition: User is on the 'Add Employee' form. ---
            print("Navigating to 'Add Employee' form...")
            # Step 1: Click on 'Employees' in the sidebar or navigation.
            # Assuming there's a navigation link/button for Employees.
            await page.get_by_role("link", name="Employees").click()

            # Wait for the Employees list page to load
            await expect(page).to_have_url("https://dev.urbuddi.com/employees")
            print("On Employees list page.")

            # Step 2: Click the 'Add Employee' button on the Employees list page.
            await page.get_by_role("button", name="Add Employee").click()

            # Wait for the 'Add Employee' form URL or a specific element on the form
            await expect(page).to_have_url("https://dev.urbuddi.com/employees/create")
            await expect(page.get_by_text("Create New Employee")).to_be_visible()
            print("On 'Create New Employee' form.")

            # --- Test Steps ---
            print("Filling in other mandatory fields, leaving Phone Number blank...")

            # Generate unique data for employee
            timestamp = int(time.time())
            first_name = f"TestFN_{timestamp}"
            last_name = "User"
            email = f"testemployee_{timestamp}@example.com"
            date_of_joining = datetime.date.today().strftime("%Y-%m-%d") # Today's date
            
            # Fill First Name
            await page.get_by_label("First Name").fill(first_name)
            
            # Fill Last Name (assuming it's mandatory or good practice)
            await page.get_by_label("Last Name").fill(last_name)

            # Fill Email
            await page.get_by_label("Email").fill(email)

            # --- Leave 'Phone Number' field empty (as per test case) ---
            # Explicitly clear if there's any default value, though it should be empty
            phone_field = page.get_by_label("Phone Number")
            await phone_field.fill("") # Ensure it's empty

            # Fill Date of Joining
            await page.get_by_label("Date of Joining").fill(date_of_joining)

            # Select Gender (assuming a select dropdown)
            # Find the select element by label or name and select an option
            await page.get_by_label("Gender").select_option("Male") # Or "Female", "Other"

            # Fill Designation
            await page.get_by_label("Designation").fill("QA Engineer")

            # Fill Department
            await page.get_by_label("Department").fill("IT")

            # Click the 'Submit' button
            print("Clicking 'Submit' button...")
            await page.get_by_role("button", name="Submit").click()

            # --- Expected Result Assertions ---
            print("Verifying expected results...")

            # 1. Employee creation fails. An error message 'Phone Number is required' is displayed.
            error_message_locator = page.get_by_text("Phone Number is required")
            await expect(error_message_locator).to_be_visible()
            print("Error message 'Phone Number is required' is displayed. PASSED.")

            # 2. The form remains on the screen.
            # This means the URL should not have changed from the create employee page,
            # and the 'Create New Employee' heading should still be visible.
            await expect(page).to_have_url("https://dev.urbuddi.com/employees/create")
            await expect(page.get_by_text("Create New Employee")).to_be_visible()
            print("Form remains on the screen. PASSED.")

            # 3. Input preserved (verify one of the previously filled fields).
            await expect(page.get_by_label("First Name")).to_have_value(first_name)
            await expect(page.get_by_label("Email")).to_have_value(email)
            print("Input fields data is preserved. PASSED.")

            print("Test Case EC-004: Verify employee creation fails when 'Phone Number' field is left blank - COMPLETED SUCCESSFULLY.")

        except Exception as e:
            print(f"Test failed due to an error: {e}")
            if browser:
                # Take a screenshot on failure for debugging
                await page.screenshot(path="failure_screenshot.png")
                print("Screenshot 'failure_screenshot.png' taken.")
            raise # Re-raise the exception to indicate test failure
        finally:
            if browser:
                await browser.close()
                print("Browser closed.")

if __name__ == "__main__":
    asyncio.run(main())