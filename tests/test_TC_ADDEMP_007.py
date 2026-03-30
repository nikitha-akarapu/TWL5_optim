import asyncio
from playwright.async_api import async_playwright, expect
from datetime import datetime, timedelta
import random

# --- Configuration ---
BASE_URL = "https://dev.urbuddi.com"
LOGIN_EMAIL = "srikanth123@optimworks.com"
LOGIN_PASSWORD = "Srikanth@123"

async def test_young_employee_birthdate_error():
    async with async_playwright() as p:
        # 1. Launch browser in headed mode
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            # --- Pre-conditions: Login ---
            print("Navigating to login page...")
            await page.goto(f"{BASE_URL}/login")

            # Fill login credentials using assumed common locators for login page
            await page.get_by_label("Email").fill(LOGIN_EMAIL)
            await page.get_by_label("Password").fill(LOGIN_PASSWORD)
            await page.get_by_role("button", name="Login").click()

            # Wait for successful login and navigation to the employees page (or dashboard then employees)
            # Expect navigation to the /allemployees page after login.
            await page.wait_for_url(f"{BASE_URL}/allemployees")
            print("Logged in successfully and navigated to employees page.")

            # Pre-condition check: User is on the 'Employees' page.
            # Verify the "Employees" header is visible on the page.
            await expect(page.get_by_text("Employees").first).to_be_visible() # Assumes "Employees" is the header text
            print("Confirmed user is on the Employees page.")

            # --- Test Steps ---

            # 1. Click on the 'Add Employee' button.
            print("Clicking 'Add Employee' button...")
            # Using the exact locator from the provided options:
            await page.get_by_text("Add Employee").click()

            # Wait for the Add Employee form/modal to appear.
            # Since the form HTML is not provided, we assume a modal or new page with a distinct title/element.
            await page.wait_for_selector("text=Add New Employee", state="visible", timeout=10000) # Assuming "Add New Employee" is a common header for the form
            print("Add New Employee form/modal displayed.")

            # 2. Fill in all mandatory fields with valid data, except 'Birthdate'.
            # These locators are assumed based on common form field labels, as the form HTML is not provided.
            unique_id = random.randint(10000, 99999)
            employee_first_name = f"TestFName{unique_id}"
            employee_last_name = f"TestLName{unique_id}"
            employee_email = f"testuser_{unique_id}@example.com"
            employee_phone = f"9{random.randint(100000000, 999999999)}" # Generates a 10-digit number starting with 9

            print("Filling mandatory fields with valid data...")
            await page.get_by_label("First Name").fill(employee_first_name)
            await page.get_by_label("Last Name").fill(employee_last_name)
            await page.get_by_label("Email").fill(employee_email) # Assuming a dedicated email field for the employee
            await page.get_by_label("Contact Number").fill(employee_phone)
            
            # Assuming Role and Designation are mandatory and are typically dropdowns or text inputs.
            # Selecting an option for 'Role' (assuming 'Employee' is a valid option)
            await page.get_by_label("Role").select_option("Employee")
            # Filling 'Designation' (assuming it's a text input)
            await page.get_by_label("Designation").fill("Junior Tester")

            # 3. Select 'Birthdate' that is less than 18 years ago from the current date.
            # Calculate a birthdate that makes the employee less than 18 years old (e.g., 17 years and 6 months ago).
            current_date = datetime.now()
            birthdate_young = current_date - timedelta(days=(17 * 365) + (6 * 30)) # Approximately 17.5 years ago
            birthdate_str = birthdate_young.strftime("%Y-%m-%d") # Format for date input fields (YYYY-MM-DD)

            print(f"Setting birthdate to: {birthdate_str} (makes employee younger than 18)")
            # Assuming a date input field labeled "Birthdate"
            await page.get_by_label("Birthdate").fill(birthdate_str)

            # 4. Click 'Save' or 'Add' button.
            print("Clicking 'Add' button to submit employee data...")
            # Assuming the form has a button with the text "Add" to submit the new employee.
            await page.get_by_role("button", name="Add").click()

            # --- Expected Result ---
            # An error message 'Employee must be at least 18 years old' (or similar) is displayed.
            print("Verifying error message presence...")
            expected_error_message = "Employee must be at least 18 years old"
            await expect(page.get_by_text(expected_error_message)).to_be_visible()
            print(f"Assertion Passed: Error message '{expected_error_message}' is displayed as expected.")

            # Optional: Further verification that the employee was NOT added
            # (e.g., by checking the URL, form persistence, or trying to navigate back and search).
            # For this test case, the visibility of the error message is the primary pass condition.

        except Exception as e:
            print(f"An error occurred during the test: {e}")
            # Take a screenshot on failure for debugging purposes
            await page.screenshot(path="error_tc_addemp_007.png")
            raise # Re-raise the exception to indicate test failure
        finally:
            await browser.close()
            print("Browser closed.")

async def main():
    await test_young_employee_birthdate_error()

if __name__ == "__main__":
    asyncio.run(main())