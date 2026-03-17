import asyncio
from playwright.async_api import async_playwright, expect
import datetime

# --- Configuration ---
BASE_URL = "https://dev.urbuddi.com/"
ADMIN_EMAIL = "srikanth123@optimworks.com"
ADMIN_PASSWORD = "Srikanth@123"

# --- Test Data for TC-ADDEMP-001 ---
# Using current timestamp for Employee ID and Email to ensure uniqueness for repeated runs
TIMESTAMP = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
EMP_ID = f"EMP_QA_{TIMESTAMP}"
FULL_NAME = "Alice Smith"
EMP_EMAIL = f"alice.smith.{TIMESTAMP}@example.com"
PHONE_NUMBER = "9876543210"
ROLE = "Software Engineer"
DESIGNATION = "Junior Developer"
DATE_OF_JOINING = "2023-01-15" # Format YYYY-MM-DD
EMP_PASSWORD = "Secure@123"

async def login(page):
    """
    Performs the login operation and navigates to the Employees section.
    Assumes standard login form elements (placeholders for email/password, button for sign in).
    These locators are NOT in the 'Extracted Available Exact Locators' map for the Employees page
    and are therefore assumed based on common web application login forms on dev.urbuddi.com.
    """
    print("--- Login Step ---")
    await page.goto(BASE_URL)
    await page.get_by_placeholder("Email").fill(ADMIN_EMAIL)
    await page.get_by_placeholder("Password").fill(ADMIN_PASSWORD)
    await page.get_by_role("button", name="Sign In").click()
    
    # Wait for navigation to the dashboard after successful login
    await page.wait_for_url(BASE_URL + "/dashboard", timeout=10000)
    print(f"Successfully logged in. Current URL: {page.url}")

    # Navigate to the 'Employees' section using the recommended locator
    print("Navigating to 'Employees' section...")
    employees_nav_link = page.get_by_text("Employees")
    await expect(employees_nav_link).to_be_visible()
    await employees_nav_link.click()
    await page.wait_for_url(BASE_URL + "/allemployees", timeout=10000)
    print(f"On Employees page. Current URL: {page.url}")

