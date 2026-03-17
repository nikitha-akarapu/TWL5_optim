import asyncio
import uuid
from playwright.async_api import async_playwright, expect

async def main():
    """
    Verifies that the 'Salary' field on the 'Add Employee' form
    rejects negative values and displays an appropriate error message.
    """
    async with async_playwright() as p:
        # Launch browser in non-headless mode for visibility during development/debugging
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        print("Navigating to login page...")
        await page.goto("https://dev.urbuddi.com/")

        # --- Pre-conditions: User is logged in as an administrator/HR ---
        print("Attempting to log in as administrator...")
        # Locators for login fields are based on common patterns and typical dev site structures.
        # Replace 'admin@urbuddi.com' and 'password123' with actual admin credentials if different.
        await page.get_by_placeholder("Email").fill("admin@urbuddi.com")
        await page.get_by_placeholder("Password").fill("password123")
        await page.get_by_role("button", name="Log In").click()

        # Wait for navigation to the dashboard or a known post-login page.
        # This assumes successful login redirects to /dashboard. Adjust if URL is different.
        await page.wait_for_url("**/dashboard", timeout=10000)
        print("Logged in successfully. On Dashboard.")

        # --- Test Step 1: Navigate to the 'Add Employee' form. ---
        print("Navigating to Employees section...")
        # Locate and click the 'Employees' link/button in the navigation.
        await page.get_by_role("link", name="Employees").click()
        await page.wait_for_url("**/employees", timeout=5000)
        print("On Employees list page.")

        print("Clicking 'Add Employee' button...")
        # Locate and click the 'Add Employee' button.
        await page.get_by_role("button", name="Add Employee").click()
        # Wait for the URL to change to the add employee form or for the form title to appear.
        await page.wait_for_url("**/employees/add", timeout=5000)
        print("On 'Add Employee' form.")

        # --- Test Step 2: Fill in all mandatory fields with valid data. ---
        # Using a unique email to avoid conflicts in a real database.
        unique_email = f"test_user_{uuid.uuid4().hex[:8]}@example.com"
        print(f"Filling mandatory fields with data, using email: {unique_email}")

        # Locators are based on common placeholder text or labels. Adjust if actual form differs.
        await page.get_by_label("First Name").fill("Playwright")
        await page.get_by_label("Last Name").fill("Test")
        await page.get_by_label("Email").fill(unique_email)
        await page.get_by_label("Phone").fill("1234567890")
        await page.get_by_label("Address").fill("123 Test Street")

        # For dropdowns like Department and Position, first click to open, then select.
        # Assuming the dropdowns are interactable and have these options.
        # If they are standard <select> elements, page.select_option is more direct.
        # Let's try clicking the input field for department then selecting the option.
        await page.get_by_label("Department").click()
        await page.get_by_role("option", name="IT").click() # Assuming "IT" is an available option

        await page.get_by_label("Position").click()
        await page.get_by_role("option", name="Software Engineer").click() # Assuming "Software Engineer" is available

        # For Hire Date, directly filling might work if it's a simple input or a date picker that accepts direct input.
        await page.get_by_label("Hire Date").fill("2023-01-15") # Example date

        # --- Test Step 3: Enter a negative value (e.g., '-50000') in the 'Salary' field. ---
        print("Entering negative salary value: -50000")
        await page.get_by_label("Salary").fill("-50000")

        # --- Test Step 4: Click the 'Submit' or 'Create Employee' button. ---
        print("Clicking 'Create Employee' button...")
        await page.get_by_role("button", name="Create Employee").click()

        # --- Expected Result: Employee creation fails. An error message 'Salary cannot be negative' is displayed, and the form remains on the screen with input preserved. ---

        print("Verifying expected results...")
        # 1. Employee creation fails. An error message 'Salary cannot be negative' is displayed.
        # This locator assumes the error message is visible on the page, possibly near the field or as a general form error.
        # Adjust the locator if the actual error message text or its container is different.
        error_message_locator = page.locator("text='Salary cannot be negative'")
        await expect(error_message_locator).to_be_visible()
        print(f"Assertion Passed: Error message '{await error_message_locator.text_content()}' is displayed.")

        # 2. The form remains on the screen.
        # We can assert that the 'Add New Employee' title (or similar form element) is still visible.
        await expect(page.get_by_role("heading", name="Add New Employee")).to_be_visible()
        print("Assertion Passed: Add Employee form remains on screen.")

        # 3. Input is preserved.
        # Verify the negative salary value is still present in the input field.
        await expect(page.get_by_label("Salary")).to_have_value("-50000")
        print("Assertion Passed: Negative salary input value is preserved.")

        print("Test EC-017: Verify 'Salary' field rejects negative values - PASSED.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())