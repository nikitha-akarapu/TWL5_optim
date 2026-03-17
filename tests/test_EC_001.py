import asyncio
import datetime
import uuid
from playwright.async_api import async_playwright, expect

async def test_employee_creation():
    async with async_playwright() as playwright:
        # Launch a Chromium browser in headless mode (set headless=False for visual debugging)
        browser = await playwright.chromium.launch(headless=True) 
        page = await browser.new_page()

        # --- Test Data Generation ---
        # Generate a unique ID to ensure unique employee data for each test run
        unique_id = str(uuid.uuid4())[:8] 
        # Get today's date for Date of Joining
        current_date = datetime.date.today().strftime("%Y-%m-%d")

        # Define employee data, including mandatory and optional fields
        employee_data = {
            "first_name": f"TestFirstName_{unique_id}",
            "last_name": f"TestLastName_{unique_id}",
            "email": f"test.employee.{unique_id}@example.com",
            "phone_number": f"1234567{unique_id[:3]}",
            "date_of_joining": current_date,
            "gender": "Male", # Assuming 'Male', 'Female', 'Other' are common options in a dropdown
            "designation": "Software Engineer",
            "department": "Engineering",
            "address": f"123 Test St, Test City, TS 12345_{unique_id}",
            "salary": "75000"
        }

        # --- Pre-conditions: User is logged in as an administrator/HR ---
        # 1. Navigate to the login page
        print("Navigating to login page...")
        await page.goto("https://dev.urbuddi.com/")
        await expect(page).to_have_url("https://dev.urbuddi.com/auth/login")

        # 2. Enter login credentials and submit
        # !!! IMPORTANT: Replace these with actual working admin/HR credentials for the 'dev.urbuddi.com' environment !!!
        admin_email = "admin@urbuddi.com" # Placeholder
        admin_password = "password"       # Placeholder

        print(f"Attempting login with email: {admin_email}...")
        await page.get_by_placeholder("Email").fill(admin_email)
        await page.get_by_placeholder("Password").fill(admin_password)
        await page.get_by_role("button", name="Sign in").click()

        # 3. Wait for navigation after successful login and verify a common element on the dashboard
        # Assuming successful login redirects to a dashboard or employees list page
        print("Waiting for post-login navigation...")
        await page.wait_for_url("https://dev.urbuddi.com/**", timeout=30000) # Wait for any URL on the domain
        # Verify successful login by checking for a common element on the dashboard/home page
        await expect(page.locator("text='Dashboard'") or page.locator("text='Employees'")).to_be_visible()
        print("Login successful.")

        # --- Test Steps ---
        # Step 1: Navigate to the 'Add Employee' form.
        print("Navigating to 'Add Employee' form...")
        # First, click on the "Employees" link in the navigation (assuming a sidebar or top menu)
        await page.locator("a[href='/employees']").click()
        # Wait for the employees list page to load and verify its title/header
        await page.wait_for_url("https://dev.urbuddi.com/employees", timeout=10000)
        await expect(page.get_by_text("Employees List")).to_be_visible() 
        
        # Then, click the 'Add Employee' button
        await page.get_by_role("button", name="Add Employee").click()
        # Wait for the add employee form page to load and verify its title/header
        await page.wait_for_url("https://dev.urbuddi.com/employees/add", timeout=10000)
        await expect(page.get_by_text("Add New Employee")).to_be_visible()
        print("Successfully navigated to 'Add New Employee' form.")

        # Step 2 & 3: Enter valid data into all mandatory and optional fields.
        print("Entering employee data into the form...")
        await page.get_by_placeholder("First Name").fill(employee_data["first_name"])
        await page.get_by_placeholder("Last Name").fill(employee_data["last_name"])
        # Using a more specific locator for email to avoid conflict if other email fields exist
        await page.locator("input[type='email'][name='email']").fill(employee_data["email"]) 
        await page.get_by_placeholder("Phone Number").fill(employee_data["phone_number"])
        # Common placeholder for date input fields
        await page.get_by_placeholder("Select Date").fill(employee_data["date_of_joining"]) 
        
        # Gender: Assuming it's a <select> dropdown with 'name="gender"'
        await page.locator("select[name='gender']").select_option(employee_data["gender"]) 

        await page.get_by_placeholder("Designation").fill(employee_data["designation"])
        await page.get_by_placeholder("Department").fill(employee_data["department"])
        await page.get_by_placeholder("Address").fill(employee_data["address"])
        await page.get_by_placeholder("Salary").fill(employee_data["salary"])
        print("All employee data entered.")

        # Step 4: Click the 'Submit' or 'Create Employee' button.
        print("Submitting employee creation form...")
        await page.get_by_role("button", name="Create Employee").click() 

        # --- Expected Result Assertions ---
        # 1. Employee is successfully created. A success message is displayed.
        print("Waiting for success message...")
        # Expect a success toast notification (common class for React/Angular apps) or specific success text
        await expect(page.locator(".Toastify__toast--success") or page.get_by_text("Employee created successfully")).to_be_visible(timeout=10000)
        print("Success message displayed: 'Employee created successfully'.")

        # 2. The form should reset or navigate back to the employee list.
        # Verify navigation to the employee list page
        print("Waiting for navigation back to Employee List...")
        await page.wait_for_url("https://dev.urbuddi.com/employees", timeout=10000)
        await expect(page.get_by_text("Employees List")).to_be_visible() 
        print("Navigated back to Employee List page.")

        # 3. The new employee appears in the employee list.
        # Construct the full name to search for in the list
        full_employee_name = f"{employee_data['first_name']} {employee_data['last_name']}"
        await expect(page.get_by_text(full_employee_name)).to_be_visible(timeout=10000)
        await expect(page.get_by_text(employee_data['email'])).to_be_visible(timeout=10000)
        print(f"New employee '{full_employee_name}' with email '{employee_data['email']}' successfully found in the employee list.")

        print("EC-001: Employee creation test completed successfully!")

        # Close the browser
        await browser.close()


# Standard boilerplate to run the async test function
if __name__ == "__main__":
    asyncio.run(test_employee_creation())