async def test_tc_addemp_001_add_employee_with_valid_mandatory_fields():
    """
    Test Case ID: TC-ADDEMP-001
    Description: Verify successful addition of a new employee with all valid mandatory fields.
    """
    print(f"\n--- Starting Test Case: TC-ADDEMP-001 (Employee: {FULL_NAME}, ID: {EMP_ID}) ---")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False) # Launch browser in headed mode as required
        page = await browser.new_page()

        try:
            # Pre-conditions: Login and navigation to Employees section
            await login(page)

            # Pre-condition 3: The 'Add Employee' button is visible and clickable.
            print("Verifying 'Add Employee' button visibility and clickability...")
            # Using recommended locator: Element: button type='button' (Text: Add Employee)
            add_employee_button = page.get_by_text("Add Employee") 
            await expect(add_employee_button).to_be_visible(timeout=5000)
            await expect(add_employee_button).to_be_enabled(timeout=5000)
            print("Pre-condition met: 'Add Employee' button is visible and enabled.")

            # Test Step 1: Click the 'Add Employee' button.
            print("Step 1: Clicking 'Add Employee' button...")
            await add_employee_button.click()
            
            # Assume a modal or new page for "Add Employee" appears.
            # We'll wait for a common modal title text to confirm it appeared.
            # This locator ('text="Add New Employee"') is assumed as no specific HTML for the modal was provided.
            await page.wait_for_selector('text="Add New Employee"', state='visible', timeout=10000)
            print("Step 1 completed: 'Add New Employee' form/modal appeared.")

            # Test Step 2: Fill in all mandatory fields with valid data.
            print(f"Step 2: Filling in mandatory fields for Employee ID: {EMP_ID}, Name: {FULL_NAME}...")
            
            # --- IMPORTANT ---
            # The 'Extracted Available Exact Locators' map does NOT contain locators
            # for the 'Add Employee' form fields themselves (Employee ID, Full Name, etc.).
            # As per instructions, we fall back to robust locators like get_by_label,
            # making reasonable assumptions based on typical form structures.

            await page.get_by_label("Employee ID").fill(EMP_ID) # Assumed locator
            await page.get_by_label("Full Name").fill(FULL_NAME) # Assumed locator
            await page.get_by_label("Email").fill(EMP_EMAIL) # Assumed locator
            await page.get_by_label("Phone Number").fill(PHONE_NUMBER) # Assumed locator
            # Assuming 'Role' and 'Designation' are simple text inputs, not dropdowns requiring select_option
            await page.get_by_label("Role").fill(ROLE) # Assumed locator
            await page.get_by_label("Designation").fill(DESIGNATION) # Assumed locator
            # Assuming 'Date of Joining' is a text input accepting YYYY-MM-DD format
            await page.get_by_label("Date of Joining").fill(DATE_OF_JOINING) # Assumed locator
            await page.get_by_label("Password").fill(EMP_PASSWORD) # Assumed locator

            print("Step 2 completed: All mandatory fields filled.")

            # Test Step 3: Click the 'Save' or 'Add Employee' button on the form.
            print("Step 3: Clicking 'Save' button on the form...")
            # Assumed locator for the Save button within the modal/form
            save_button_on_form = page.get_by_role("button", name="Save") 
            await save_button_on_form.click()
            print("Step 3 completed: 'Save' button clicked.")

            # Expected Result 1: A success message (e.g., 'Employee added successfully') is displayed.
            print("Expected Result 1: Verifying success message...")
            # Assumed locator for a common success message
            success_message_locator = page.get_by_text("Employee added successfully") 
            await expect(success_message_locator).to_be_visible(timeout=10000)
            print("Verification 1 successful: 'Employee added successfully' message displayed.")

            # Expected Result 2: The newly added employee appears in the Employees table.
            print(f"Expected Result 2: Verifying new employee {FULL_NAME} (ID: {EMP_ID}) in the table...")
            
            # Use the provided locator for the EMP ID filter input
            # Element: input type='text' (ID: ag-26-input) -> Recommended Locator: page.locator("#ag-26-input")
            emp_id_filter_input = page.locator("#ag-26-input")
            await expect(emp_id_filter_input).to_be_visible(timeout=5000)
            await emp_id_filter_input.fill(EMP_ID)
            await page.keyboard.press("Enter") # Trigger filter application
            await page.wait_for_timeout(2000) # Give some time for the grid to filter and refresh

            # Verify the employee ID and Full Name are present in the table rows
            # This relies on the text being directly visible within the AG-Grid cells.
            await expect(page.get_by_text(EMP_ID)).to_be_visible(timeout=5000)
            await expect(page.get_by_text(FULL_NAME)).to_be_visible(timeout=5000)
            print(f"Verification 2 successful: Employee {FULL_NAME} with ID {EMP_ID} found in the Employees table.")

            # Expected Result 3: The 'Add Employee' form/modal closes.
            print("Expected Result 3: Verifying the 'Add Employee' form/modal closes...")
            # We assume the modal title 'Add New Employee' (used to detect modal opening) is no longer visible
            await expect(page.get_by_text("Add New Employee")).not_to_be_visible(timeout=5000)
            print("Verification 3 successful: 'Add Employee' form/modal closed.")

            print("\n--- Test Case TC-ADDEMP-001 Status: PASSED ---")

        except Exception as e:
            print(f"\n--- Test Case TC-ADDEMP-001 Status: FAILED ---")
            print(f"Error encountered: {e}")
            # Capture a screenshot on failure for debugging
            screenshot_path = f"failure_TC-ADDEMP-001_{TIMESTAMP}.png"
            await page.screenshot(path=screenshot_path)
            print(f"Screenshot saved to: {screenshot_path}")
        finally:
            await browser.close()

if __name__ == "__main__":
    # To run this script, save it as a .py file (e.g., test_add_employee.py)
    # and execute from your terminal using: python -m playwright test test_add_employee.py
    # or directly: python test_add_employee.py
    # Ensure you have Playwright installed: pip install playwright
    # And browsers installed: playwright install
    asyncio.run(test_tc_addemp_001_add_employee_with_valid_mandatory_fields())