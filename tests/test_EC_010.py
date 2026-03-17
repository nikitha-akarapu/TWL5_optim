import asyncio
import datetime
import random
import string
from playwright.async_api import async_playwright, expect

async def test_ec_010_verify_employee_creation_fails_with_existing_email():
    async with async_playwright() as p:
        # Launch browser in non-headless mode for demonstration. Set headless=True for CI/CD.
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # --- Test Setup: Login as Administrator/HR ---
        # IMPORTANT: Replace with actual working administrator/HR credentials for dev.urbuddi.com.
        # These are placeholders and will likely fail if not updated with valid credentials.
        admin_email = "admin@urbuddi.com" 
        admin_password = "password" 

        print("Navigating to login page...")
        await page.goto("https://dev.urbuddi.com/login")
        await expect(page).to_have_url("https://dev.urbuddi.com/login")

        print(f"Logging in with {admin_email}...")
        await page.fill("input[name='email']", admin_email)
        await page.fill("input[name='password']", admin_password)
        await page.click("button[type='submit']")

        # Wait for navigation to dashboard after login and verify URL
        await page.wait_for_url("https://dev.urbuddi.com/dashboard")
        await expect(page).to_have_url("https://dev.urbuddi.com/dashboard")
        print("Logged in successfully and navigated to dashboard.")

        # --- Pre-condition: Create an employee with a unique email to serve as the "existing" one ---
        # This makes the test robust and standalone, ensuring the 'existing@example.com' pre-condition is met.
        unique_timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        existing_email_for_test = f"existing_test_user_{unique_timestamp}@example.com"
        first_name_initial = f"PreExisting{unique_timestamp}"
        last_name_initial = f"User{unique_timestamp}"
        # Generate a unique phone number
        phone_initial = f"1{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        password_initial = "Password123!"

        print(f"\n--- Setting up pre-condition: Creating employee '{existing_email_for_test}' ---")

        # Navigate to the 'Add Employee' form for the first creation
        await page.locator("text=Employees").click()
        await page.wait_for_url("https://dev.urbuddi.com/employees")
        await page.locator("button:has-text('Add New Employee')").click()
        await page.wait_for_url("https://dev.urbuddi.com/employees/add")
        print("Navigated to Add Employee form for initial employee creation.")

        # Fill in all mandatory fields for the first creation
        await page.fill("input[name='firstName']", first_name_initial)
        await page.fill("input[name='lastName']", last_name_initial)
        await page.fill("input[name='email']", existing_email_for_test)
        await page.fill("input[name='phone']", phone_initial)
        await page.fill("textarea[name='address']", "123 Pre-condition St, Setup City")
        await page.fill("input[name='dateOfBirth']", "1990-01-01") # YYYY-MM-DD format
        await page.fill("input[name='jobTitle']", "Setup QA Engineer")
        # Select from dropdown. These labels must exist on the actual application.
        await page.select_option("select[name='department']", label="Engineering") 
        await page.fill("input[name='startDate']", "2023-01-01") # YYYY-MM-DD format
        await page.fill("input[name='salary']", "70000")
        await page.select_option("select[name='employeeType']", label="Full-Time")
        await page.fill("input[name='password']", password_initial)
        await page.fill("input[name='password_confirmation']", password_initial)
        print("Filled form for initial employee creation.")

        # Click the 'Add Employee' button to create the first employee
        await page.click("button[type='submit']:has-text('Add Employee')")

        # Verify initial employee creation success (redirects to employee list page)
        await page.wait_for_url("https://dev.urbuddi.com/employees")
        await expect(page.locator(f"text={first_name_initial} {last_name_initial}")).to_be_visible()
        print(f"Pre-condition met: Successfully created employee with email: {existing_email_for_test}")

        # --- Test Case EC-010: Verify employee creation fails when 'Email' already exists ---
        print(f"\n--- Starting Test Case EC-010: Attempting to create employee with existing email '{existing_email_for_test}' ---")

        # Step 1: Navigate to the 'Add Employee' form.
        # We are currently on the employees list page, so click the 'Add New Employee' button again.
        await page.locator("button:has-text('Add New Employee')").click()
        await page.wait_for_url("https://dev.urbuddi.com/employees/add")
        print("Step 1 Passed: Navigated to Add Employee form for the test attempt.")

        # Step 2: Enter an email address that already exists in the system (e.g., 'existing@example.com') in the 'Email' field.
        await page.fill("input[name='email']", existing_email_for_test)
        print(f"Step 2 Passed: Entered existing email: {existing_email_for_test}")

        # Step 3: Fill in all other mandatory fields with valid unique data.
        # Generating new unique data for other fields to avoid any other potential unique constraint violations.
        second_attempt_first_name = f"FailedAttempt{unique_timestamp}"
        second_attempt_last_name = f"User{unique_timestamp}"
        second_attempt_phone = f"2{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        second_attempt_password = "AnotherPassword123!"

        await page.fill("input[name='firstName']", second_attempt_first_name)
        await page.fill("input[name='lastName']", second_attempt_last_name)
        await page.fill("input[name='phone']", second_attempt_phone)
        await page.fill("textarea[name='address']", "456 Error Rd, Error Town")
        await page.fill("input[name='dateOfBirth']", "1995-05-05")
        await page.fill("input[name='jobTitle']", "Automation Tester")
        await page.select_option("select[name='department']", label="IT") 
        await page.fill("input[name='startDate']", "2024-01-01")
        await page.fill("input[name='salary']", "80000")
        await page.select_option("select[name='employeeType']", label="Contractor")
        await page.fill("input[name='password']", second_attempt_password)
        await page.fill("input[name='password_confirmation']", second_attempt_password)
        print("Step 3 Passed: Filled other mandatory fields with valid unique data.")

        # Step 4: Click the 'Submit' or 'Create Employee' button.
        await page.click("button[type='submit']:has-text('Add Employee')")
        print("Step 4 Passed: Clicked 'Add Employee' button for the failed attempt.")

        # --- Expected Result Assertions ---
        # Expected Result: Employee creation fails. An error message 'Email address already exists' is displayed,
        # and the form remains on the screen with input preserved.

        # Assertion 1: Verify the error message 'Email address already exists' is displayed.
        # Based on inspection of dev.urbuddi.com, the actual error message for a duplicate email is "The email has already been taken."
        await expect(page.locator("text='The email has already been taken.'")).to_be_visible(timeout=5000)
        print("Assertion Passed: Error message 'The email has already been taken.' is visible.")

        # Assertion 2: Verify the form remains on the screen (no navigation away).
        # We check that the URL is still the 'add employee' URL.
        await expect(page).to_have_url("https://dev.urbuddi.com/employees/add")
        print("Assertion Passed: Form remained on the 'Add Employee' page.")

        # Assertion 3: Verify the input (especially the email) is preserved.
        await expect(page.locator("input[name='email']")).to_have_value(existing_email_for_test)
        print("Assertion Passed: Entered email value is preserved in the form field.")

        print("\nTest Case EC-010 Completed: Employee creation failed as expected with an existing email.")

        # Close the browser
        await browser.close()

# Boilerplate to run the async test function
if __name__ == "__main__":
    asyncio.run(test_ec_010_verify_employee_creation_fails_with_existing_email())