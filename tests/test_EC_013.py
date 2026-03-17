import asyncio
from playwright.async_api import async_playwright, expect
import datetime
import uuid

async def main():
    async with async_playwright() as p:
        # Launch a Chromium browser in headless mode (set to False to see the browser UI)
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # --- Base URL for the application ---
        base_url = "https://dev.urbuddi.com/"

        print("Navigating to login page...")
        await page.goto(f"{base_url}auth/login")
        # Assert that we are on the login page
        await expect(page).to_have_url(f"{base_url}auth/login")

        # --- Pre-condition: User is logged in as an administrator/HR ---
        # IMPORTANT: Replace these with actual administrator/HR credentials for the dev environment.
        # These are placeholders and may not work.
        admin_email = "admin@example.com" # Example email
        admin_password = "password123" # Example password

        print(f"Attempting to log in with email: {admin_email}")
        # Use common locators for email and password input fields
        await page.fill('input[type="email"]', admin_email)
        await page.fill('input[type="password"]', admin_password)
        # Click the login button, commonly identified by type="submit" or text "Log in"
        await page.click('button[type="submit"]')

        # Wait for navigation after login. Assuming it goes to a dashboard or employees list.
        # Adjust URL or element to wait for based on actual application behavior.
        # A timeout is added in case login is slow or redirects differently.
        try:
            await page.wait_for_url(f"{base_url}dashboard", timeout=15000) # Wait up to 15 seconds for dashboard
            await expect(page).to_have_url(f"{base_url}dashboard")
            print("Successfully logged in and navigated to dashboard (assumed).")
        except Exception:
            print("Login failed or navigation to dashboard was not as expected. Continuing with test assuming login was successful.")
            # If login often redirects to a different page or takes longer, adjust the wait_for_url.
            # For a real test, robust login verification is crucial.

        # --- Test Step 1: Navigate to the 'Add Employee' form. ---
        print("Navigating to 'Employees' list page...")
        # Click on the "Employees" navigation link.
        await page.get_by_role("link", name="Employees").click()
        # Assert that we are on the employees list page
        await page.wait_for_url(f"{base_url}employees", timeout=10000)
        await expect(page).to_have_url(f"{base_url}employees")
        print("On Employees list page.")

        print("Clicking 'Add Employee' button to open the form...")
        # Click the "Add Employee" button, commonly found on the employee list page.
        await page.get_by_role("button", name="Add Employee").click()
        # Assert that we have navigated to the add employee form URL
        await page.wait_for_url(f"{base_url}employees/add", timeout=10000)
        await expect(page).to_have_url(f"{base_url}employees/add")
        print("Successfully navigated to the 'Add Employee' form.")

        # --- Test Step 2: Select a date in the future for 'Date of Joining'. ---
        # Calculate a date 7 days in the future
        future_date = (datetime.date.today() + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
        print(f"Attempting to set 'Date of Joining' to a future date: {future_date}")

        # Locate the 'Date of Joining' input field. Common locators include:
        # - by its 'name' attribute (e.g., 'dateOfJoining')
        # - by its label text (e.g., 'Date of Joining')
        # - by a placeholder (e.g., 'YYYY-MM-DD')
        await page.fill('input[name="dateOfJoining"]', future_date)
        # Alternatively: await page.get_by_label("Date of Joining").fill(future_date)

        # --- Test Step 3: Fill in all other mandatory fields with valid data. ---
        # Generate unique data for employee details to avoid conflicts on repeated test runs.
        unique_suffix = uuid.uuid4().hex[:6] # Unique 6-character string
        first_name = f"FutureDateFN_{unique_suffix}"
        last_name = f"FutureDateLN_{unique_suffix}"
        employee_email = f"future.employee.{unique_suffix}@example.com"
        job_title = "Automation Test Engineer"
        department = "R&D" # Assuming "R&D" is a valid department or a simple text input

        print("Filling in other mandatory employee details...")
        await page.fill('input[name="firstName"]', first_name)
        await page.fill('input[name="lastName"]', last_name)
        await page.fill('input[name="email"]', employee_email)
        await page.fill('input[name="jobTitle"]', job_title)
        # If 'Department' is a dropdown (select element), use select_option:
        # await page.select_option('select[name="department"]', 'R&D')
        # Otherwise, assume it's a text input:
        await page.fill('input[name="department"]', department)

        # --- Test Step 4: Click the 'Submit' or 'Create Employee' button. ---
        print("Clicking the 'Create Employee' button...")
        # Locate the submit button. It might have text like "Create Employee" or "Submit".
        await page.get_by_role("button", name="Create Employee").click()

        # Give the application a moment to process the submission and display the error message.
        await page.wait_for_timeout(2000) # Adjust this timeout based on observed application response time

        # --- Expected Result: Employee creation fails. ---
        # --- Expected Result: An error message 'Date of Joining cannot be in the future' is displayed. ---
        expected_error_message = "Date of Joining cannot be in the future"
        print(f"Verifying the error message: '{expected_error_message}' is displayed.")
        # Locate the error message. It could be a simple text on the page or inside a specific error div/span.
        error_message_locator = page.locator(f"text='{expected_error_message}'")
        await expect(error_message_locator).to_be_visible()
        print("Error message found and is visible.")

        # --- Expected Result: The form remains on the screen with input preserved. ---
        print("Verifying the form remains on the screen and inputs are preserved...")
        # Check if a distinctive element of the 'Add Employee' form is still visible,
        # indicating the form did not submit successfully and navigate away.
        await expect(page.get_by_text("Add New Employee", exact=True)).to_be_visible()
        # Verify that the future date we entered is still present in the 'Date of Joining' field.
        await expect(page.locator('input[name="dateOfJoining"]')).to_have_value(future_date)
        # Optionally, verify other mandatory fields also retained their values.
        await expect(page.locator('input[name="firstName"]')).to_have_value(first_name)
        await expect(page.locator('input[name="email"]')).to_have_value(employee_email)
        print("Form remained on screen and previously entered input is preserved.")

        print("\nTest Case EC-013: Verify employee creation fails with future 'Date of Joining' - PASSED.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())