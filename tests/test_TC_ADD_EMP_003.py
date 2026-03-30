import asyncio
from playwright.async_api import async_playwright, expect
import datetime
import random

async def main():
    async with async_playwright() as p:
        # 1. Launch browser in headed mode as required.
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # --- Pre-condition 1: User is logged in to the application ---
        print("Navigating to login page...")
        await page.goto("https://dev.urbuddi.com/")

        # Since no specific HTML or locators for the login page were provided in the 'Extracted Available Exact Locators',
        # we will use common Playwright locators (get_by_placeholder, get_by_role)
        # assuming standard input fields for email/password and a login button.
        print("Filling login credentials...")
        await page.get_by_placeholder("Email").fill("srikanth123@optimworks.com")
        await page.get_by_placeholder("Password").fill("Srikanth@123")
        await page.get_by_role("button", name="Sign In").click()

        # Wait for successful login by asserting navigation to a known page (e.g., dashboard)
        # and checking for a visible element that confirms login.
        try:
            await page.wait_for_url("**/") # Assumes root URL after login, adjust if dashboard has a different path
            await expect(page.get_by_text("Dashboard")).to_be_visible() # Verifies an element from the dashboard/home page
            print("Login successful.")
        except Exception as e:
            print(f"Login failed or expected post-login page not found: {e}")
            await page.screenshot(path="login_failure.png")
            await browser.close()
            return

        # --- Pre-condition 2: User has navigated to the 'Employees' section ---
        print("Navigating to 'Employees' section...")
        # Using recommended locator from the provided map
        await page.get_by_text("Employees").click()
        await expect(page).to_have_url("**/allemployees") # Assert the URL changed to the employees page
        await expect(page.get_by_text("Employees", exact=True)).to_be_visible() # Verify the 'Employees' page title is visible
        print("Navigated to Employees section.")

        # --- Pre-condition 3: The 'Add Employee' form is accessible ---
        # This will be verified in the first test step by clicking the button and expecting the form.

        # --- Test Case ID: TC-ADD-EMP-003 ---
        print("\nStarting Test Case TC-ADD-EMP-003: Verify employee cannot be added with invalid data.")

        # Generate unique ID and today's date for form filling
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        employee_id = f"EMP{timestamp}{random.randint(10, 99)}"
        today_date = datetime.date.today().strftime("%Y-%m-%d") # Common date format for input type="date"

        # 1. Click on the 'Add Employee' button.
        print("Step 1: Clicking 'Add Employee' button...")
        # Using recommended locator from the provided map
        await page.get_by_text("Add Employee").click()
        # Expect the Add Employee modal/form to appear. Assuming a common heading or text for the modal.
        await expect(page.get_by_role("heading", name="Add Employee").or_(page.get_by_text("Add Employee Form"))).to_be_visible()
        print("Add Employee form is accessible and visible.")

        # 2. Fill 'Full Name' (e.g., 'Alice Smith').
        print(f"Step 2: Filling 'Full Name' with 'Alice Smith'")
        # No specific locator for form fields provided in the map, using `get_by_label`.
        await page.get_by_label("Full Name").fill("Alice Smith")

        # 3. Fill 'Email' with an invalid format (e.g., 'alice.smith@example').
        invalid_email = "alice.smith@example" # Missing top-level domain
        print(f"Step 3: Filling 'Email' with invalid format: '{invalid_email}'")
        await page.get_by_label("Email").fill(invalid_email)

        # 4. Fill 'Employee ID' with a unique ID (e.g., 'EMP003').
        print(f"Step 4: Filling 'Employee ID' with unique ID: '{employee_id}'")
        await page.get_by_label("Employee ID").fill(employee_id)

        # 5. Select a 'Role' (e.g., 'Employee').
        print(f"Step 5: Selecting 'Role': 'Employee'")
        # Assuming it's a standard select dropdown or a custom one that behaves similarly to `select_option`
        # or requires clicking an element and then clicking an option from a list.
        try:
            await page.get_by_label("Role").select_option("Employee")
        except Exception:
            # Fallback for custom dropdowns (e.g., Material UI, Ant Design): click the input, then click the option
            print("  'Role' select_option failed, attempting click-and-select strategy.")
            await page.get_by_label("Role").click() # Click the element that opens the dropdown options
            await page.get_by_role("option", name="Employee").click() # Click the actual option in the opened list

        # 6. Fill 'Designation' (e.g., 'UX Designer').
        print(f"Step 6: Filling 'Designation': 'UX Designer'")
        await page.get_by_label("Designation").fill("UX Designer")

        # 7. Select 'Date of Joining' (e.g., today's date).
        print(f"Step 7: Selecting 'Date of Joining': '{today_date}'")
        # Assuming an input field that accepts direct date input in YYYY-MM-DD format.
        await page.get_by_label("Date of Joining").fill(today_date)

        # 8. (If applicable) Fill 'Phone Number' with non-numeric characters (e.g., 'abcdefghij').
        invalid_phone_number = "abcdefghij"
        print(f"Step 8: Filling 'Phone Number' with non-numeric characters: '{invalid_phone_number}'")
        await page.get_by_label("Phone Number").fill(invalid_phone_number)

        # 9. Click the 'Submit' or 'Add' button.
        print("Step 9: Clicking 'Add' button to submit the form...")
        # Assuming the form's submit button is named "Add".
        await page.get_by_role("button", name="Add", exact=True).click()

        # --- Expected Result Assertions ---
        print("\nVerifying expected results...")

        # Expected Result 1: The employee is NOT added. An error message indicating 'Invalid Email format' (or similar validation message) is displayed.
        print("Asserting 'Invalid email format' error message is displayed...")
        # Using .or_() to handle common variations of the email validation message
        await expect(page.get_by_text("Invalid email format").or_(page.get_by_text("Please enter a valid email"))).to_be_visible()
        print("Email validation error displayed as expected.")

        # Expected Result 2: If phone number validation exists, an error for non-numeric input should be shown.
        print("Asserting phone number validation error is displayed...")
        # Using .or_() to handle common variations of the phone number validation message
        await expect(page.get_by_text("Phone number must be numeric").or_(page.get_by_text("Invalid phone number"))).to_be_visible()
        print("Phone number validation error displayed as expected.")

        # Expected Result 3: The form remains open.
        print("Asserting the Add Employee form remains open...")
        # Re-assert that the modal heading or a form field is still visible.
        await expect(page.get_by_role("heading", name="Add Employee").or_(page.get_by_text("Add Employee Form"))).to_be_visible()
        print("Add Employee form remained open as expected.")

        print("\nTest Case TC-ADD-EMP-003 PASSED: Employee cannot be added with invalid data, error messages displayed, and form remains open.")

        # Capture screenshot for documentation
        await page.screenshot(path="tc-add-emp-003_success.png")

        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())