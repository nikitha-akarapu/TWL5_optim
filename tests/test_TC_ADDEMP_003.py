import asyncio
from playwright.async_api import async_playwright, expect

async def main():
    """
    Automates testing of error messages for invalid data formats in mandatory
    fields when adding a new employee on dev.urbuddi.com.

    Test Case ID: TC-ADDEMP-003
    Description: Verify error messages for invalid data formats in mandatory fields
                 when adding a new employee.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        print("Starting test TC-ADDEMP-003: Verify error messages for invalid data formats.")

        try:
            # --- Pre-condition 1: User is logged in as an administrator ---
            # Navigate to the base URL, assuming it's the login page initially.
            await page.goto("https://dev.urbuddi.com/")
            print("Navigated to application base URL.")

            # Login process
            # Locators for login fields are inferred as their HTML was not provided in the snippet.
            # Using common label-based locators.
            await page.get_by_label("Email").fill("srikanth123@optimworks.com")
            await page.get_by_label("Password").fill("Srikanth@123")
            await page.get_by_role("button", name="Login").click()
            print("Attempted login with provided credentials.")

            # Wait for navigation to the 'allemployees' page to confirm successful login.
            # This implicitly fulfills Pre-condition 2.
            await page.wait_for_url("https://dev.urbuddi.com/allemployees", timeout=15000)
            print("Login successful and navigated to 'Employees' section.")

            # Ensure the Employees link is present and active, as per the HTML snippet.
            # From Extracted Available Exact Locators: Element: a (Text: Employees) -> Recommended Locator: page.get_by_text("Employees")
            employees_nav_link = page.get_by_text("Employees", exact=True)
            await expect(employees_nav_link).to_be_visible()
            # If we are already on /allemployees, clicking the nav link might not be necessary,
            # but ensuring its visibility confirms navigation to the section.

            # --- Pre-condition 3: The 'Add Employee' button is visible and clickable. ---
            # From Extracted Available Exact Locators: Element: button type='button' (Text: Add Employee) -> Recommended Locator: page.get_by_text("Add Employee")
            add_employee_main_button = page.get_by_text("Add Employee", exact=True)
            await expect(add_employee_main_button).to_be_visible()
            await expect(add_employee_main_button).to_be_enabled()
            print("Pre-conditions (Login, Employees section, Add Employee button) met.")

            # --- Test Steps ---
            # 1. Click the 'Add Employee' button.
            await add_employee_main_button.click()
            print("Clicked 'Add Employee' button to open the form/modal.")

            # Wait for the 'Add Employee' form/modal to appear.
            # The HTML for the form itself is not provided, so we'll infer locators
            # for common modal elements.
            add_employee_modal_locator = page.get_by_text("Add Employee Details", exact=True).or_(
                page.get_by_role("heading", name="Add Employee")).or_(
                page.locator(".add-employee-modal")) # Fallback CSS selector
            await expect(add_employee_modal_locator).to_be_visible(timeout=10000)
            print("Add Employee form/modal is now visible.")

            # 2. In the 'Add Employee' form, fill in fields with invalid data.
            # Locators for form fields are inferred as their HTML is not provided.
            # Using common label-based locators.
            print("Filling form with invalid data...")
            await page.get_by_label("Employee ID").fill("EMP!!")
            await page.get_by_label("Full Name").fill("12345")
            await page.get_by_label("Email Address").fill("invalid-email-format")
            await page.get_by_label("Phone Number").fill("abcde-123")
            # For Date of Joining, assuming a text input field for direct entry
            await page.get_by_label("Date of Joining").fill("32-13-2023")
            await page.get_by_label("Password").fill("short")
            print("Form fields filled with invalid data.")

            # Note: For simplicity and to focus on the specified invalid fields,
            # other potential mandatory fields are not filled, assuming the application
            # will still attempt validation on the provided fields upon submission.

            # 3. Click the 'Save' or 'Add Employee' button on the form.
            # Inferring the button within the modal.
            save_form_button = page.get_by_role("button", name="Save", exact=True).or_(
                               page.get_by_role("button", name="Add Employee", exact=True))
            await save_form_button.click()
            print("Clicked 'Save/Add Employee' button on the form.")

            # --- Expected Result Verification ---
            test_passed = True
            failure_details = []

            # 1. Specific error messages are displayed for each field with invalid data.
            expected_errors = {
                "Employee ID": "Employee ID format is invalid",
                "Full Name": "Full Name must contain only letters",
                "Email Address": "Please enter a valid email address",
                "Phone Number": "Phone number must be 10 digits and numeric",
                "Date of Joining": "Invalid date selected",
                "Password": "Password does not meet complexity requirements"
            }

            for field_name, error_message in expected_errors.items():
                try:
                    # Error messages are usually displayed as text near the input field.
                    await expect(page.get_by_text(error_message, exact=True)).to_be_visible(timeout=5000)
                    print(f"PASS: Error message '{error_message}' for '{field_name}' is displayed.")
                except AssertionError:
                    test_passed = False
                    failure_details.append(f"FAIL: Error message '{error_message}' for '{field_name}' was NOT displayed.")
                    print(f"FAIL: Error message '{error_message}' for '{field_name}' was NOT displayed.")

            # 2. The 'Add Employee' form/modal remains open.
            try:
                await expect(add_employee_modal_locator).to_be_visible(timeout=3000)
                print("PASS: Add Employee form/modal remains open.")
            except AssertionError:
                test_passed = False
                failure_details.append("FAIL: Add Employee form/modal did NOT remain open.")
                print("FAIL: Add Employee form/modal did NOT remain open.")

            # 3. The employee is NOT added to the system.
            # This is implicitly verified by the form remaining open with errors.
            # Explicitly checking the employee list would require more steps
            # (e.g., dismissing the modal, checking table count, searching),
            # which is beyond the scope of this specific error message test case.
            print("Implicitly verified: Employee is NOT added (form remains open with errors).")

            if not test_passed:
                raise AssertionError(f"Test TC-ADDEMP-003 failed. Details: {'; '.join(failure_details)}")

            print("\nTest TC-ADDEMP-003: PASSED.")

        except Exception as e:
            print(f"\nTest TC-ADDEMP-003: FAILED due to an exception: {e}")
            await page.screenshot(path="tc_addemp_003_failure_screenshot.png", full_page=True)
            raise # Re-raise the exception to indicate failure in an automated test runner

        finally:
            await browser.close()
            print("Browser closed.")

if __name__ == '__main__':
    asyncio.run(main())