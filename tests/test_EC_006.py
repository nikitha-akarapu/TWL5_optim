import asyncio
from playwright.async_api import async_playwright, expect
import datetime
import uuid

async def test_employee_creation_gender_required():
    """
    Test Case ID: EC-006
    Description: Verify employee creation fails when 'Gender' field is not selected (mandatory field).
    """
    async with async_playwright() as p:
        # Launch browser in headless mode by default. Set headless=False for visual debugging.
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            # 1. Navigate to the application login URL
            print("Navigating to the application login page...")
            await page.goto("https://dev.urbuddi.com/")
            await expect(page).to_have_url("https://dev.urbuddi.com/login")

            # Pre-condition: User is logged in as an administrator/HR
            print("Attempting to log in as administrator...")
            # Using generic locators for login fields. Adjust if actual IDs/names differ.
            # IMPORTANT: Replace "admin@example.com" and "password" with actual valid administrator credentials
            # for your test environment on dev.urbuddi.com.
            await page.get_by_placeholder("Email").fill("admin@example.com") # Placeholder email
            await page.get_by_placeholder("Password").fill("password")       # Placeholder password
            await page.get_by_role("button", name="Log in").click()

            # Wait for navigation after login. Expect to land on a dashboard or home page.
            # Adjust the expected URL if the post-login page is different.
            await page.wait_for_url("https://dev.urbuddi.com/dashboard")
            print("Successfully logged in and navigated to dashboard.")

            # Test Step 1: Navigate to the 'Add Employee' form.
            print("Navigating to the 'Add Employee' form...")
            # This typically involves clicking navigation links.
            # Step A: Click on the 'Employees' link/button in the sidebar/navbar
            # Adjust locator if the navigation item for 'Employees' uses a different text or selector.
            await page.get_by_text("Employees").click()
            await page.wait_for_url("https://dev.urbuddi.com/employees")
            print("Navigated to Employees list page.")

            # Step B: Click on the 'Add Employee' button
            # Adjust locator if the 'Add Employee' button uses a different text or selector.
            await page.get_by_role("button", name="Add Employee").click()
            # Wait for the form to appear. If it's a modal, the URL might not change,
            # so we'll assert the presence of the form's title.
            await expect(page.get_by_text("Add Employee")).to_be_visible() # Asserts the 'Add Employee' form title is visible
            print("Navigated to 'Add Employee' form successfully.")

            # Test Step 2: Ensure 'Gender' field is not selected (e.g., default 'Select' option).
            # We locate the gender field but do not interact with it, thus leaving it in its default state.
            # Assuming 'Gender' field is a select dropdown with a label. Adjust locator if different (e.g., placeholder).
            gender_select_locator = page.get_by_label("Gender")
            await expect(gender_select_locator).to_be_visible()
            # Optional: Assert its initial value if you know the default "empty" option's value (e.g., "").
            # await expect(gender_select_locator).to_have_value("")
            print("Ensuring 'Gender' field remains unselected.")

            # Test Step 3: Fill in other mandatory fields with valid data.
            print("Filling other mandatory fields with valid data...")
            unique_id = uuid.uuid4().hex[:8] # Generate a unique string for test data
            current_date = datetime.date.today().strftime("%Y-%m-%d") # Format for date inputs

            # Fill First Name and Last Name
            await page.get_by_label("First Name").fill(f"TestFirstName-{unique_id}")
            await page.get_by_label("Last Name").fill(f"TestLastName-{unique_id}") # Assuming Last Name is also mandatory

            # Fill Email (unique) and Phone Number
            await page.get_by_label("Email").fill(f"test.employee.{unique_id}@example.com")
            # Using placeholder for phone if no label is present. Adjust locator as needed.
            await page.get_by_placeholder("Phone Number").fill("1234567890")

            # Fill Date of Joining and Date of Birth
            await page.get_by_label("Date of Joining").fill(current_date)
            await page.get_by_label("Date of Birth").fill("1990-01-15") # Example date of birth

            # Fill Designation
            await page.get_by_label("Designation").fill("Automation QA Engineer")

            # Select Department (assuming it's a dropdown).
            # Replace 'IT' with an actual department label/value available in the dropdown on dev.urbuddi.com.
            department_dropdown = page.get_by_label("Department")
            await expect(department_dropdown).to_be_visible()
            await department_dropdown.select_option(label="IT") # Select by visible text label

            # Fill Salary (assuming it's mandatory)
            await page.get_by_label("Salary").fill("75000")

            # Test Step 4: Click the 'Submit' or 'Create Employee' button.
            print("Clicking the 'Create Employee' button...")
            # Adjust locator if the button text or role is different.
            await page.get_by_role("button", name="Create Employee").click()

            # Expected Result: Employee creation fails. An error message 'Gender is required' is displayed.
            print("Verifying expected error message and form state...")
            error_message_locator = page.get_by_text("Gender is required")
            await expect(error_message_locator).to_be_visible()
            print(f"Error message '{await error_message_locator.text_content()}' is displayed as expected.")

            # Expected Result: The form remains on the screen with input preserved.
            # We can verify this by checking if the 'Create Employee' button is still visible
            # and if the 'Add Employee' form title is still present.
            await expect(page.get_by_role("button", name="Create Employee")).to_be_visible()
            await expect(page.get_by_text("Add Employee")).to_be_visible()
            print("Form remains on screen (Create Employee button and form title still visible).")

            print("Test EC-006: Employee creation failed as expected due to missing 'Gender' field.")

        except Exception as e:
            print(f"Test failed with error: {e}")
            # Take a screenshot on failure for debugging purposes
            await page.screenshot(path=f"screenshot_failure_EC-006_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.png")
            raise # Re-raise the exception to indicate test failure

        finally:
            await browser.close()
            print("Browser closed.")

# To run the test script directly from your terminal:
# 1. Make sure you have Playwright installed: `pip install playwright`
# 2. Install browser binaries: `playwright install`
# 3. Run this script: `python your_script_name.py`
if __name__ == "__main__":
    asyncio.run(test_employee_creation_gender_required())