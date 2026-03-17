from playwright.async_api import async_playwright, expect
import asyncio
import datetime

async def main():
    async with async_playwright() as p:
        # Launch Chromium browser. Set headless=False to watch the test execution.
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # --- Pre-conditions: User is logged in as an administrator/HR and is on the 'Add Employee' form. ---

        # 1. Navigate to the application's login page
        print("Navigating to the application URL...")
        await page.goto("https://dev.urbuddi.com/")

        # Assume standard login fields using common placeholders or roles.
        # Replace with actual admin credentials for a real test environment.
        # If these selectors are incorrect, inspect the page DOM for exact ones.
        try:
            print("Attempting to log in as admin...")
            await page.get_by_placeholder("Email").fill("admin@example.com") # Dummy admin email
            await page.get_by_placeholder("Password").fill("password123") # Dummy admin password
            await page.get_by_role("button", name="Sign in").click()

            # Wait for successful navigation to the dashboard or a common post-login page.
            # Adjust the URL pattern if your application redirects elsewhere.
            await page.wait_for_url("**/dashboard", timeout=10000)
            print("Successfully logged in and navigated to the dashboard.")
        except Exception as e:
            print(f"Login failed or dashboard not reached: {e}")
            await browser.close()
            return

        # 2. Navigate to the 'Add Employee' form.
        print("Navigating to the 'Employees' section...")
        # Click on the 'Employees' navigation link/button.
        await page.get_by_text("Employees", exact=True).click()

        # Wait for the Employees list page to load.
        await page.wait_for_url("**/employees", timeout=10000)
        print("Navigated to Employees list page.")

        print("Clicking 'Add Employee' button...")
        # Click the button or link that takes us to the 'Add Employee' form.
        # Common text patterns are 'Add Employee' or 'Create Employee'.
        try:
            await page.get_by_role("button", name="Add Employee").click()
        except Exception:
            # Fallback if the button name is different or it's a link.
            await page.get_by_text("Add Employee").click()

        # Wait for the 'Add Employee' form to load. Assert its URL and a unique element.
        await page.wait_for_url("**/employees/add", timeout=10000)
        await expect(page.get_by_text("Add Employee", exact=True)).to_be_visible() # Check for form title
        print("Navigated to 'Add Employee' form successfully.")

        # --- Test Steps: ---

        # Step 1: Leave 'Email' field empty.
        # We identify the email input field but do not interact with it to leave it blank.
        email_field_locator = page.get_by_placeholder("Email", exact=True)
        # Ensure the field is indeed empty (e.g., if there's any default value).
        await email_field_locator.fill("") 
        print("Ensured 'Email' field is left empty.")

        # Step 2: Fill in other mandatory fields with valid data.
        print("Filling other mandatory fields with valid data...")

        # First Name
        await page.get_by_placeholder("First Name").fill("TestFirstName")

        # Phone Number (using a valid format)
        await page.get_by_placeholder("Phone Number").fill("1234567890")

        # Date of Joining (assuming a standard text input for date, e.g., YYYY-MM-DD)
        # If it's a date picker, more advanced interactions might be needed.
        today_date = datetime.date.today().strftime("%Y-%m-%d")
        await page.get_by_placeholder("Date of Joining").fill(today_date)
        # Press Enter/Tab to ensure the date input registers if needed
        await page.get_by_placeholder("Date of Joining").press("Enter") 

        # Gender (assuming a dropdown, common selector is 'select_option')
        # Adjust selector if it's radio buttons (e.g., `page.get_by_label("Male").check()`)
        await page.get_by_label("Gender").select_option("Male") 

        # Designation
        await page.get_by_placeholder("Designation").fill("Automation QA Engineer")

        # Department
        await page.get_by_placeholder("Department").fill("IT")

        # Step 3: Click the 'Submit' or 'Create Employee' button.
        print("Clicking the 'Create Employee' button...")
        await page.get_by_role("button", name="Create Employee").click()

        # --- Expected Result Assertions: ---

        # Assertion 1: Employee creation fails.
        # This is verified by ensuring the URL has not changed, meaning we are still on the form.
        await expect(page).to_have_url("**/employees/add")
        print("Assertion Passed: Employee creation failed (remained on the add form).")

        # Assertion 2: An error message 'Email is required' is displayed.
        print("Verifying error message 'Email is required' is displayed...")
        error_message_locator = page.get_by_text("Email is required", exact=True)
        await expect(error_message_locator).to_be_visible()
        print("Assertion Passed: Error message 'Email is required' is visible.")

        # Assertion 3: The form remains on the screen with input preserved.
        # Verify by checking the value of one of the fields we filled.
        await expect(page.get_by_placeholder("First Name")).to_have_value("TestFirstName")
        await expect(page.get_by_placeholder("Phone Number")).to_have_value("1234567890")
        print("Assertion Passed: Form input preserved after submission attempt.")

        print("Test Case EC-003: Verify employee creation fails when 'Email' field is left blank - PASSED.")

        # Close the browser.
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())