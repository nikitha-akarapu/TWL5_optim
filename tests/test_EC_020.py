import asyncio
from playwright.async_api import async_playwright, expect
import datetime
import uuid

# --- Configuration ---
BASE_URL = "https://dev.urbuddi.com/"
# IMPORTANT: Replace these with actual valid administrator/HR test credentials.
# Do NOT use real production credentials here.
ADMIN_EMAIL = "your_admin_email@example.com" # Placeholder: Update with actual admin email
ADMIN_PASSWORD = "your_admin_password" # Placeholder: Update with actual admin password

# --- Helper function for unique email generation ---
def generate_unique_email(base_name="employee"):
    """Generates a unique email address using a timestamp and a random suffix."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = uuid.uuid4().hex[:6]
    return f"{base_name}_{timestamp}_{random_suffix}@example.com"

async def test_date_of_joining_boundary_dates():
    """
    EC-020: Verify 'Date of Joining' accepts boundary dates (today's date, earliest allowed date).
    """
    async with async_playwright() as p:
        # Launch browser in headless mode by default. Set headless=False for visual debugging.
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        print("--- Starting Test: EC-020 Verify 'Date of Joining' boundary dates ---")

        try:
            # Pre-condition: User is logged in as an administrator/HR

            # 1. Navigate to the login page
            print(f"Navigating to {BASE_URL}")
            await page.goto(BASE_URL)
            # Assuming the initial navigation lands on a login page, adjust URL if needed
            await expect(page).to_have_url(f"{BASE_URL}login", timeout=10000)
            print("On login page.")

            # 2. Perform Login
            print("Attempting to log in as administrator...")
            # Using common locators (placeholder, name attribute) for login fields
            await page.fill('input[placeholder="Email"]', ADMIN_EMAIL) # Highly probable locator
            await page.fill('input[placeholder="Password"]', ADMIN_PASSWORD) # Highly probable locator
            await page.click('button:has-text("Login")') # Highly probable locator for login button

            # Wait for navigation after successful login, usually to a dashboard or employees list
            await page.wait_for_url(f"{BASE_URL}dashboard", timeout=15000) # Adjust URL if login redirects elsewhere
            print("Successfully logged in.")

            # 3. Navigate to the 'Add Employee' form.
            # This step assumes a common UI navigation flow: click 'Employees' link, then 'Add Employee' button.
            print("Navigating to 'Add Employee' form...")
            try:
                # First, locate and click the 'Employees' navigation link (e.g., in a sidebar)
                await page.click('a:has-text("Employees")', timeout=10000) # Assuming a link with this text
                await page.wait_for_url(f"{BASE_URL}employees", timeout=10000) # Adjust URL if 'Employees' list is different
                print("Navigated to Employees list page.")
            except Exception:
                print("Could not find 'Employees' navigation link. Assuming 'Add Employee' button is directly accessible or no intermediate step is needed.")

            # Then, locate and click the 'Add Employee' button on the employees list page or dashboard
            await page.click('button:has-text("Add Employee")', timeout=10000) # Assuming a button with this text
            await page.wait_for_url(f"{BASE_URL}employees/add", timeout=10000) # Adjust URL if 'Add Employee' form URL is different
            print("On 'Add Employee' form.")

            # --- Test Step 1: Set 'Date of Joining' to today's date ---
            print("\n--- Scenario 1: Setting 'Date of Joining' to today's date ---")
            today_date_str = datetime.date.today().isoformat()
            employee_first_name_today = f"TestUserToday_{uuid.uuid4().hex[:4]}"
            employee_email_today = generate_unique_email(f"today_{employee_first_name_today}")

            # Fill in all other mandatory fields with valid data
            await page.fill('input[placeholder="First Name"]', employee_first_name_today) # Or input[name="firstName"]
            await page.fill('input[placeholder="Last Name"]', "Doe") # Or input[name="lastName"]
            await page.fill('input[placeholder="Email"]', employee_email_today) # Or input[name="email"]
            await page.fill('input[placeholder="Job Title"]', "Automation QA") # Or input[name="jobTitle"]

            # Set 'Date of Joining' to today's date
            # Assuming the date input is of type="date" and has a name attribute
            await page.fill('input[type="date"][name="dateOfJoining"]', today_date_str) # Or input[placeholder="Date of Joining"]
            print(f"Filled form for {employee_first_name_today} with Date of Joining: {today_date_str}")

            # Click the 'Submit' or 'Create Employee' button
            await page.click('button:has-text("Create Employee")') # Or button[type="submit"] or button:has-text("Submit")

            # Expected Result: Employee is successfully created. No validation errors related to the date.
            # Verify redirection to the employees list page after successful creation
            await expect(page).to_have_url(f"{BASE_URL}employees", timeout=15000)
            # Verify a success message is displayed (common pattern: a toast notification or alert)
            success_message_locator = page.locator('text="Employee created successfully"') # Adjust text if different
            await expect(success_message_locator).to_be_visible()
            print(f"Successfully created employee '{employee_first_name_today}' with today's date.")

            # --- Test Step 2: Repeat with a very old, but valid, historical date ---
            print("\n--- Scenario 2: Setting 'Date of Joining' to Jan 1, 1900 ---")
            # Navigate back to the 'Add Employee' form for the next test
            await page.click('button:has-text("Add Employee")')
            await page.wait_for_url(f"{BASE_URL}employees/add", timeout=10000)
            print("Navigated back to 'Add Employee' form for historical date test.")

            historical_date_str = datetime.date(1900, 1, 1).isoformat()
            employee_first_name_hist = f"TestUserHist_{uuid.uuid4().hex[:4]}"
            employee_email_hist = generate_unique_email(f"hist_{employee_first_name_hist}")

            # Fill in all other mandatory fields with valid, unique data
            await page.fill('input[placeholder="First Name"]', employee_first_name_hist)
            await page.fill('input[placeholder="Last Name"]', "Smith")
            await page.fill('input[placeholder="Email"]', employee_email_hist)
            await page.fill('input[placeholder="Job Title"]', "Historical Archivist")

            # Set 'Date of Joining' to the historical date
            await page.fill('input[type="date"][name="dateOfJoining"]', historical_date_str)
            print(f"Filled form for {employee_first_name_hist} with Date of Joining: {historical_date_str}")

            # Click the 'Submit' or 'Create Employee' button
            await page.click('button:has-text("Create Employee")')

            # Expected Result: Employee is successfully created. No validation errors related to the date.
            # Verify redirection and success message again
            await expect(page).to_have_url(f"{BASE_URL}employees", timeout=15000)
            await expect(success_message_locator).to_be_visible()
            print(f"Successfully created employee '{employee_first_name_hist}' with historical date.")

            # Verify no validation errors related to the date are displayed
            # This is a generic check for common error message containers. Refine if specific locators exist.
            error_message_locators = page.locator('.error-message, .validation-error, [role="alert"][aria-live="assertive"]')
            await expect(error_message_locators).to_have_count(0, timeout=5000) # Assert no error messages are visible
            print("Confirmed no date validation errors were displayed for historical date.")

            print("\n--- Test EC-020 Completed Successfully! All boundary dates accepted. ---")

        except Exception as e:
            print(f"An error occurred during the test: {e}")
            # Take a screenshot on failure for debugging purposes
            await page.screenshot(path="test_failure_ec020_screenshot.png")
            raise # Re-raise the exception to indicate test failure

        finally:
            # Ensure the browser is closed even if the test fails
            await browser.close()

if __name__ == "__main__":
    # To run this test, make sure you have Playwright installed:
    # pip install playwright
    # playwright install
    asyncio.run(test_date_of_joining_boundary_dates())