import asyncio
from playwright.async_api import async_playwright, expect
import datetime
import uuid

async def test_employee_creation_with_special_address():
    async with async_playwright() as p:
        # Launch browser in headless mode (set to False to see the browser)
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Generate unique employee data to avoid conflicts on repeated runs
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:8] # Short unique ID for email
        
        first_name = f"TestFN_{timestamp}"
        last_name = f"TestLN_{timestamp}"
        employee_email = f"test.employee.{unique_id}@{timestamp}.com" # Unique email
        phone_number = "1234567890" # Example phone number
        job_title = "Automation Tester"
        department = "QA" # Assuming a simple text input or default dropdown option
        
        # Test Case Specific Address with special characters and multiple lines
        test_address = "#123, St. Peter's Rd\nApt B-4,\nChennai-600001, India"

        try:
            # 1. Navigate to the base URL (login page)
            print("Navigating to login page...")
            await page.goto("https://dev.urbuddi.com/")
            # Verify that we are on the login page by checking the title
            await expect(page).to_have_title("Login | Urbuddi")

            # Pre-conditions: User is logged in as an administrator/HR
            # NOTE: Replace 'admin@urbuddi.com' and 'password' with actual admin/HR credentials for your environment.
            # Using highly probable generic locators for login fields (by name attribute)
            print("Attempting to log in as admin/HR...")
            await page.fill('input[name="email"]', "admin@urbuddi.com") 
            await page.fill('input[name="password"]', "password")      
            await page.click('button[type="submit"]') # Click the "Sign In" button

            # Wait for navigation after successful login (e.g., to dashboard)
            # Expect URL to change to dashboard
            await page.wait_for_url("**/dashboard") 
            await expect(page).to_have_url("https://dev.urbuddi.com/dashboard")
            print("Logged in successfully and navigated to dashboard.")

            # Test Step 1: Navigate to the 'Add Employee' form.
            # This typically involves clicking an 'Employees' link/button first, then 'Add Employee'.
            print("Navigating to 'Add Employee' form...")
            
            # Click on the 'Employees' navigation link (using text locator)
            await page.click('a:has-text("Employees")')
            # Wait for navigation to the employees list page
            await page.wait_for_url("**/employees")
            await expect(page).to_have_url("https://dev.urbuddi.com/employees")
            print("On Employees list page.")

            # Click the 'Add Employee' button (using text locator)
            await page.click('button:has-text("Add Employee")')
            # Wait for navigation to the 'Add Employee' form
            await page.wait_for_url("**/employees/add") 
            await expect(page).to_have_url("https://dev.urbuddi.com/employees/add")
            print("Successfully navigated to 'Add Employee' form.")

            # Test Step 2: Fill in all mandatory fields with valid data.
            print("Filling mandatory employee details...")
            await page.fill('input[name="firstName"]', first_name)
            await page.fill('input[name="lastName"]', last_name)
            await page.fill('input[name="email"]', employee_email)
            await page.fill('input[name="phone"]', phone_number)
            
            # Assuming Job Title and Department are text inputs for simplicity.
            # If they are dropdowns, `page.select_option()` or click/type would be used.
            await page.fill('input[name="jobTitle"]', job_title)
            await page.fill('input[name="department"]', department)
            
            # Test Step 3: Enter an address containing special characters and multiple lines into the 'Address' field.
            # Assuming the address field is a <textarea> element.
            print(f"Entering address with special characters and multiple lines: \n'''{test_address}'''")
            await page.fill('textarea[name="address"]', test_address) 

            # Test Step 4: Click the 'Submit' or 'Create Employee' button.
            print("Clicking 'Create Employee' button...")
            await page.click('button[type="submit"]:has-text("Create Employee")') # Using type="submit" and text

            # Expected Result: Employee is successfully created.
            # Look for a success notification/toast message
            print("Waiting for employee creation success notification...")
            await expect(page.locator('div[role="status"]')).to_contain_text("Employee created successfully")
            print("Success notification found: 'Employee created successfully'")

            # Verify redirection to the employee list page
            await page.wait_for_url("**/employees") 
            await expect(page).to_have_url("https://dev.urbuddi.com/employees")
            print("Redirected to Employees list page after creation.")

            # Verify the address is saved correctly with all special characters and line breaks preserved.
            # This requires finding the newly created employee and inspecting their details.
            print("Verifying saved address on employee detail page...")
            
            # Search for the employee by their unique email to find them in the list
            await page.fill('input[placeholder="Search by name, email, or department"]', employee_email)
            await page.press('input[placeholder="Search by name, email, or department"]', 'Enter')
            
            # Give a small pause for search results to load
            await page.wait_for_timeout(1000) 

            # Click on the newly created employee's row/link to view details
            # Assuming the full name acts as a clickable element in the list
            employee_row_locator = page.locator(f'text="{first_name} {last_name}"').first
            await expect(employee_row_locator).to_be_visible() # Ensure the employee is found
            await employee_row_locator.click()

            # Wait for navigation to the employee detail page
            # Assuming the URL includes an employee ID or unique identifier like email
            await page.wait_for_url(f"**/employees/**") 
            # Further refinement of URL check for specific employee ID if possible
            # await expect(page).to_have_url(f"https://dev.urbuddi.com/employees/{employee_email_or_id}") # More precise if ID is known
            print(f"On employee detail page for {first_name} {last_name}.")
            
            # Locate the address display field on the detail page and verify its content.
            # NOTE: The exact locator for the displayed address on the detail page might vary.
            # We are assuming a common pattern where a label like "Address:" is followed by its value.
            
            # Try to find an element (e.g., div, p, span) that displays the address content.
            # A common pattern is: `<div>Address:</div><div>[address value here]</div>`
            address_display_value_locator = page.locator('div:has-text("Address:") + div') 
            
            # If the above locator doesn't work, try other common patterns or a broader search.
            if not await address_display_value_locator.is_visible():
                address_display_value_locator = page.locator('p:has-text("Address:") + p')
            if not await address_display_value_locator.is_visible():
                # Fallback: look for a generic element that contains a distinctive part of the address.
                # This is less precise but robust if structure varies.
                print("Specific address display locator not found, trying broader search for address text.")
                address_display_value_locator = page.locator(f'div:has-text("{test_address.splitlines()[0]}")').first # Check for div containing first line
            
            await expect(address_display_value_locator).to_be_visible() # Ensure the address display element is visible
            
            # Get the actual displayed text content. `inner_text()` often preserves visual line breaks (e.g., `<br>` -> `\n`).
            actual_displayed_address = await address_display_value_locator.inner_text()
            
            print(f"\n--- Address Verification ---")
            print(f"Expected address (with newlines): \n'''{test_address}'''")
            print(f"Actual displayed address: \n'''{actual_displayed_address}'''")
            print(f"--- End Address Verification ---\n")

            # For "line breaks preserved", we expect `\n` characters to be present in the retrieved text
            # if the UI renders them (e.g., with <br> tags).
            # Playwright's `inner_text()` is good at capturing visually rendered text.

            # Verify that the actual displayed address contains the special characters and has the same line breaks.
            # Comparing the full string directly for exact match of `\n` if `inner_text()` provides it.
            # This is the strongest assertion for "line breaks preserved".
            expect(actual_displayed_address.strip()).to_equal(test_address.strip())
            
            print("Address verified successfully with all special characters and line breaks preserved.")

        except Exception as e:
            # Capture screenshot on failure for debugging
            await page.screenshot(path=f"failure_screenshot_{timestamp}.png")
            print(f"Test failed: {e}")
            raise # Re-raise the exception to mark the test as failed
        finally:
            await browser.close()
            print("Browser closed.")

if __name__ == '__main__':
    # Run the asynchronous test function
    asyncio.run(test_employee_creation_with_special_address())