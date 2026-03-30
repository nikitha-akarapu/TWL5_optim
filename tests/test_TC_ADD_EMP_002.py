import asyncio
from datetime import datetime
from playwright.async_api import async_playwright, expect

async def test_add_employee_mandatory_fullname_blank():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # --- Pre-condition 1: User is logged in ---
        # Navigate to the application login page
        await page.goto("https://dev.urbuddi.com/")

        # Login fields (Email, Password) and Login button locators are not in the provided
        # "Extracted Available Exact Locators" or "Form HTML Content".
        # As per instructions, falling back to best available locators for these.
        # Using Playwright's get_by_placeholder and get_by_role for robustness.
        await page.get_by_placeholder("Email").fill("srikanth123@optimworks.com")
        await page.get_by_placeholder("Password").fill("Srikanth@123")
        await page.get_by_role("button", name="Login").click()

        # Wait for successful login and navigation to the dashboard.
        # A common element like "Dashboard" text or the URL change indicates successful login.
        await page.wait_for_url("**/") # Wait for the base URL after login
        await expect(page.get_by_text("Dashboard")).to_be_visible()

        print("Logged in successfully.")

        # --- Pre-condition 2: User has navigated to the 'Employees' section ---
        # Using the recommended locator for "Employees" from the provided map.
        await page.get_by_text("Employees").click()
        await page.wait_for_url("**/allemployees") # Wait for navigation to employees page

        # Verify the Employees page title using a CSS selector from the provided HTML.
        await expect(page.locator(".sc-feUZmu.qNlEl")).to_have_text("Employees")

        print("Navigated to Employees section.")

        # --- Test Step 1: Click on the 'Add Employee' button ---
        # Using the recommended locator for "Add Employee" button from the provided map.
        await page.get_by_text("Add Employee").click()

        # --- Pre-condition 3: The 'Add Employee' form is accessible ---
        # Wait for the Add Employee form/modal to appear.
        # The HTML for the 'Add Employee' form itself is NOT provided in the problem description.
        # Therefore, locators for fields within the form (Full Name, Email, Employee ID, Role, etc.)
        # are assumed using Playwright's robust text-based locators like get_by_label,
        # which are generally preferred when specific IDs or classes are unknown.
        # Assuming the form has a visible heading like "Add New Employee".
        await expect(page.get_by_role("heading", name="Add New Employee")).to_be_visible()

        print("Add Employee form is accessible and opened.")

        # --- Test Steps for TC-ADD-EMP-002 ---

        # Step 2: Leave 'Full Name' field blank.
        # Assuming 'Full Name' input field can be located by its label.
        full_name_field = page.get_by_label("Full Name")
        await expect(full_name_field).to_be_empty() # Assert it's initially empty

        # Step 3: Fill 'Email' with a valid email (e.g., 'jane.doe@example.com').
        # Generate a unique email to avoid conflicts if previously added.
        unique_email = f"jane.doe.{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"
        await page.get_by_label("Email").fill(unique_email)

        # Step 4: Fill 'Employee ID' with a unique ID (e.g., 'EMP002').
        # Generate a unique Employee ID.
        unique_employee_id = f"EMP{datetime.now().strftime('%H%M%S')}"
        await page.get_by_label("Employee ID").fill(unique_employee_id)

        # Step 5: Select a 'Role' (e.g., 'Employee').
        # Assuming 'Role' is a standard select dropdown or a component handled by select_option.
        await page.get_by_label("Role").select_option("Employee")

        # Step 6: Fill 'Designation' (e.g., 'QA Engineer').
        await page.get_by_label("Designation").fill("QA Engineer")

        # Step 7: Select 'Date of Joining' (e.g., today's date).
        # Assuming 'Date of Joining' is an input field that accepts YYYY-MM-DD format.
        today_date = datetime.now().strftime("%Y-%m-%d")
        await page.get_by_label("Date of Joining").fill(today_date)

        # Step 8: Click the 'Submit' or 'Add' button.
        # Assuming the button to submit the form is labeled "Add".
        await page.get_by_role("button", name="Add", exact=True).click()

        print("Attempted to add employee with 'Full Name' field left blank.")

        # --- Expected Result Verification ---

        # Expected Result 1: The employee is NOT added.
        # This will be verified by the presence of an error message and the form remaining open.

        # Expected Result 2: An error message indicating 'Full Name is mandatory'
        # (or similar validation message) is displayed next to the respective field or as a general notification.
        # Assuming the exact text "Full Name is mandatory" appears.
        error_message_locator = page.get_by_text("Full Name is mandatory", exact=False)
        await expect(error_message_locator).to_be_visible()
        await expect(error_message_locator).to_have_text("Full Name is mandatory")

        print("Verified: 'Full Name is mandatory' error message is displayed.")

        # Expected Result 3: The form remains open.
        # Assert that the form title or another input field is still visible, indicating the form did not close.
        await expect(page.get_by_role("heading", name="Add New Employee")).to_be_visible()
        await expect(page.get_by_label("Email")).to_be_visible() # Check another form field is still there

        print("Verified: Add Employee form remains open.")

        await browser.close()

if __name__ == '__main__':
    asyncio.run(test_add_employee_mandatory_fullname_blank())