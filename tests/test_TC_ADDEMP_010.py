import asyncio
from playwright.async_api import async_playwright, expect

# --- Configuration ---
BASE_URL = "https://dev.urbuddi.com/"
LOGIN_EMAIL = "srikanth123@optimworks.com"
LOGIN_PASSWORD = "Srikanth@123"

# Test data for character limit validation
# Assuming common character limits: Full Name ~255, Designation ~50-100
LONG_FULL_NAME = "A" * 256  # String exceeding assumed max length
LONG_DESIGNATION = "B" * 100 # String exceeding assumed max length

# Valid dummy data for other mandatory fields.
# IMPORTANT: The HTML for the 'Add Employee' form is NOT provided in the problem statement.
# Therefore, locators for these fields are based on common web application practices
# (e.g., using `get_by_label` for visible labels) and are assumed to exist.
# This deviates from the strict rule about using only provided HTML/locators for
# *elements of the 'Add Employee' form*, as the relevant HTML for that form is absent.
DUMMY_EMPLOYEE_EMAIL = f"test_emp_{asyncio.get_event_loop().time()}@example.com".replace(".", "") # Unique email
DUMMY_PHONE_NUMBER = "9876543210"
DUMMY_DATE_OF_JOINING = "2023-01-01" # YYYY-MM-DD format for a date input
DUMMY_ROLE = "Employee" # Common default role for a dropdown
DUMMY_DEPARTMENT = "IT" # Common default department for a dropdown

async def login(page):
    """Performs user login as a pre-condition for the test."""
    print("Navigating to login page...")
    await page.goto(BASE_URL)

    # Locators for login fields are assumed as login page HTML/locators are not provided.
    # Using get_by_placeholder and falling back to CSS selector for robustness.
    try:
        await page.get_by_placeholder("Email").fill(LOGIN_EMAIL)
        await page.get_by_placeholder("Password").fill(LOGIN_PASSWORD)
        print("Filled login credentials using placeholders.")
    except Exception:
        # Fallback if placeholders are not present
        await page.locator("input[type='email']").fill(LOGIN_EMAIL)
        await page.locator("input[type='password']").fill(LOGIN_PASSWORD)
        print("Filled login credentials using CSS selectors.")
    
    # Locate and click the login button.
    # Common locators: get_by_role("button", name="Login"), get_by_text("Login")
    try:
        await page.get_by_role("button", name="Login").click()
        print("Clicked login button by role.")
    except Exception:
        await page.get_by_text("Login").click()
        print("Clicked login button by text.")

    # Wait for navigation to the 'Employees' page, which is the expected post-login state.
    await page.wait_for_url(BASE_URL + "allemployees", timeout=15000)
    print("Successfully logged in and navigated to Employees page.")

async def test_character_limit_validation_add_employee():
    """
    Test Case ID: TC-ADDEMP-010
    Description: Verify character limit validation for 'Full Name' and 'Designation' fields.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False) # Launch browser in headed mode as required
        page = await browser.new_page()

        try:
            # Pre-conditions: User is logged in with provided credentials. User is on the 'Employees' page.
            await login(page)

            # Assert that we are on the Employees page by verifying the URL and a visible element.
            await expect(page.url).to_contain("allemployees")
            # Using exact locator provided: page.get_by_text("Employees") from the left navigation
            await expect(page.get_by_text("Employees").first).to_be_visible() 
            await expect(page.get_by_text("Add Employee").first).to_be_visible() # Ensure the Add Employee button is present

            print(f"Executing Test Case ID: TC-ADDEMP-010 - {test_character_limit_validation_add_employee.__doc__.strip()}")

            # Test Step 1: Click on the 'Add Employee' button.
            # Using exact locator provided: page.get_by_text("Add Employee")
            add_employee_button = page.get_by_text("Add Employee").first
            await add_employee_button.click()
            print("Step 1: Clicked 'Add Employee' button.")

            # Assume a modal or a new page appears for the "Add Employee" form.
            # Wait for a key element in the new form, e.g., the 'Full Name' label, to ensure it's loaded.
            await page.wait_for_selector("text=Full Name", timeout=10000)
            print("Add Employee form/modal is now visible.")

            # Test Step 2: Fill in all other mandatory fields with valid data.
            # Test Step 3: Fill 'Full Name' with a string exceeding the assumed maximum length (e.g., 256 characters).
            # Test Step 4: Fill 'Designation' with a string exceeding the assumed maximum length (e.g., 100 characters).
            
            # As the HTML for the 'Add Employee' form is NOT provided, these locators are based on
            # common web form structures. The labels ("Full Name", "Designation", etc.) are assumed to be
            # present as visible labels associated with their respective input fields.
            
            # Fill 'Full Name' with the excessively long string
            full_name_input = page.get_by_label("Full Name")
            await expect(full_name_input).to_be_visible()
            await full_name_input.fill(LONG_FULL_NAME)
            print(f"Step 3: Filled 'Full Name' with {len(LONG_FULL_NAME)} characters.")

            # Fill 'Designation' with the excessively long string
            designation_input = page.get_by_label("Designation")
            await expect(designation_input).to_be_visible()
            await designation_input.fill(LONG_DESIGNATION)
            print(f"Step 4: Filled 'Designation' with {len(LONG_DESIGNATION)} characters.")

            # Fill other assumed mandatory fields with valid dummy data
            await page.get_by_label("Employee Email").fill(DUMMY_EMPLOYEE_EMAIL)
            await page.get_by_label("Phone Number").fill(DUMMY_PHONE_NUMBER)
            await page.get_by_label("Date of Joining").fill(DUMMY_DATE_OF_JOINING)
            
            # Assuming Role and Department are select dropdowns
            await page.get_by_label("Role").select_option(DUMMY_ROLE)
            await page.get_by_label("Department").select_option(DUMMY_DEPARTMENT)
            print("Step 2: Filled other mandatory fields with valid data.")

            # Test Step 5: Click 'Save' or 'Add' button.
            # Assuming the submission button is labeled "Add" or "Save".
            save_or_add_button = page.get_by_role("button", name="Add")
            if not await save_or_add_button.is_visible():
                save_or_add_button = page.get_by_role("button", name="Save")
            
            await expect(save_or_add_button).to_be_visible()
            await save_or_add_button.click()
            print("Step 5: Clicked 'Save' or 'Add' button.")

            # Expected Result: If a character limit is enforced, an error message
            # 'Full Name exceeds character limit' or 'Designation exceeds character limit'
            # (or similar) should be displayed.

            # Locate the expected error messages. Searching for text content as their specific
            # element structure is unknown without the form's HTML.
            full_name_error = page.get_by_text("Full Name exceeds character limit", exact=False)
            designation_error = page.get_by_text("Designation exceeds character limit", exact=False)
            
            # Assert that both expected error messages are visible
            await expect(full_name_error).to_be_visible(timeout=5000)
            print(f"Verification: Found error message for Full Name: '{await full_name_error.text_content()}'")
            
            await expect(designation_error).to_be_visible(timeout=5000)
            print(f"Verification: Found error message for Designation: '{await designation_error.text_content()}'")

            print("Test TC-ADDEMP-010 passed: Character limit validation messages for 'Full Name' and 'Designation' were displayed as expected.")

        except Exception as e:
            print(f"Test TC-ADDEMP-010 failed: {e}")
            # Capture a screenshot on failure for debugging
            await page.screenshot(path="tc_addemp_010_failure.png")
            raise # Re-raise the exception to mark the test as failed
        finally:
            await page.close()
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_character_limit_validation_add_employee())