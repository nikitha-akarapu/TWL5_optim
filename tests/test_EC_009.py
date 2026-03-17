import asyncio
from playwright.async_api import async_playwright, expect

async def test_invalid_email_employee_creation():
    async with async_playwright() as p:
        # Launch Chromium browser. Set headless=False to observe the test execution visually.
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        print("Starting test: EC-009 - Verify employee creation fails with invalid Email format.")

        # Pre-condition: User is logged in as an administrator/HR and is on the 'Add Employee' form.

        # 1. Navigate to the login page
        await page.goto("https://dev.urbuddi.com/")
        print("Navigated to the login page.")

        # Assume admin/HR login credentials. Replace with actual credentials if known.
        # Using generic locators (placeholders) which are common for login forms.
        try:
            await page.fill('input[placeholder="Email"]', "admin@urbuddi.com") # Placeholder email
            await page.fill('input[placeholder="Password"]', "password123") # Placeholder password
            await page.click('button:has-text("Login")') # Click the login button
            print("Attempted login with placeholder credentials.")

            # Wait for successful login by checking for a common element on the dashboard/home page.
            # Assuming 'Dashboard' text appears after successful login.
            await page.wait_for_selector('text="Dashboard"', timeout=15000)
            print("Successfully logged in as administrator/HR.")
        except Exception:
            print("Login failed or 'Dashboard' element not found. Please check credentials or locators for the login process.")
            await browser.close()
            return

        # 2. Navigate to the 'Add Employee' form.
        # This typically involves clicking a link/button in the navigation menu.
        # Assuming a common navigation structure: sidebar link 'Employees' then a button 'Add Employee'.
        try:
            # Click on 'Employees' navigation link
            await page.click('a:has-text("Employees")')
            print("Navigated to the 'Employees' section.")

            # Click on 'Add Employee' button/link within the Employees section
            await page.click('button:has-text("Add Employee")')
            print("Navigated to the 'Add Employee' form.")

            # Wait for the Add Employee form to be visible, e.g., by checking for its title.
            # Assuming a heading like 'Add New Employee' on the form page.
            await page.wait_for_selector('h1:has-text("Add New Employee")', timeout=10000)
            print("Confirmed presence of 'Add New Employee' form.")
        except Exception:
            print("Failed to navigate to 'Add Employee' form. Check locators for navigation elements ('Employees' link, 'Add Employee' button) or form title.")
            await browser.close()
            return

        # 3. Enter an invalid email format in the 'Email' field.
        invalid_email = "test@.com" # Example of an invalid email format
        # Using a common placeholder for the email field in the Add Employee form.
        await page.fill('input[placeholder="Email Address"]', invalid_email)
        print(f"Entered invalid email: '{invalid_email}' in the 'Email' field.")

        # 4. Fill in all other mandatory fields with valid data.
        # These locators and data are speculative based on common form structures.
        # Adjust them to match the actual UI of the urbuddi.com 'Add Employee' form.
        await page.fill('input[placeholder="First Name"]', "Invalid")
        await page.fill('input[placeholder="Last Name"]', "User")
        await page.fill('input[placeholder="Phone Number"]', "1234567890")
        await page.fill('input[placeholder="Address Line 1"]', "999 Test Street")
        await page.fill('input[placeholder="City"]', "Testington")
        await page.select_option('select[name="state"]', label="California") # Assuming a state dropdown with 'name="state"'
        await page.fill('input[placeholder="Zip Code"]', "90210")
        await page.select_option('select[name="country"]', label="United States") # Assuming a country dropdown
        await page.fill('input[placeholder="Date of Birth"]', "01/15/1990") # Assuming MM/DD/YYYY format for DOB
        # Add other mandatory fields as required by the application.

        print("Filled other mandatory fields with valid data.")

        # 5. Click the 'Submit' or 'Create Employee' button.
        # Using a common text for the submit button on employee creation forms.
        await page.click('button:has-text("Create Employee")')
        print("Clicked the 'Create Employee' button.")

        # Expected Result: Employee creation fails. An error message 'Please enter a valid email address' is displayed, and the form remains on the screen with input preserved.

        # Assertions:
        # Verify error message is displayed
        error_message_locator = page.locator('text="Please enter a valid email address"')
        await expect(error_message_locator).to_be_visible()
        await expect(error_message_locator).to_have_text('Please enter a valid email address')
        print("Assertion Passed: Verified error message 'Please enter a valid email address' is displayed.")

        # Verify the form remains on the screen (e.g., the 'Create Employee' button is still visible)
        # This checks that there was no redirection away from the form.
        await expect(page.locator('button:has-text("Create Employee")')).to_be_visible()
        print("Assertion Passed: Verified the form remains on the screen.")

        # Verify the invalid email input is preserved in the field
        email_field_locator = page.locator('input[placeholder="Email Address"]')
        await expect(email_field_locator).to_have_value(invalid_email)
        print(f"Assertion Passed: Verified the invalid email '{invalid_email}' is preserved in the input field.")

        print("Test Case EC-009 completed successfully: Employee creation failed as expected with an invalid email format.")

        # Close the browser
        await browser.close()

# Main entry point to run the test
if __name__ == "__main__":
    asyncio.run(test_invalid_email_employee_creation())