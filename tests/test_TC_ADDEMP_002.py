import asyncio
from playwright.async_api import async_playwright, expect

# Test Case ID: TC-ADDEMP-002
# Description: Verify error messages for missing mandatory fields when attempting to add a new employee.

async def run_test_tc_addemp_002():
    async with async_playwright() as p:
        # 1. Launch browser in headed mode as required
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # --- Pre-condition: User is logged in as an administrator ---
        print("Navigating to login page...")
        await page.goto("https://dev.urbuddi.com/")

        # Login credentials
        login_email = "srikanth123@optimworks.com"
        login_password = "Srikanth@123"

        # Fill email and password fields.
        # The login page HTML/locators are not in the provided map, so using common Playwright locators.
        # Using get_by_placeholder which is generally robust if IDs are not known or stable.
        await page.get_by_placeholder("Email").fill(login_email)
        print(f"Filled email: {login_email}")

        await page.get_by_placeholder("Password").fill(login_password)
        print(f"Filled password: {login_password}")

        # Click the Sign In button. Assuming common text for the login button.
        await page.get_by_role("button", name="Sign In").click()
        print("Clicked 'Sign In' button. Waiting for successful login navigation...")

        # Wait for navigation to the dashboard or employees page after login
        # Adjusted timeout for potential slower environments
        await page.wait_for_url("https://dev.urbuddi.com/*", timeout=60000) 
        print("Login successful. Navigated to a post-login page.")

        # --- Pre-condition: User has navigated to the 'Employees' section ---
        print("Navigating to 'Employees' section...")
        # Using the recommended locator from the provided map for the 'Employees' navigation link
        await page.get_by_text("Employees").click()
        await page.wait_for_url("https://dev.urbuddi.com/allemployees")
        print("Navigated to 'Employees' page.")

        # --- Pre-condition: The 'Add Employee' button is visible and clickable ---
        # Using the recommended locator from the provided map for the main 'Add Employee' button
        # Based on the HTML, there's a standalone "Add Employee" button in the page-header-container.
        add_employee_button_main_page = page.get_by_text("Add Employee", exact=True)
        await expect(add_employee_button_main_page).to_be_visible()
        await expect(add_employee_button_main_page).to_be_enabled()
        print("'Add Employee' button on the main page is visible and clickable.")

        # --- Test Step 1: Click the 'Add Employee' button ---
        await add_employee_button_main_page.click()
        print("Clicked 'Add Employee' button to open the form/modal.")

        # --- Wait for the 'Add Employee' form/modal to appear ---
        # The HTML for the form itself is not provided, so we assume a common modal structure.
        # We'll expect a heading or a prominent text that indicates the modal is open.
        # Using `get_by_role("heading", name="Add Employee")` as a robust locator for the modal title.
        add_employee_modal_title = page.get_by_role("heading", name="Add Employee").or_(page.get_by_text("Add New Employee"))
        await expect(add_employee_modal_title).to_be_visible()
        print("Add Employee form/modal is open.")

        # --- Test Step 2: In the 'Add Employee' form, intentionally leave mandatory fields blank ---
        # This step requires no explicit Playwright actions, as we are testing *missing* input.
        print("Intentionally leaving mandatory fields blank.")
        # No fill actions here.

        # --- Test Step 3: Click the 'Save' or 'Add Employee' button on the form ---
        # Assuming the submit button within the modal is named "Add Employee" or "Save".
        # We prioritize "Add Employee" as it's consistent with the feature.
        # We use `exact=True` to prevent false positives if there are other similar texts.
        submit_button_in_modal = page.get_by_role("button", name="Add Employee", exact=True).or_(page.get_by_role("button", name="Save", exact=True))
        await submit_button_in_modal.click()
        print("Clicked the submit button ('Add Employee' or 'Save') on the form.")

        # --- Expected Result 1: Appropriate error messages are displayed ---
        print("Verifying error messages for blank mandatory fields...")

        # List of expected error messages based on the test case description
        expected_error_messages = [
            "Full Name is required",
            "Email is required",
            "Phone number cannot be empty",
            "Employee ID is mandatory",
            "Role is required",
            "Designation is required",
            "Date of Joining is required",
            "Password is required"
        ]

        # Iterate through each expected error message and assert its visibility
        for error_msg_text in expected_error_messages:
            error_locator = page.get_by_text(error_msg_text, exact=True)
            await expect(error_locator).to_be_visible(timeout=5000) # Give some time for errors to appear
            print(f"   - Verified error message: '{error_msg_text}' is displayed.")

        # --- Expected Result 2: The 'Add Employee' form/modal remains open ---
        # Re-asserting the visibility of the modal title confirms the form is still open.
        await expect(add_employee_modal_title).to_be_visible()
        print("Verified: Add Employee form/modal remains open as expected.")

        # --- Expected Result 3: The employee is NOT added to the system. ---
        # This is implicitly verified by the form remaining open and displaying error messages.
        # If the form closed, it would indicate a successful (or at least attempted) submission without errors.
        print("Verified: Employee was NOT added to the system (form remained open with errors, indicating submission failure).")

        print("\nTest Case TC-ADDEMP-002: PASSED")

        await browser.close()

# Main function to run the test
async def main():
    await run_test_tc_addemp_002()

if __name__ == "__main__":
    asyncio.run(main())