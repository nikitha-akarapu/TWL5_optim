import asyncio
import os
import random
import string
from playwright.async_api import async_playwright, expect

# Configuration for the test
BASE_URL = "https://dev.urbuddi.com/"
# It's recommended to use environment variables for sensitive data like credentials.
# If environment variables are not set, default values are provided for demonstration.
ADMIN_EMAIL = os.environ.get("URBUDDI_ADMIN_EMAIL", "admin@admin.com") # Replace with a valid admin email for the dev environment
ADMIN_PASSWORD = os.environ.get("URBUDDI_ADMIN_PASSWORD", "admin123") # Replace with the corresponding password
MAX_FIRST_NAME_LENGTH = 50

async def test_employee_first_name_max_length_validation():
    """
    Test Case ID: EC-014
    Description: Verify 'First Name' field correctly handles maximum allowed length (50 characters).
    """
    async with async_playwright() as p:
        # Launch browser in headless mode (set headless=False to watch the test run)
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            print(f"Starting test for EC-014: Verify 'First Name' max length ({MAX_FIRST_NAME_LENGTH} chars).")

            # --- Pre-conditions: User is logged in as an administrator/HR ---
            print("Navigating to login page...")
            await page.goto(BASE_URL)

            # Fill in login credentials using common placeholder/id locators
            await page.fill('input[placeholder="Email"], input[id="email"]', ADMIN_EMAIL)
            await page.fill('input[placeholder="Password"], input[id="password"]', ADMIN_PASSWORD)
            
            # Click the sign-in button
            await page.click('button:has-text("Sign in"), button[type="submit"]')
            
            # Wait for successful login and navigation to dashboard (adjust URL pattern as needed)
            await page.wait_for_url(f"{BASE_URL}dashboard*", timeout=10000)
            print("Successfully logged in as administrator/HR.")

            # --- Navigate to the 'Add Employee' form ---
            print("Navigating to 'Add Employee' form...")
            # Assuming there's an 'Employees' link in the sidebar/navigation
            await page.click('a:has-text("Employees")')
            await page.wait_for_url(f"{BASE_URL}employees*", timeout=10000)

            # Assuming there's an 'Add Employee' button on the Employees list page
            await page.click('button:has-text("Add Employee"), a:has-text("Add Employee")')
            # Wait for the Add Employee form URL (adjust URL pattern as needed)
            await page.wait_for_url(f"{BASE_URL}employees/add*", timeout=10000)
            print("Successfully navigated to 'Add Employee' form.")

            # --- Test Step: Verify input field does not allow more than 50 characters (client-side) ---
            first_name_field_locator = page.locator('input[placeholder="First Name"], input[id="firstName"]')
            
            # Generate a string slightly longer than the maximum allowed length
            long_first_name_attempt = 'A' * (MAX_FIRST_NAME_LENGTH + 5) # 55 characters
            print(f"Attempting to fill First Name field with {len(long_first_name_attempt)} characters...")
            
            await first_name_field_locator.fill(long_first_name_attempt)
            
            # Retrieve the actual value from the input field
            actual_first_name_value = await first_name_field_locator.input_value()
            print(f"Actual value in First Name field: '{actual_first_name_value}' (length: {len(actual_first_name_value)})")
            
            # Assert that the field's value is truncated to the maximum allowed length
            # This verifies the client-side maxlength attribute is working.
            expect(first_name_field_locator).to_have_value('A' * MAX_FIRST_NAME_LENGTH)
            print(f"Assertion Passed: First Name field correctly truncated input to {MAX_FIRST_NAME_LENGTH} characters client-side.")

            # Clear the field for the next step
            await first_name_field_locator.clear()

            # --- Test Step: Enter a First Name with exactly 50 characters (max length) ---
            valid_first_name = ''.join(random.choice(string.ascii_letters) for _ in range(MAX_FIRST_NAME_LENGTH))
            print(f"Filling First Name with exactly {MAX_FIRST_NAME_LENGTH} characters: {valid_first_name}")
            await first_name_field_locator.fill(valid_first_name)

            # --- Test Step: Fill in all other mandatory fields with valid data ---
            # Generate unique identifiers to avoid conflicts
            unique_id = ''.join(random.choices(string.digits, k=4))
            employee_last_name = f"LastName{unique_id}"
            employee_email = f"employee.test.{unique_id}@urbuddi.com"
            employee_phone = f"555-01{unique_id}"

            await page.fill('input[placeholder="Last Name"], input[id="lastName"]', employee_last_name)
            print(f"Filled Last Name: {employee_last_name}")
            
            await page.fill('input[placeholder="Email"], input[id="email"]', employee_email)
            print(f"Filled Email: {employee_email}")
            
            await page.fill('input[placeholder="Phone Number"], input[id="phone"]', employee_phone)
            print(f"Filled Phone Number: {employee_phone}")

            await page.fill('input[placeholder="Job Title"], input[id="jobTitle"]', "Automation QA")
            print("Filled Job Title: Automation QA")

            # Assuming 'Department' is a dropdown/select element. If it's an input, use `fill`.
            department_locator = page.locator('select[id="department"], select[name="department"]')
            if await department_locator.is_visible():
                # Select the first available option that is not empty
                options = await department_locator.locator('option').all_text_contents()
                if options and (len(options) > 1 and options[0] == "" or len(options) == 1 and options[0] != ""):
                    await department_locator.select_option(options[1] if options[0] == "" else options[0])
                    print(f"Selected Department: {await department_locator.evaluate('el => el.value')}")
                else:
                    print("No suitable department option found or Department field might be an input.")
            else:
                # Fallback if Department is an input field (common alternative)
                await page.fill('input[placeholder="Department"], input[id="department"]', "Engineering")
                print("Filled Department (as input): Engineering")
            
            await page.fill('input[type="date"], input[placeholder="Start Date"]', "2023-01-01")
            print("Filled Start Date: 2023-01-01")

            # Assuming password fields are mandatory for the new employee
            try:
                await page.fill('input[placeholder="Password"], input[id="password"] >> nth=1', "Password123!") # Use nth=1 if there are multiple 'Password' placeholders
                await page.fill('input[placeholder="Confirm Password"], input[id="confirmPassword"]', "Password123!")
                print("Filled employee password fields.")
            except Exception:
                print("Employee password fields not found or not required, skipping.")

            # --- Test Step: Click the 'Submit' or 'Create Employee' button ---
            print("Clicking 'Create Employee' button...")
            await page.click('button:has-text("Create Employee"), button[type="submit"]')

            # --- Expected Result: Employee is successfully created ---
            # Look for a success message (e.g., a toast notification) or redirection
            await page.wait_for_selector('text="Employee created successfully"', timeout=10000)
            print("Assertion Passed: 'Employee created successfully' message appeared.")

            # --- Expected Result: The First Name is saved correctly without truncation ---
            # Navigate back to the employees list to verify the created employee
            await page.goto(f"{BASE_URL}employees")
            print("Navigated back to Employees list to verify created employee.")

            # Find the newly created employee in the list by their unique Last Name
            # Assuming employee data is displayed in a table row or similar structure
            employee_row_locator = page.locator(f'tr:has-text("{employee_last_name}")')
            await expect(employee_row_locator).to_be_visible(timeout=10000)
            print(f"Found new employee in the list: {employee_last_name}.")
            
            # Assert that the full 50-character First Name is present in the employee row
            await expect(employee_row_locator).to_contain_text(valid_first_name)
            print(f"Assertion Passed: First Name '{valid_first_name}' found without truncation in the employee list.")
            
            print("Test EC-014 completed successfully: First Name maximum length handling verified.")

        except Exception as e:
            print(f"Test EC-014 FAILED due to an error: {e}")
            # Take a screenshot on failure for debugging
            screenshot_path = "ec_014_failure_screenshot.png"
            await page.screenshot(path=screenshot_path)
            print(f"Screenshot saved to: {screenshot_path}")
            raise # Re-raise the exception to indicate test failure

        finally:
            # Clean up: Close the browser
            await browser.close()
            print("Browser closed.")

if __name__ == "__main__":
    # To run this script:
    # 1. Install Playwright: `pip install playwright`
    # 2. Install Playwright browser binaries: `playwright install`
    # 3. Set environment variables for URBUDDI_ADMIN_EMAIL and URBUDDI_ADMIN_PASSWORD
    #    Example (Linux/macOS):
    #    export URBUDDI_ADMIN_EMAIL="your_admin_email@example.com"
    #    export URBUDDI_ADMIN_PASSWORD="your_admin_password"
    #    Example (Windows Command Prompt):
    #    set URBUDDI_ADMIN_EMAIL="your_admin_email@example.com"
    #    set URBUDDI_ADMIN_PASSWORD="your_admin_password"
    #    (Or modify the default values at the top of the script directly for quick testing)
    # 4. Run the script: `python your_test_script_name.py`
    
    asyncio.run(test_employee_first_name_max_length_validation())