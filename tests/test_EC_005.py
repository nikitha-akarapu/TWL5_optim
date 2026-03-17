from playwright.async_api import async_playwright, expect
import asyncio
import datetime

async def test_ec_005():
    """
    Test Case ID: EC-005
    Description: Verify employee creation fails when 'Date of Joining' field is left blank (mandatory field).
    """
    async with async_playwright() as p:
        # Launch browser in headless mode (set headless=False to see the browser UI)
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Set a default timeout for all operations on the page
        page.set_default_timeout(15000) # 15 seconds

        try:
            print("Starting Test Case EC-005: Verify employee creation fails with blank Date of Joining.")

            # --- Pre-conditions: User is logged in as an administrator/HR ---
            print("Navigating to login page...")
            await page.goto("https://dev.urbuddi.com/auth/login")
            await expect(page).to_have_url("https://dev.urbuddi.com/auth/login")

            print("Logging in as administrator...")
            # Fill in admin credentials (replace with actual valid credentials)
            await page.get_by_label("Email").fill("devtest@urbuddi.com")
            await page.get_by_label("Password").fill("password")
            await page.get_by_role("button", name="Login").click()

            # Wait for navigation to the dashboard after successful login
            await page.wait_for_url("https://dev.urbuddi.com/dashboard")
            print("Successfully logged in and landed on dashboard.")

            # --- Pre-conditions: Navigate to the 'Add Employee' form ---
            print("Navigating to the 'Employees' section...")
            # Click on the 'Employees' link in the sidebar
            await page.get_by_role("link", name="Employees").click()
            await page.wait_for_url("https://dev.urbuddi.com/employees")
            print("Landed on Employees page.")

            print("Clicking 'Add New Employee' button...")
            # Click the 'Add New Employee' button
            await page.get_by_role("button", name="Add New Employee").click()
            await page.wait_for_url("https://dev.urbuddi.com/employees/add")
            print("Landed on 'Add Employee' form.")

            # --- Test Steps ---
            # 1. Navigate to the 'Add Employee' form. (Already done in pre-conditions)

            # 2. Leave 'Date of Joining' field empty.
            # This field is initially empty, so we just don't interact with it.

            # 3. Fill in other mandatory fields with valid data
            unique_email = f"test.user_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"
            print(f"Filling mandatory fields (except Date of Joining) with test data. Email: {unique_email}")

            await page.get_by_label("First Name").fill("Automation")
            await page.get_by_label("Last Name").fill("User") # Not mandatory per test, but good practice
            await page.get_by_label("Email").fill(unique_email)
            await page.get_by_label("Phone").fill("1234567890")

            # Gender dropdown
            await page.get_by_label("Gender").select_option("Male") # Assuming "Male" is an option

            # Designation dropdown
            # It's better to select by value or label if known, otherwise by index.
            # Assuming 'Software Engineer' is a valid option. If not, try index: await page.get_by_label("Designation").select_option(index=1)
            await page.get_by_label("Designation").select_option("Software Engineer")

            # Department dropdown
            # Assuming 'IT' is a valid option. If not, try index: await page.get_by_label("Department").select_option(index=1)
            await page.get_by_label("Department").select_option("IT")

            # 4. Click the 'Submit' or 'Create Employee' button.
            print("Clicking 'Submit' button...")
            await page.get_by_role("button", name="Submit").click()

            # --- Expected Result ---
            # Employee creation fails.
            # An error message 'Date of Joining is required' is displayed.
            # The form remains on the screen with input preserved.

            print("Verifying error message and form state...")
            # Assert that the error message is displayed
            date_of_joining_error_locator = page.locator("text='Date of Joining is required'")
            await expect(date_of_joining_error_locator).to_be_visible(timeout=5000)
            print("Error message 'Date of Joining is required' is displayed as expected.")

            # Assert that the form remains on the screen (e.g., check current URL and a form field)
            await expect(page).to_have_url("https://dev.urbuddi.com/employees/add")
            await expect(page.get_by_label("First Name")).to_have_value("Automation")
            print("Form remains on screen with input preserved as expected.")

            print("Test Case EC-005 PASSED.")

        except Exception as e:
            print(f"Test Case EC-005 FAILED: {e}")
            # Optional: Take a screenshot on failure
            await page.screenshot(path="EC-005_failure_screenshot.png")
            raise # Re-raise the exception to indicate test failure

        finally:
            # Close the browser
            await browser.close()
            print("Browser closed.")

# To run the test directly using `python your_script_name.py`
if __name__ == "__main__":
    asyncio.run(test_ec_005())