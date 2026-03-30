import asyncio
from playwright.async_api import async_playwright, expect
from datetime import datetime
import uuid

async def test_add_new_employee():
    """
    Test Case ID: TC-ADD-EMP-001
    Description: Verify successful addition of a new employee with all mandatory fields filled with valid data.
    """
    async with async_playwright() as p:
        # Launch browser in headed mode as per requirements
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # --- Pre-conditions: 1. User is logged in ---
        print("Navigating to login page...")
        await page.goto("https://dev.urbuddi.com/")

        # Login credentials
        user_email = "srikanth123@optimworks.com"
        user_password = "Srikanth@123"

        # The 'Extracted Available Exact Locators' map does not contain locators for the login page fields.
        # Falling back to Playwright's robust generic locators (placeholder/role) for the login form.
        print(f"Attempting to log in with Email: {user_email}")
        await page.get_by_placeholder("Email").fill(user_email)
        await page.get_by_placeholder("Password").fill(user_password)
        await page.get_by_role("button", name="Login").click()

        # Wait for navigation after login.
        # We expect to land on the /allemployees page or a dashboard from which Employees is accessible.
        try:
            # Wait for the "Employees" navigation item to be visible, indicating successful login and initial load.
            await page.get_by_text("Employees").wait_for(timeout=10000)
            print("Successfully logged in.")
        except Exception:
            print("Login failed or expected element 'Employees' not visible after login.")
            await page.screenshot(path="login_failure.png")
            raise

        # --- Pre-conditions: 2. User has navigated to the 'Employees' section. ---
        # If the current URL is not the employees page, click the 'Employees' navigation link.
        if "/allemployees" not in page.url:
            print("Navigating to 'Employees' section via navigation link...")
            await page.get_by_text("Employees").click()
            await page.wait_for_url("**/allemployees")
            print("Navigated to Employees section.")
        else:
            print("Already on the Employees section.")

        # --- Pre-conditions: 3. The 'Add Employee' form is accessible. ---
        # Verify the 'Add Employee' button is visible, implying the form can be accessed.
        await expect(page.get_by_text("Add Employee")).to_be_visible()
        print("Verified 'Add Employee' button is accessible.")

        # Generate unique employee data for repeatable tests
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id_suffix = uuid.uuid4().hex[:6] # Using a shorter unique string
        
        new_employee_name = f"John Doe {timestamp}"
        new_employee_email = f"john.doe.{unique_id_suffix}@example.com"
        new_employee_id = f"EMP{unique_id_suffix.upper()}"
        new_employee_role = "Employee" 
        new_employee_designation = "Software Engineer"
        new_employee_doj = datetime.now().strftime("%Y-%m-%d") # Today's date in YYYY-MM-DD format
        new_employee_phone = "9876543210"

        print(f"\nGenerated employee data:")
        print(f"  Full Name: {new_employee_name}")
        print(f"  Email: {new_employee_email}")
        print(f"  Employee ID: {new_employee_id}")
        print(f"  Role: {new_employee_role}")
        print(f"  Designation: {new_employee_designation}")
        print(f"  Date of Joining: {new_employee_doj}")
        print(f"  Phone Number: {new_employee_phone}")

        # --- Test Steps ---

        # 1. Click on the 'Add Employee' button.
        print("\nStep 1: Clicking 'Add Employee' button...")
        # Using recommended locator from the map
        await page.get_by_text("Add Employee").click()
        
        # The HTML for the 'Add Employee' form is not provided in the problem description.
        # We will infer locators for form fields using Playwright's get_by_placeholder or get_by_label.
        # Wait for a representative form field to be visible to confirm the form is open.
        await page.get_by_placeholder("Full Name").wait_for(timeout=5000)
        print("Add Employee form is now visible.")

        # 2. Fill 'Full Name' with a valid name.
        print(f"Step 2: Filling 'Full Name' with '{new_employee_name}'...")
        await page.get_by_placeholder("Full Name").fill(new_employee_name)

        # 3. Fill 'Email' with a unique and valid email address.
        print(f"Step 3: Filling 'Email' with '{new_employee_email}'...")
        await page.get_by_placeholder("Email").fill(new_employee_email)

        # 4. Fill 'Employee ID' with a unique alphanumeric ID.
        print(f"Step 4: Filling 'Employee ID' with '{new_employee_id}'...")
        await page.get_by_placeholder("Employee ID").fill(new_employee_id)

        # 5. Select a 'Role' from the dropdown (e.g., 'Employee').
        print(f"Step 5: Selecting 'Role' as '{new_employee_role}'...")
        # Assuming the role dropdown is either a standard <select> or a custom one.
        # Try `get_by_label` for standard selects, fallback to clicking placeholder and text.
        try:
            await page.get_by_label("Role").select_option(new_employee_role)
            print("Role selected using get_by_label.select_option().")
        except Exception:
            print("Could not use select_option, attempting custom dropdown interaction for Role...")
            # Fallback for custom dropdowns: click the dropdown trigger and then the option text
            await page.get_by_placeholder("Select Role").click() # Assuming common placeholder for custom dropdown
            await page.get_by_text(new_employee_role, exact=True).click()
            print("Role selected using custom dropdown interaction.")


        # 6. Fill 'Designation'.
        print(f"Step 6: Filling 'Designation' with '{new_employee_designation}'...")
        await page.get_by_placeholder("Designation").fill(new_employee_designation)

        # 7. Select 'Date of Joining' using the date picker (e.g., today's date).
        print(f"Step 7: Filling 'Date of Joining' with '{new_employee_doj}'...")
        # Assuming direct text entry is possible for the date input field.
        await page.get_by_placeholder("Date of Joining").fill(new_employee_doj)

        # 8. (Optional) Fill 'Phone Number'.
        print(f"Step 8: Filling 'Phone Number' with '{new_employee_phone}'...")
        await page.get_by_placeholder("Phone Number").fill(new_employee_phone)

        # 9. Click the 'Submit' or 'Add' button on the form.
        print("Step 9: Clicking 'Submit' button on the form...")
        # Assuming the submit button has text "Submit"
        await page.get_by_role("button", name="Submit").click()

        # --- Expected Result Verification ---

        # Expected Result 1 & 2: The employee is successfully added, and a success message is displayed.
        print("\nVerifying success message...")
        # Common success message text, adjust if application uses a different message
        success_message_locator = page.get_by_text("Employee added successfully!") 
        await expect(success_message_locator).to_be_visible(timeout=10000)
        print("Assertion Passed: Success message 'Employee added successfully!' displayed.")
        
        # If it's a transient toast message, wait for it to disappear
        await success_message_locator.wait_for(state="hidden", timeout=5000) 

        # Expected Result 3: The new employee appears in the 'Active' employee list.
        print("Verifying the new employee appears in the 'Active' list...")

        # Use the provided recommended locator for filtering by NAME in the AG Grid
        print(f"Filtering employee list by Name: '{new_employee_name}' to verify entry.")
        await page.locator("#ag-28-input").fill(new_employee_name)
        
        # Wait for the grid to update and display the filtered results.
        # Verify the presence of the new employee's name, ID, and email in the grid.
        await expect(page.get_by_text(new_employee_name)).to_be_visible(timeout=10000)
        await expect(page.get_by_text(new_employee_id)).to_be_visible(timeout=10000)
        await expect(page.get_by_text(new_employee_email)).to_be_visible(timeout=10000)
        
        print(f"Assertion Passed: Employee '{new_employee_name}' with ID '{new_employee_id}' and Email '{new_employee_email}' is found in the active employee list.")
        
        # Optionally, clear the filter input after verification
        await page.locator("#ag-28-input").fill("")
        await page.keyboard.press("Enter") # Trigger filter clear

        print("\nTest TC-ADD-EMP-001 completed successfully!")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_add_new_employee())