import asyncio
from playwright.async_api import async_playwright, expect

async def main():
    async with async_playwright() as p:
        # Launch browser in headless mode by default. Set headless=False for visual debugging.
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Test Case ID: TC-LA-001
        print("--- Starting Test Case TC-LA-001: Verify successful leave application with valid details ---")

        try:
            # 1. Log in to the application using provided credentials
            print("Step 1: Navigating to login page and logging in...")
            await page.goto("https://dev.urbuddi.com/")
            await page.wait_for_load_state('networkidle')

            # Login page elements are not in the provided "Extracted Available Exact Locators" map.
            # Using common Playwright locators for input fields and button.
            await page.locator("#userEmail").fill("srikanth123@optimworks.com")
            await page.locator("#userPassword").fill("Srikanth@123")
            await page.get_by_role("button", name="Login").click()

            # Wait for successful navigation to the dashboard/home page
            await page.wait_for_url("https://dev.urbuddi.com/")
            # Assert that a dashboard element is visible to confirm successful login
            await expect(page.get_by_text("Dashboard")).to_be_visible()
            print("Successfully logged in.")

            # 2. Navigate to the 'Leave Management' section
            print("Step 2: Navigating to 'Leave Management' section...")
            # Using recommended locator: page.get_by_text("Leave Management")
            await page.get_by_text("Leave Management").click()
            await page.wait_for_url("https://dev.urbuddi.com/leave_management")
            await page.wait_for_load_state('networkidle')
            # Assert that the "Leave Management" page header is visible
            await expect(page.locator("p.sc-feUZmu.qNlEl")).to_have_text("Leave Management")
            print("Navigated to 'Leave Management' page.")

            # 3. Click the 'Apply Leave' button
            print("Step 3: Clicking the 'Apply Leave' button...")
            # Using recommended locator: page.get_by_text("Apply Leave")
            await page.get_by_text("Apply Leave", exact=True).click()
            # Wait for the Apply Leave form/modal to appear.
            # Assuming the form has a visible header like "Apply for Leave"
            await page.wait_for_selector("h3:has-text('Apply for Leave')")
            print("Apply Leave form/modal is open.")

            # 4. In the 'Apply Leave' form:
            print("Step 4: Filling the 'Apply Leave' form with valid details...")
            # Locators for the form elements are not in the provided map.
            # Using common Playwright locators (get_by_label, get_by_role)
            # a. Select a 'Leave Type' (e.g., 'Casual Leave')
            await page.get_by_label("Leave Type").select_option("Casual Leave")
            print("Selected Leave Type: Casual Leave.")

            # b. Select 'Start Date' as March 18, 2026
            # Assuming direct input for date fields. If a date picker opens,
            # more complex interaction would be required to navigate the calendar.
            await page.get_by_label("Start Date").fill("03/18/2026")
            await page.keyboard.press("Escape") # Press Escape to close any potential date picker pop-up
            print("Selected Start Date: 03/18/2026.")

            # c. Select 'End Date' as March 20, 2026
            await page.get_by_label("End Date").fill("03/20/2026")
            await page.keyboard.press("Escape") # Press Escape to close any potential date picker pop-up
            print("Selected End Date: 03/20/2026.")

            # d. Enter a 'Reason' for leave (e.g., 'Family Function')
            await page.get_by_label("Reason").fill("Family Function")
            print("Entered Reason: Family Function.")

            # 5. Click the 'Submit' button on the form.
            print("Step 5: Clicking 'Submit' button on the form...")
            # This is the submit button within the form/modal.
            await page.get_by_role("button", name="Submit").click()
            print("Leave application form submitted.")

            # Expected Result:
            # A success message (e.g., 'Leave application submitted successfully') is displayed.
            print("Verifying success message...")
            success_message_locator = page.get_by_text("Leave application submitted successfully")
            await expect(success_message_locator).to_be_visible(timeout=10000) # Increased timeout for message visibility
            print("Success message 'Leave application submitted successfully' displayed.")

            # The newly applied leave request appears in the 'Your History' or 'Requests' section
            # with a 'Pending' status, showing Start Date (March 18, 2026), End Date (March 20, 2026),
            # Request Days (3), Request Type (Casual Leave), and Status (Pending).
            print("Verifying newly applied leave request in 'Your History' table...")

            # Ensure 'Your History' tab is active (it's usually default based on HTML provided)
            await page.get_by_text("Your History", exact=True).click()
            await page.wait_for_load_state('networkidle')
            await page.wait_for_timeout(2000) # Give the grid some time to refresh and render the new entry

            # Define expected values for the new leave entry
            expected_start_date_grid = "03/18/2026"
            expected_end_date_grid = "03/20/2026"
            expected_request_days = "3" # March 18, 19, 20 are 3 days
            expected_request_type = "Casual Leave"
            expected_status = "Pending"

            # Locate the row in the AG Grid that contains all the expected details
            # Using a chained filter for robustness across multiple text contents within a row.
            applied_leave_row = page.locator(
                f".ag-row:has-text('{expected_start_date_grid}')"
                f":has-text('{expected_end_date_grid}')"
                f":has-text('{expected_request_days}')"
                f":has-text('{expected_request_type}')"
                f":has-text('{expected_status}')"
            ).first

            await expect(applied_leave_row).to_be_visible(timeout=15000) # Increased timeout for grid entry visibility
            print("\nVerification successful: Newly applied leave request found in 'Your History' table with details:")
            print(f"  Start Date: {expected_start_date_grid}")
            print(f"  End Date: {expected_end_date_grid}")
            print(f"  Request Days: {expected_request_days}")
            print(f"  Request Type: {expected_request_type}")
            print(f"  Status: {expected_status}")

            print("\n--- Test Case TC-LA-001 PASSED ---")

        except Exception as e:
            print(f"\n--- Test Case TC-LA-001 FAILED ---")
            print(f"Error: {e}")
            # Optional: Take a screenshot on failure
            await page.screenshot(path="failure_tc_la_001.png")
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(main())