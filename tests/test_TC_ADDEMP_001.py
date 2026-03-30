import asyncio
from playwright.async_api import async_playwright, expect
from datetime import datetime, timedelta
import uuid

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # --- Pre-condition: User Login ---
        print("Navigating to base URL for login...")
        # Navigating to the base URL which typically redirects to the login page if not authenticated.
        await page.goto("https://dev.urbuddi.com/")
        await page.wait_for_load_state('networkidle') # Wait for initial page load and any redirects.
        
        # Attempting to fill login credentials.
        # The HTML for the login page is not provided, nor are specific locators mapped for it.
        # Therefore, strict CSS selectors based on common input 'name' attributes are used as fallback.
        print("Attempting to fill login credentials...")
        await page.locator("input[name='email']").fill("srikanth123@optimworks.com")
        await page.locator("input[name='password']").fill("Srikanth@123")
        
        # Click the login button.
        # Assuming a common CSS selector for the login button, as its HTML is not provided.
        await page.locator("button[type='submit']").click()
        
        # Wait for navigation to the 'Employees' page after successful login.
        # This URL also serves as a confirmation of successful login.
        await page.wait_for_url("https://dev.urbuddi.com/allemployees")
        print("Logged in successfully and navigated to Employees page URL.")

        # Verify page title to confirm being on the Employees page.
        # The HTML snippet shows <p class="sc-feUZmu qNlEl">Employees</p>.
        await expect(page.locator(".sc-feUZmu.qNlEl")).to_have_text("Employees")
        print("Verified 'Employees' page title is displayed.")

        # --- Test Step 1: Click on the 'Add Employee' button. ---
        print("Clicking 'Add Employee' button...")
        # Using the exact locator from the provided 'Extracted Available Exact Locators' map.
        await page.get_by_text("Add Employee").click()
        
        # Wait for the add employee form to load and become visible.
        # Assuming the form appears and has an input field for 'Full Name'.
        # Since the 'Add Employee' form HTML is not provided, using a common CSS selector.
        await page.wait_for_selector("input[name='fullName']")
        print("Add Employee form dialog/page opened.")

        # Generate unique data for the new employee to prevent conflicts on re-runs.
        unique_id = str(uuid.uuid4())[:4]
        employee_full_name = f"John Doe {unique_id}"
        employee_email = f"john.doe.{unique_id}@example.com"
        
        current_date = datetime.now()
        joining_date = current_date.strftime("%Y-%m-%d")
        # Calculate birthdate ensuring the employee is 25 years old (satisfies 18+).
        birth_date = (current_date - timedelta(days=365*25)).strftime("%Y-%m-%d") 
        employee_phone = "9876543210"
        employee_password = "Password123!"

        # --- Test Steps 2-11: Fill in employee details. ---
        print("Filling employee details with unique data...")
        # Locators for form fields are assumed to be CSS selectors based on 'name' attributes
        # as the 'Add Employee' form HTML content was not provided and no specific Playwright locators are mapped for them.
        await page.locator("input[name='fullName']").fill(employee_full_name)
        await page.locator("input[name='email']").fill(employee_email)
        
        # Select 'Role' from the dropdown - assuming 'Developer' is a valid visible option.
        await page.locator("select[name='role']").select_option("Developer") 
        
        await page.locator("input[name='designation']").fill("Software Engineer") 
        await page.locator("input[name='joiningDate']").fill(joining_date) 
        await page.locator("input[name='birthdate']").fill(birth_date) 
        await page.locator("input[name='phoneNumber']").fill(employee_phone) 
        
        # Select 'Gender' from the dropdown - assuming 'Male' is a valid visible option.
        await page.locator("select[name='gender']").select_option("Male") 
        
        await page.locator("input[name='password']").fill(employee_password) 
        await page.locator("input[name='confirmPassword']").fill(employee_password) 
        print("All mandatory employee details filled successfully.")

        # --- Test Step 12: Click 'Save' or 'Add' button. ---
        print("Clicking 'Save' button to add the employee...")
        # Assuming a 'Save' button exists on the form.
        # Since the button HTML for the form is not provided, using a CSS selector by visible text.
        await page.locator("button:has-text('Save')").click() 
        
        # Wait for the form submission to complete and the page to navigate back to the employees list.
        await page.wait_for_url("https://dev.urbuddi.com/allemployees") 
        
        # --- Expected Result: Verify a success message is displayed. ---
        # Assuming a toast notification or similar element displays "Employee added successfully".
        # Using a Playwright locator based on visible text content.
        print("Verifying success message is displayed...")
        await expect(page.get_by_text("Employee added successfully")).to_be_visible()
        print("Success message 'Employee added successfully' confirmed.")

        # --- Expected Result: Verify the new employee appears in the employee list with 'Active' status. ---
        print(f"Verifying employee '{employee_full_name}' in the employee list with 'Active' status...")
        
        # Ensure the 'Active' tab is selected to view newly added employees.
        # Using the exact locator from the provided 'Extracted Available Exact Locators' map.
        await page.get_by_text("Active").click()
        
        # Wait for the data grid to potentially reload or filter after clicking the 'Active' tab.
        # This might involve waiting for the employee's name to appear in the grid.
        
        # Locate the employee's row in the AG Grid.
        # The AG Grid structure elements (.ag-root-wrapper-body, .ag-row) are derived from the provided HTML.
        # Using a CSS selector to find the row that contains the unique full name.
        employee_row_locator = page.locator(f".ag-root-wrapper-body .ag-row:has-text('{employee_full_name}')")
        await expect(employee_row_locator).to_be_visible(timeout=10000) # Increased timeout for grid data to load
        
        # Verify that 'Active' status text is visible within the located employee's row.
        await expect(employee_row_locator.locator("text='Active'")).to_be_visible()
        print(f"Employee '{employee_full_name}' found in the list with 'Active' status. Test PASSED.")

        await browser.close()
        print("Browser closed. Test execution finished.")

if __name__ == "__main__":
    asyncio.run(main())