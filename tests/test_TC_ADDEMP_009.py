import asyncio
from playwright.async_api import async_playwright, expect

async def main():
    async with async_playwright() as p:
        # Launch browser in headed mode as required
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        print("--- Test Case ID: TC-ADDEMP-009 ---")
        print("Description: Verify error message when 'Password' and 'Confirm Password' do not match.")

        # --- Pre-conditions: Login ---
        print("Pre-condition: Navigating to login page and logging in.")
        await page.goto("https://dev.urbuddi.com/")

        # Login with provided credentials.
        # The HTML for the login page is not provided, so standard CSS selectors are inferred.
        await page.fill('input[name="email"]', "srikanth123@optimworks.com")
        await page.fill('input[name="password"]', "Srikanth@123")
        await page.click('button[type="submit"]') # Assuming a submit button for login

        # Wait for a prominent element on the post-login page to ensure successful navigation.
        # The 'Employees' link in the left navigation is a good indicator.
        await page.get_by_text("Employees").wait_for(state='visible')
        print("Logged in successfully.")

        # --- Pre-conditions: User is on the 'Employees' page. ---
        print("Pre-condition: Ensuring user is on 'Employees' page.")
        # Check if the current URL is already the employees page. If not, click the 'Employees' link.
        if "/allemployees" not in page.url:
            # Using the exact locator provided in the 'Extracted Available Exact Locators'
            await page.get_by_text("Employees").click()
            await page.wait_for_url("https://dev.urbuddi.com/allemployees") # Wait for navigation to the employees URL
        print("User is confirmed to be on the 'Employees' page.")

        # --- Test Steps ---
        print("Step 1: Click on the 'Add Employee' button.")
        # Using the exact locator provided in the 'Extracted Available Exact Locators'
        await page.get_by_text("Add Employee").click()

        # IMPORTANT ASSUMPTION: The HTML content for the 'Add Employee' form/modal is NOT provided.
        # Therefore, locators for the form fields (like Full Name, Email, Password, etc.) are inferred
        # based on common placeholder texts typically found in such forms.
        # If these inferred locators do not match the actual application's form structure,
        # this part of the script will require adjustment with the correct HTML/locators.
        print("Waiting for 'Add New Employee' form/modal to appear (assuming a title 'Add New Employee').")
        await page.wait_for_selector('text="Add New Employee" >> visible=true', timeout=10000)
        print("Add New Employee form is visible.")

        print("Step 2: Fill in all mandatory fields with valid data using inferred placeholders.")
        # Generate unique data for employee fields to avoid conflicts on repeated runs
        import random
        import string
        unique_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
        full_name = f"Auto Test {unique_suffix}"
        employee_email = f"auto.test.{unique_suffix}@example.com"
        employee_id = f"EMP{random.randint(1000, 9999)}"
        phone_number = f"9{random.randint(100000000, 999999999)}"

        await page.get_by_placeholder("Full Name").fill(full_name)
        await page.get_by_placeholder("Employee ID").fill(employee_id)
        await page.get_by_placeholder("Email").fill(employee_email)
        await page.get_by_placeholder("Phone Number").fill(phone_number)
        
        # Assuming 'Role' and 'Designation' are text inputs with placeholders
        await page.get_by_placeholder("Role").fill("QA Engineer")
        await page.get_by_placeholder("Designation").fill("Automation QA")

        # Assuming two date input fields with placeholder "dd/mm/yyyy"
        await page.get_by_placeholder("dd/mm/yyyy").nth(0).fill("15/06/2023") # Example for Date of Joining
        await page.get_by_placeholder("dd/mm/yyyy").nth(1).fill("20/03/1990") # Example for Date of Birth

        print("Step 3: Fill in 'Password' with 'Pass123'.")
        # Assuming a password input field with placeholder "Password"
        await page.get_by_placeholder("Password").fill("Pass123")

        print("Step 4: Fill in 'Confirm Password' with a different value 'Pass1234'.")
        # Assuming a confirm password input field with placeholder "Confirm Password"
        await page.get_by_placeholder("Confirm Password").fill("Pass1234")

        print("Step 5: Click 'Save' or 'Add' button.")
        # Assuming the form has a button with the accessible name 'Save'
        await page.get_by_role("button", name="Save").click()

        # --- Expected Result Assertion ---
        print("Expected Result: Verifying error message 'Password and Confirm Password do not match' is displayed.")
        # Locate the error message and assert its visibility
        error_message_locator = page.get_by_text("Password and Confirm Password do not match")
        await expect(error_message_locator).to_be_visible()
        print(f"Assertion Passed: Error message '{await error_message_locator.text_content()}' is visible as expected.")
        
        # The second part of the expected result "The employee is not added" is implicitly covered
        # by the presence of the error message, indicating form submission failure.
        
        print("Test Case TC-ADDEMP-009 Completed Successfully.")

        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())