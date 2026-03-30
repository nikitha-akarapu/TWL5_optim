import asyncio
from playwright.async_api import async_playwright, expect
import datetime
import random
import string

async def main():
    async with async_playwright() as p:
        # 1. Launch browser in headed mode
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # Base URL for the application
        base_url = "https://dev.urbuddi.com/"
        await page.goto(base_url)

        # Pre-conditions: Login
        # Login credentials
        login_email = "srikanth123@optimworks.com"
        login_password = "Srikanth@123"

        # --- Login Steps ---
        # IMPORTANT: Locators for the login page are NOT provided in the HTML snippet or exact locators list.
        # These locators are ASSUMPTIONS based on common web application login form structures.
        print("Attempting to log in...")
        try:
            # Assume input fields for email and password
            await page.fill('input[type="email"]', login_email)
            await page.fill('input[type="password"]', login_password)
            # Assume a login button with text "Sign in"
            await page.get_by_role("button", name="Sign in").click()
            # Wait for navigation after login to ensure the new page is loaded
            await page.wait_for_url(f"{base_url}*")
            print("Login successful.")
        except Exception as e:
            print(f"Login elements not found or login failed. Assuming user is already logged in or form is different. Error: {e}")
            # If login fails, the script will continue, assuming the pre-condition of being logged in is met.

        # 2. Pre-conditions: User is on the 'Employees' page.
        # Navigate to the employees page if not already there.
        # Using the exact locator from the provided list: page.get_by_text("Employees")
        if not "/allemployees" in page.url:
            print("Navigating to Employees page via sidebar.")
            await page.get_by_text("Employees").click()
            # Wait for the URL to reflect the employees page
            await page.wait_for_url(f"{base_url}allemployees")
        print("Successfully on the Employees page.")

        # Test Case ID: TC-ADDEMP-002
        # Description: Verify successful addition of a new employee with all valid fields (mandatory and optional).

        # Generate unique test data for the new employee
        unique_suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
        full_name = f"Jane Smith {unique_suffix}"
        email = f"jane.smith.{unique_suffix}@example.com"
        # Generate a valid 10-digit phone number
        phone_number = f"998877{random.randint(1000, 9999)}"
        password = "SecurePass!23" # Example password

        # Calculate dates
        # Joining date: 1 year ago from today
        joining_date = (datetime.date.today() - datetime.timedelta(days=365)).strftime("%Y-%m-%d")
        # Birthdate: 25 years ago from today, ensuring 18+
        birth_date = (datetime.date.today() - datetime.timedelta(days=25 * 365)).strftime("%Y-%m-%d")

        # Test Steps:
        # 1. Click on the 'Add Employee' button.
        print("Step 1: Clicking 'Add Employee' button.")
        # Using the exact locator from the provided list
        await page.get_by_text("Add Employee").click()

        # IMPORTANT NOTE REGARDING LOCATORS FOR ADD EMPLOYEE FORM:
        # The provided 'Form HTML Content' and 'Extracted Available Exact Locators' list are for the
        # 'Employees' list page, NOT the 'Add Employee' form that appears after clicking the button.
        # Therefore, locators for the input fields within the 'Add Employee' form are NOT available from the given information.
        # The following locators for form fields are ASSUMPTIONS based on common web form practices (e.g., using get_by_label)
        # and the field names mentioned in the manual test case.
        # If actual HTML for the 'Add Employee' form were provided, more precise and robust locators would be used.

        # Wait for the add employee form to appear (e.g., by waiting for a common input field like Full Name)
        await page.wait_for_selector('input[name="fullName"]', state='visible')
        print("Add Employee form is visible. Filling details...")

        # 2. Fill in 'Full Name' with valid data
        await page.get_by_label("Full Name").fill(full_name) # Assumption: input field has a label "Full Name"
        # 3. Fill in 'Email' with a unique and valid email format
        await page.get_by_label("Email").fill(email) # Assumption: input field has a label "Email"
        # 4. Select 'Role' from the dropdown (e.g., 'QA Engineer').
        # Assumption: a select element with label "Role" and an option "QA Engineer"
        await page.get_by_label("Role").select_option("QA Engineer")
        # 5. Fill in 'Designation' with valid data
        await page.get_by_label("Designation").fill("Senior QA") # Assumption: input field has a label "Designation"
        # 6. Fill in 'Team'
        await page.get_by_label("Team").fill("Quality Assurance") # Assumption: input field has a label "Team"
        # 7. Select 'Joining Date'
        # Assumption: an input field (likely type="date") with label "Joining Date"
        await page.get_by_label("Joining Date").fill(joining_date)
        # 8. Select 'Birthdate'
        # Assumption: an input field (likely type="date") with label "Birthdate"
        await page.get_by_label("Birthdate").fill(birth_date)
        # 9. Fill in 'Phone Number' with a valid 10-digit number
        await page.get_by_label("Phone Number").fill(phone_number) # Assumption: input field has a label "Phone Number"
        # 10. Select 'Gender'
        # Assumption: a select element with label "Gender" and an option "Female"
        await page.get_by_label("Gender").select_option("Female")
        # 11. Select 'Reporting Manager' from the dropdown (if available).
        # Assumption: a select element with label "Reporting Manager". Selecting the first option (index=1) as a placeholder.
        try:
            await page.get_by_label("Reporting Manager").select_option(index=1)
        except Exception:
            print("Reporting Manager dropdown not found or no options; skipping selection.")
        # 12. Select 'Status' as 'Active'.
        # Assumption: a select element with label "Status" and an option "Active"
        await page.get_by_label("Status").select_option("Active")
        # 13. Fill in 'Password'
        await page.get_by_label("Password").fill(password) # Assumption: input field has a label "Password"
        # 14. Fill in 'Confirm Password' with the same password
        await page.get_by_label("Confirm Password").fill(password) # Assumption: input field has a label "Confirm Password"

        # 15. Click 'Save' or 'Add' button.
        print("Step 15: Clicking 'Save' button to add employee.")
        # Assumption: The button to submit the form is named "Save" or "Add".
        # Using get_by_role("button", name="Save") as a common pattern.
        await page.get_by_role("button", name="Save").click()

        # Expected Result: The employee 'Jane Smith' is successfully added and appears in the employee list with all provided details. A success message is displayed.

        # Assertion 1: Verify success message is displayed.
        print("Verifying success message.")
        # Assuming a common success message will appear on the page or as a toast notification.
        # Using .or_ to handle slight variations in success message text.
        await expect(
            page.get_by_text("Employee added successfully")
            .or_(page.get_by_text("Employee created successfully"))
            .or_(page.get_by_role("status", name="Success message"))
        ).to_be_visible(timeout=10000)
        print("Success message displayed: 'Employee added successfully'.")

        # Wait for potential navigation back to the employees list or for the form to close
        await page.wait_for_url(f"{base_url}allemployees")

        # Assertion 2: Verify the new employee appears in the employee list table.
        print(f"Verifying employee '{full_name}' with email '{email}' in the employee list.")

        # Use the filter input available in the provided HTML to search for the new employee by name.
        # Using the exact locator from the provided list: page.get_by_label("NAME Filter Input")
        await page.get_by_label("NAME Filter Input").fill(full_name)
        await page.keyboard.press("Enter") # Trigger the filter search

        # Wait for the table to update and find the employee's full name and email in the grid.
        # Assuming 'gridcell' role is used by the AG Grid for individual cells.
        await expect(page.get_by_role("gridcell", name=full_name)).to_be_visible(timeout=15000)
        await expect(page.get_by_role("gridcell", name=email)).to_be_visible(timeout=15000)
        print(f"Employee '{full_name}' successfully found in the employee list with email '{email}'.")

        print("\nTest TC-ADDEMP-002: Verify successful addition of a new employee PASSED.")

        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())