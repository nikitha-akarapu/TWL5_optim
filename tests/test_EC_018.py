import asyncio
from playwright.async_api import async_playwright, expect

async def test_empty_employee_creation_submission():
    async with async_playwright() as p:
        # Launch browser
        # Set headless=False to see the browser actions, useful for debugging.
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # --- Pre-condition: User is logged in as an administrator/HR ---

        # 1. Navigate to the login page
        await page.goto("https://dev.urbuddi.com/login")
        print("Navigated to login page.")

        # IMPORTANT: Replace with actual test credentials for your environment.
        # These are placeholders and will likely fail without valid credentials.
        test_email = "admin@example.com"  # Replace with a valid administrator/HR email
        test_password = "password123"      # Replace with the corresponding password

        # Fill in login credentials
        # Using placeholder attribute for locator, which is a common and robust approach.
        await page.locator('input[placeholder="Email Address"]').fill(test_email)
        await page.locator('input[placeholder="Password"]').fill(test_password)
        
        # Click the Login button
        # Using button text for locator.
        await page.locator('button:has-text("Login")').click()
        print("Attempted login with provided credentials.")

        # Wait for navigation after login. This usually leads to a dashboard or home page.
        # We'll try to wait for a URL specific to the dashboard.
        try:
            await page.wait_for_url("**/dashboard", timeout=15000) # Increased timeout for potential network latency
            print("Successfully logged in and navigated to dashboard URL.")
        except Exception:
            # If the URL isn't exactly '/dashboard', check for a common element on the dashboard
            await expect(page.locator('h1:has-text("Welcome")')).to_be_visible(timeout=10000)
            print("Successfully logged in (dashboard element 'Welcome' found).")

        # --- Test Step: Navigate to the 'Add Employee' form. ---
        # Assuming a common navigation pattern: Click 'Employees' in a sidebar/menu, then 'Add Employee' button.

        # Click on 'Employees' navigation link (often found in a sidebar or main navigation)
        # Using generic locator for a link with text 'Employees'. Adjust if the actual element is different.
        await page.locator('a:has-text("Employees")').click()
        print("Clicked 'Employees' navigation link.")

        # Wait for the Employees list/management page to load, then click 'Add Employee' button.
        # Using generic locator for a button with text 'Add Employee'.
        await page.locator('button:has-text("Add Employee")').click()
        print("Clicked 'Add Employee' button to navigate to the form.")

        # Verify navigation to the 'Add Employee' form by checking its title or a unique element.
        # Assuming the form has an <h1> title like "Add Employee" or "Create New Employee".
        await expect(page.locator('h1:has-text("Add Employee")')).to_be_visible()
        # Store the current URL to verify no redirection after submission
        add_employee_form_url = page.url
        print(f"Navigated to Add Employee form. Current URL: {add_employee_form_url}")

        # --- Test Step: Leave all fields (mandatory and optional) empty. ---
        # Since we just navigated to the form, all fields are naturally empty by default.
        # No explicit action needed here.
        print("All form fields are left empty as per test case requirement.")

        # --- Test Step: Click the 'Submit' or 'Create Employee' button. ---
        # Locate and click the button that submits the form.
        # Using generic locator for a button with text 'Create Employee'.
        await page.locator('button:has-text("Create Employee")').click()
        print("Clicked the 'Create Employee' submit button.")

        # --- Expected Result: Employee creation fails. ---
        # Verify that the URL remains the same, indicating the form was not successfully submitted (no redirect).
        await expect(page).to_have_url(add_employee_form_url)
        print("Verified URL remained the same, indicating form submission failed (no redirect).")

        # --- Expected Result: Validation errors for all mandatory fields are displayed. ---
        # These locators look for specific text content of validation error messages.
        # Inspect the actual application to confirm the exact text and element types (e.g., p, span, div).

        # Assert specific validation error messages are visible
        await expect(page.locator('text="First name is required"')).to_be_visible()
        print("Verified 'First name is required' error message is displayed.")

        await expect(page.locator('text="Last name is required"')).to_be_visible()
        print("Verified 'Last name is required' error message is displayed.")

        await expect(page.locator('text="Email is required"')).to_be_visible()
        print("Verified 'Email is required' error message is displayed.")
        
        # Common additional mandatory fields that might have validation errors
        await expect(page.locator('text="Phone number is required"')).to_be_visible()
        print("Verified 'Phone number is required' error message is displayed.")

        await expect(page.locator('text="Job Title is required"')).to_be_visible()
        print("Verified 'Job Title is required' error message is displayed.")

        await expect(page.locator('text="Department is required"')).to_be_visible()
        print("Verified 'Department is required' error message is displayed.")
        
        # --- Expected Result: The form remains on the screen. ---
        # This is implicitly verified by the URL not changing and error messages being visible.
        # We can explicitly check for the form title again to confirm the form's presence.
        await expect(page.locator('h1:has-text("Add Employee")')).to_be_visible()
        print("Verified the 'Add Employee' form title is still visible, confirming form remains on screen.")

        print("Test EC-018: Verify form submission with all fields empty - PASSED!")

        # Close the browser context and browser
        await context.close()
        await browser.close()

# Run the test
if __name__ == "__main__":
    asyncio.run(test_empty_employee_creation_submission())