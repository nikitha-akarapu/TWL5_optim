import asyncio
from playwright.async_api import async_playwright, expect

async def test_ec_016():
    """
    Test Case ID: EC-016
    Description: Verify 'Salary' field rejects non-numeric input.
    """
    async with async_playwright() as p:
        # Launch browser in headless mode by default, change to False for visual debugging
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            # --- Pre-conditions: User is logged in as an administrator/HR ---
            # Navigate to the login page
            print("Navigating to login page...")
            await page.goto("https://dev.urbuddi.com/login")
            await page.wait_for_load_state("networkidle")

            # Fill login credentials (using placeholder credentials)
            # Replace with actual admin/HR credentials for a real run
            await page.fill('input[type="email"]', "admin@example.com") # Assuming this is an admin email
            await page.fill('input[type="password"]', "password123")  # Assuming a placeholder password
            await page.click('button:has-text("Login")')

            # Wait for navigation after login, assert successful login by checking for a dashboard element
            print("Logging in...")
            await page.wait_for_url("https://dev.urbuddi.com/dashboard", timeout=10000) # Adjust dashboard URL if different
            await expect(page.locator('text="Dashboard"')).to_be_visible() # Check for a common dashboard element
            print("Logged in successfully.")

            # --- Test Step 1: Navigate to the 'Add Employee' form. ---
            # Assuming there's a navigation link or button for "Employees" and then "Add Employee"
            print("Navigating to Add Employee form...")
            await page.click('a[href="/employees"]') # Click on Employees link
            await page.wait_for_load_state("networkidle")
            await page.click('button:has-text("Add Employee")') # Click Add Employee button
            await page.wait_for_url("**/employees/add", timeout=10000) # Adjust Add Employee URL if different
            await expect(page.locator('h1:has-text("Add New Employee")')).to_be_visible() # Verify being on the correct page
            print("On 'Add New Employee' form.")

            # --- Test Step 2: Fill in all mandatory fields with valid data. ---
            # Using generic locators (placeholders or labels)
            print("Filling mandatory fields...")
            await page.fill('input[placeholder="First Name"]', "Test")
            await page.fill('input[placeholder="Last Name"]', "User")
            await page.fill('input[placeholder="Email"]', f"testuser_{await page.evaluate('Math.random().toString(36).substring(7)')}@example.com") # Unique email
            await page.fill('input[placeholder="Phone Number"]', "1234567890")
            await page.fill('input[placeholder="Date of Birth"]', "1990-01-01") # YYYY-MM-DD format
            await page.fill('input[placeholder="Address"]', "123 Test St")
            await page.fill('input[placeholder="City"]', "Testville")
            await page.fill('input[placeholder="State"]', "CA")
            await page.fill('input[placeholder="Zip Code"]', "90210")
            await page.fill('input[placeholder="Job Title"]', "QA Engineer")
            
            # For dropdowns, use select_option
            # Assuming Department is a dropdown with a specific value
            try:
                await page.select_option('select[name="department"]', label="Engineering") # Adjust 'name' or 'id' if different
            except Exception:
                print("Could not find 'department' select field, attempting to fill as input.")
                await page.fill('input[placeholder="Department"]', "Engineering")


            # --- Test Step 3: Enter non-numeric characters in the 'Salary' field. ---
            print("Entering non-numeric data into 'Salary' field...")
            # Locate the salary field. Assuming it's an input with a placeholder or label.
            # If the input type is 'number', Playwright fill might automatically strip non-numeric characters.
            # We'll try to fill it with a string and then check if the error appears.
            await page.fill('input[placeholder="Salary"]', "abcd")
            # Or if it's based on a label: await page.locator('label:has-text("Salary") + input').fill("abcd")

            # --- Test Step 4: Click the 'Submit' or 'Create Employee' button. ---
            print("Clicking 'Create Employee' button...")
            await page.click('button:has-text("Create Employee")')
            await page.wait_for_load_state("domcontentloaded") # Wait for the form submission to process

            # --- Expected Result: Employee creation fails. An error message 'Salary must be a number' is displayed. ---
            print("Verifying expected error message...")
            # Common selectors for error messages: specific text, data-test-id, or a div/span near the field.
            # We'll wait for the specific error message to be visible.
            error_message_locator = page.locator('text="Salary must be a number"')
            await expect(error_message_locator).to_be_visible(timeout=5000)
            print("Success: 'Salary must be a number' error message is displayed.")

            # Optional: Verify the form is still present (employee was not created)
            await expect(page.locator('h1:has-text("Add New Employee")')).to_be_visible()
            print("Success: Employee creation failed, still on 'Add New Employee' form.")

        except Exception as e:
            print(f"Test failed: {e}")
            # Optionally take a screenshot on failure
            await page.screenshot(path="test_failure_ec_016.png")
            raise
        finally:
            # Close the browser
            await browser.close()
            print("Browser closed.")

# To run the test directly
if __name__ == "__main__":
    asyncio.run(test_ec_016())