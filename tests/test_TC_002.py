import asyncio
from playwright.async_api import async_playwright, expect
from datetime import datetime, timedelta

async def main():
    async with async_playwright() as p:
        # Launch browser in non-headless mode for visual debugging
        browser = await p.chromium.launch(headless=False, args=["--start-maximized"])
        page = await browser.new_page(no_viewport=True) # Use no_viewport=True with --start-maximized

        # Base URL of the application
        base_url = "https://dev.urbuddi.com/"

        # --- Login Steps (Pre-condition for TC-002) ---
        print("Navigating to application login page...")
        await page.goto(base_url)
        # Wait for the page to be fully loaded, including network requests
        await page.wait_for_load_state('networkidle', timeout=15000)

        print("Entering login credentials...")
        # Locator for email input field (assuming placeholder)
        await page.fill('input[placeholder="Enter your email"]', "srikanth123@optimworks.com")
        # Locator for password input field (assuming placeholder)
        await page.fill('input[placeholder="Enter your password"]', "Srikanth@123")
        
        # Locator for the Login button
        await page.click('button:has-text("Login")')
        
        # Wait for navigation to the dashboard or home page after successful login
        print("Waiting for login to complete and redirect to dashboard...")
        # Adjust the expected URL if the dashboard URL is different
        await page.wait_for_url(f"{base_url}dashboard", timeout=20000) 
        print("Login successful. Currently on dashboard page.")

        # --- Test Case TC-002: Verify mandatory 'Reason' field validation ---

        print("\n--- Executing Test Case TC-002: Verify Reason field mandatory validation ---")
        
        # Step 2: Navigate to the 'Leave Management' section.
        print("Navigating to 'Leave Management' section...")
        # Common locator for navigation links (e.g., in a sidebar or top menu) by text content
        # This assumes "Leave Management" is a direct clickable text.
        try:
            await page.click('text="Leave Management"', timeout=10000)
        except Exception:
            # Fallback locator if the above fails, e.g., if it's nested or has specific attributes
            print("Direct click on 'Leave Management' failed, trying alternative locator...")
            # Assuming 'Leave Management' is part of a navigation list or a menu item
            await page.locator('div[role="navigation"] >> text="Leave Management"').click(timeout=10000)

        # Wait for the URL to change to the leave management page
        await page.wait_for_url(f"{base_url}leave", timeout=15000) 
        print("Successfully navigated to Leave Management page.")

        # Step 3: Click on the 'Apply Leave' button.
        print("Clicking 'Apply Leave' button...")
        # Locator for the "Apply Leave" button on the leave management page
        await page.click('button:has-text("Apply Leave")')
        # Wait for the leave application form/modal to appear. We'll wait for a key element on the form.
        await page.wait_for_selector('text="Leave Type"', timeout=10000) 
        print("Apply Leave form/modal is now open.")

        # Step 4: From the 'Leave Type' dropdown, select 'Sick Leave'.
        print("Selecting 'Sick Leave' from 'Leave Type' dropdown...")
        # Locator for the Leave Type dropdown. Common patterns: <select> element or custom dropdown.
        leave_type_dropdown_locator = 'select[name="leaveType"]' # Standard HTML select
        
        if await page.is_visible(leave_type_dropdown_locator):
            # If it's a standard <select> element
            await page.select_option(leave_type_dropdown_locator, label="Sick Leave")
        else:
            # If it's a custom dropdown (e.g., Ant Design, Material UI), typically involves clicking a div/input
            # and then clicking an option in the opened list.
            print("Standard select not found, attempting custom dropdown interaction (e.g., Ant Design).")
            # Click the dropdown opener (e.g., a div with role="combobox" or a specific class)
            await page.click('div:has-text("Leave Type") >> div[role="combobox"]') 
            # Click the 'Sick Leave' option that appears in the overlay/popup
            await page.click('div[title="Sick Leave"]') # Assuming the option element has title="Sick Leave"
            
        print("Selected 'Sick Leave' as Leave Type.")

        # Step 5: Select a valid 'Start Date' and 'End Date' (a single day in the future).
        print("Selecting future start and end dates...")
        
        # Calculate tomorrow's date
        tomorrow = datetime.now() + timedelta(days=1)
        # Format the date as 'YYYY-MM-DD', which is commonly accepted by HTML5 date inputs
        tomorrow_str = tomorrow.strftime('%Y-%m-%d') 

        # Locators for Start Date and End Date input fields
        start_date_input_locator = 'input[placeholder="Start Date"]'
        end_date_input_locator = 'input[placeholder="End Date"]'

        # Fill the date inputs directly. Playwright handles date pickers well with direct input.
        await page.fill(start_date_input_locator, tomorrow_str)
        await page.fill(end_date_input_locator, tomorrow_str)
        # Blur the input field to ensure value is registered and date picker closes if open
        await page.press(end_date_input_locator, 'Enter') 
        
        print(f"Selected Start Date: {tomorrow_str}, End Date: {tomorrow_str}.")

        # Step 6: Leave the 'Reason' field blank.
        print("Leaving 'Reason' field blank (not interacting with it).")
        # Ensure the field locator exists but we don't fill it
        reason_field_locator = 'textarea[placeholder="Enter Reason"]' # Assuming a textarea with this placeholder
        await expect(page.locator(reason_field_locator)).to_be_visible() # Just to confirm its presence

        # Step 7: Click the 'Submit' button.
        print("Clicking the 'Submit' button...")
        # Locator for the Submit button on the leave application form
        await page.click('button:has-text("Submit")')

        # --- Assertion ---
        # Expected Result: An error message is displayed, clearly indicating that the 'Reason' field is mandatory.
        # The leave application is not submitted, and the form remains open or redirects back with the error.
        print("Verifying error message for mandatory 'Reason' field and form status...")
        
        # Assert that a validation error message related to the 'Reason' field is displayed.
        # This locator uses a regex to catch common error messages like "Reason is required", "Reason cannot be empty", etc.
        # It expects the text to be visible somewhere on the page, preferably near the Reason field.
        await expect(page.locator('text=/Reason is required|Reason cannot be empty|This field is mandatory/i')).to_be_visible(timeout=10000)
        
        # Additionally, assert that the 'Apply Leave' form title or a key form element is still visible,
        # indicating that the form was NOT successfully submitted.
        await expect(page.locator('text="Apply Leave"')).to_be_visible() 
        
        print("Assertion passed: Mandatory 'Reason' field error message displayed and 'Apply Leave' form remains open.")

        print("\n--- Test Case TC-002 Completed Successfully ---")

        # Close the browser
        await browser.close()

if __name__ == '__main__':
    # Run the main asynchronous test function
    asyncio.run(main())