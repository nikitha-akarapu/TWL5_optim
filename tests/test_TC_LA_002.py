import asyncio
import os
from playwright.async_api import async_playwright, expect

# Test Case ID: TC-LA-002
# Description: Verify validation for missing mandatory 'Reason' field in leave application.
# Status: Initializing... will be updated after execution.

# --- Configuration ---
BASE_URL = "https://dev.urbuddi.com/"
LOGIN_EMAIL = "srikanth123@optimworks.com"
LOGIN_PASSWORD = "Srikanth@123"

async def test_leave_reason_validation():
    print(f"--- Running Test Case: TC-LA-002 ---")
    print(f"Description: Verify validation for missing mandatory 'Reason' field in leave application.")
    
    test_status = "FAILED" # Default status before execution

    async with async_playwright() as p:
        # Launch browser in headless mode by default. Set headless=False to observe the execution.
        browser = await p.chromium.launch(headless=True) 
        page = await browser.new_page()

        try:
            # Step 1: Log in to the application using provided credentials.
            print("Step 1: Navigating to login page and logging in...")
            await page.goto(BASE_URL)
            await page.wait_for_load_state('networkidle')

            # --- Login Page Locators ---
            # The 'Extracted Available Exact Locators' map did not contain locators for the login page.
            # We are assuming common locators for email, password inputs, and a login button.
            # Input fields are typically identified by type or placeholder, buttons by text or type="submit".
            await page.fill('input[type="email"]', LOGIN_EMAIL)
            await page.fill('input[type="password"]', LOGIN_PASSWORD)
            
            # Assuming a login button with the text "Login".
            await page.click('button:has-text("Login")') 
            
            # Wait for navigation to the dashboard or a known element after successful login.
            # Assuming successful login redirects to '/dashboard'.
            await page.wait_for_url(f"{BASE_URL}dashboard", timeout=10000) 
            print("Successfully logged in.")

            # Step 2: Navigate to the 'Leave Management' section.
            print("Step 2: Navigating to 'Leave Management' section.")
            # Recommended Locator: page.get_by_text("Leave Management")
            await page.get_by_text("Leave Management").click()
            await page.wait_for_url(f"{BASE_URL}leave_management", timeout=5000)
            await page.wait_for_load_state('networkidle')
            print("Navigated to 'Leave Management'.")

            # Step 3: Click the 'Apply Leave' button.
            print("Step 3: Clicking 'Apply Leave' button.")
            # Recommended Locator: page.get_by_text("Apply Leave")
            await page.get_by_text("Apply Leave").click()
            
            # Wait for the "Apply Leave" form/modal to appear.
            # The HTML for the 'Apply Leave' form itself was not provided in the snippet.
            # We'll wait for the presence of a "Submit" button, which is typically part of such a form/modal.
            # Using get_by_role is a robust Playwright locator strategy.
            await page.get_by_role("button", name="Submit").wait_for(state="visible", timeout=5000)
            print("Apply Leave form is accessible.")

            # Step 4: In the 'Apply Leave' form:
            print("Step 4: Filling 'Apply Leave' form (leaving Reason empty).")
            
            # As the 'Apply Leave' form HTML was not provided, we are using robust locators based on labels and roles.
            
            # a. Select a 'Leave Type' (e.g., 'Sick Leave').
            # Assuming a select element with an associated label "Leave Type".
            await page.get_by_label("Leave Type").select_option("Sick Leave")
            print("Selected 'Sick Leave' from Leave Type dropdown.")

            # b. Select 'Start Date' as April 5, 2026.
            # Assuming an input field with an associated label "Start Date".
            # Filling date in 'YYYY-MM-DD' format directly into the input.
            await page.get_by_label("Start Date").fill("2026-04-05")
            print("Selected Start Date: 2026-04-05.")

            # c. Select 'End Date' as April 5, 2026.
            # Assuming an input field with an associated label "End Date".
            # Filling date in 'YYYY-MM-DD' format directly into the input.
            await page.get_by_label("End Date").fill("2026-04-05")
            print("Selected End Date: 2026-04-05.")

            # d. Leave the 'Reason' field empty.
            # Locate the Reason field using its label.
            # Verify it's empty, and if not, clear it, though typically it should be empty initially.
            reason_field = page.get_by_label("Reason")
            await expect(reason_field).to_be_empty() # Assert it's initially empty
            # If the field could potentially be pre-filled: await reason_field.fill("") 
            print("Reason field left empty as required.")

            # Step 5: Click the 'Submit' button on the form.
            print("Step 5: Clicking 'Submit' button on the form.")
            # Assuming the submit button is identified by its role and name within the form context.
            await page.get_by_role("button", name="Submit").click()
            print("Clicked 'Submit'.")

            # Expected Result: An error message indicating that the 'Reason' field is mandatory
            # (e.g., 'Reason is required', 'Please provide a reason for leave') is displayed.
            # The leave application is not submitted, and the form remains open.
            
            # Locate the error message, checking for both possible texts as specified in the test case.
            error_message_locator = page.locator("text=Reason is required").or_(
                                    page.locator("text=Please provide a reason for leave"))
            
            await expect(error_message_locator).to_be_visible(timeout=5000)
            error_text = await error_message_locator.text_content()
            print(f"Validation error message found: '{error_text}'")

            # Verify the form remains open by checking if the Submit button is still visible.
            await expect(page.get_by_role("button", name="Submit")).to_be_visible()
            print("Verified: Apply Leave form remains open after validation error.")

            test_status = "PASSED"
            print(f"--- Test Case TC-LA-002: {test_status} ---")

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            test_status = "FAILED"
            print(f"--- Test Case TC-LA-002: {test_status} ---")
            # Take a screenshot on failure for debugging purposes
            screenshot_path = f"TC-LA-002_failure.png"
            await page.screenshot(path=screenshot_path)
            print(f"Screenshot taken: {screenshot_path}")
        finally:
            # Ensure the browser is closed even if an error occurs
            await browser.close()
    
    return test_status

if __name__ == "__main__":
    # To ensure Playwright browsers are installed, uncomment the line below.
    # os.system("playwright install") 
    
    final_status = asyncio.run(test_leave_reason_validation())
    print(f"\nFinal Test Status for TC-LA-002: {final_status}")