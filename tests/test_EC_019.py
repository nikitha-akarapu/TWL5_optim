import asyncio
from playwright.async_api import async_playwright, expect

async def test_cancel_add_employee():
    async with async_playwright() as p:
        # Launch the browser. Set headless=False to see the browser UI.
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # --- Test Case ID: EC-019 ---
        # Description: Verify 'Cancel' button functionality.

        # Pre-conditions: User is logged in as an administrator/HR and is on the 'Add Employee' form.

        print("Step 1: Navigate to the login page.")
        await page.goto("https://dev.urbuddi.com/auth/login")
        await expect(page).to_have_url("https://dev.urbuddi.com/auth/login")

        print("Step 2: Log in as administrator/HR.")
        # IMPORTANT: Replace "admin@example.com" and "password123" with actual administrator/HR credentials
        # for dev.urbuddi.com. These are placeholders.
        await page.fill('input[placeholder="Email"]', "admin@example.com")
        await page.fill('input[placeholder="Password"]', "password123")
        await page.click('button:has-text("Log In")')

        # Wait for the navigation to complete after login.
        # This will wait until the URL is no longer the login URL.
        await page.wait_for_url(lambda url: url != "https://dev.urbuddi.com/auth/login", timeout=10000)
        print(f"Logged in. Current URL: {page.url}")

        # --- Test Steps: ["Navigate to the 'Add Employee' form."] ---
        print("Step 3: Navigate to the 'Employees' list page.")
        # Assuming there's a navigation link or button with the text "Employees".
        await page.click('a:has-text("Employees")')
        await page.wait_for_url("https://dev.urbuddi.com/employees", timeout=10000)
        await expect(page).to_have_url("https://dev.urbuddi.com/employees")
        print("On Employees list page.")

        print("Step 4: Click the 'Add Employee' button to open the form.")
        # Assuming there's a button with the text "Add Employee" on the employee list page.
        await page.click('button:has-text("Add Employee")')
        await page.wait_for_url("https://dev.urbuddi.com/employees/add", timeout=10000)
        await expect(page).to_have_url("https://dev.urbuddi.com/employees/add")
        
        # Assert that the 'Add Employee' form heading is visible.
        await expect(page.locator('h1:has-text("Add Employee")')).to_be_visible()
        print("On 'Add Employee' form.")

        # --- Test Steps: ['Optionally, enter some data into a few fields.'] ---
        print("Step 5: Enter some optional data into a few fields.")
        # Filling common employee fields using placeholder text as locators.
        await page.fill('input[placeholder="First Name"]', "CancelTest")
        await page.fill('input[placeholder="Last Name"]', "User")
        await page.fill('input[placeholder="Email"]', "cancel.test@example.com")
        await page.fill('input[placeholder="Phone Number"]', "1234567890")
        
        # Verify that the data was entered into the fields.
        await expect(page.locator('input[placeholder="First Name"]')).to_have_value("CancelTest")
        await expect(page.locator('input[placeholder="Email"]')).to_have_value("cancel.test@example.com")
        print("Data entered into form fields.")

        # --- Test Steps: ["Click the 'Cancel' button."] ---
        print("Step 6: Click the 'Cancel' button.")
        # Locate and click the 'Cancel' button.
        await page.click('button:has-text("Cancel")')
        print("Clicked 'Cancel' button.")

        # --- Expected Result Verification ---
        # "The form is closed or cleared, and the user is redirected to the previous page (e.g., Employee List page)
        # without creating a new employee. Any unsaved data should be lost."

        print("Step 7: Verify redirection to the previous page (Employee List page).")
        # Wait for the URL to change back to the employees list page.
        await page.wait_for_url("https://dev.urbuddi.com/employees", timeout=10000)
        await expect(page).to_have_url("https://dev.urbuddi.com/employees")
        print("Successfully redirected to Employee List page.")

        print("Step 8: Verify the 'Add Employee' form is closed and its elements are not visible.")
        # Assert that the 'Add Employee' heading and some input fields are no longer visible.
        await expect(page.locator('h1:has-text("Add Employee")')).not_to_be_visible()
        await expect(page.locator('input[placeholder="First Name"]')).not_to_be_visible()
        await expect(page.locator('input[placeholder="Email"]')).not_to_be_visible()
        print("Add Employee form elements are no longer visible.")
        
        # Optionally, verify an element specific to the Employee List page is visible to confirm correct page load.
        await expect(page.locator('h1:has-text("Employees")')).to_be_visible()

        print("\nTest EC-019 'Verify Cancel button functionality' PASSED successfully.")

        await browser.close()

if __name__ == "__main__":
    # Run the asynchronous test function
    asyncio.run(test_cancel_add_employee())