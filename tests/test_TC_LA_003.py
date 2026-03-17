import asyncio
from playwright.async_api import async_playwright, expect

# Test Case Details
TEST_CASE_ID = "TC-LA-003"
DESCRIPTION = "Verify validation when 'End Date' is before 'Start Date' in leave application."
BASE_URL = "https://dev.urbuddi.com/"
LOGIN_EMAIL = "srikanth123@optimworks.com"
LOGIN_PASSWORD = "Srikanth@123"

async def test_leave_application_end_date_validation():
    """
    Tests the validation on the leave application form when the end date is before the start date.
    """
    print(f"--- Running Test Case: {TEST_CASE_ID} ---")
    print(f"Description: {DESCRIPTION}")
    print(f"Pre-conditions: User '{LOGIN_EMAIL}' logs in and navigates to Leave Management.")

    async with async_playwright() as p:
        # Launch a Chromium browser in headless mode (set headless=False to see the browser UI)
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            # Step 1: Log in to the application
            print("Step 1: Navigating to login page and logging in.")
            await page.goto(BASE_URL)
            # Assert that we are on the login page (assuming the URL changes to /login)
            await expect(page).to_have_url(f"{BASE_URL}login")

            # Login locators are not in the provided HTML snippet or extracted locators map.
            # Using common Playwright locators for input fields with typical IDs and a button by role/name.
            await page.locator("#userEmail").fill(LOGIN_EMAIL)
            await page.locator("#userPassword").fill(LOGIN_PASSWORD)
            await page.get_by_role("button", name="Login").click()

            # Wait for navigation to the dashboard or home page after successful login
            await page.wait_for_url(BASE_URL)
            print("Logged in successfully. Navigated to dashboard.")

            # Step 2: Navigate to the 'Leave Management' section.
            print("Step 2: Navigating to 'Leave Management' section.")
            # Recommended Locator: page.get_by_text("Leave Management")
            await page.get_by_text("Leave Management").click()

            # Wait for the URL to change to the Leave Management page
            await page.wait_for_url(f"{BASE_URL}leave_management")
            # Verify the page header text to confirm navigation
            await expect(page.locator(".sc-feUZmu.qNlEl")).to_have_text("Leave Management")
            print("Navigated to 'Leave Management' page.")

            # Step 3: Click the 'Apply Leave' button.
            print("Step 3: Clicking 'Apply Leave' button.")
            # Recommended Locator: page.get_by_text("Apply Leave")
            await page.get_by_text("Apply Leave").click()

            # The 'Apply Leave' form HTML is not provided in the snippet.
            # Assuming it opens a modal or navigates to a new page, and typically has a title.
            # Waiting for a common form element (e.g., a header with text "Apply For Leave") to appear.
            await page.wait_for_selector('text="Apply For Leave"', state='visible')
            print("The 'Apply Leave' form is accessible.")

            # Step 4: In the 'Apply Leave' form, fill details.
            print("Step 4: Filling the 'Apply Leave' form with an invalid End Date.")

            # Locators for form fields are not in the provided HTML or extracted map.
            # Using Playwright's `get_by_label` for robustness, assuming standard labels.

            # a. Select a 'Leave Type' (e.g., 'Annual Leave').
            await page.get_by_label("Leave Type").select_option("Annual Leave")
            print("Selected Leave Type: 'Annual Leave'.")

            # b. Select 'Start Date' as March 25, 2026.
            # Filling the input field directly. Assuming format YYYY-MM-DD for Playwright fill.
            await page.get_by_label("Start Date").fill("2026-03-25")
            print("Set Start Date: March 25, 2026.")

            # c. Select 'End Date' as March 23, 2026 (an earlier date than Start Date).
            await page.get_by_label("End Date").fill("2026-03-23")
            print("Set End Date: March 23, 2026 (earlier than Start Date).")

            # d. Enter a 'Reason' (e.g., 'Urgent personal work').
            await page.get_by_label("Reason").fill("Urgent personal work")
            print("Entered Reason: 'Urgent personal work'.")

            # Step 5: Click the 'Submit' button on the form.
            print("Step 5: Clicking the 'Submit' button.")
            # The submit button for the form is not in the provided HTML or extracted locators map.
            # Using common Playwright locator for a button with text 'Submit'.
            await page.get_by_role("button", name="Submit").click()

            # Step 6: Verify expected result.
            print("Step 6: Verifying validation error message and form state.")

            # Expected Result: An error message indicating that 'End Date cannot be before Start Date'
            # or similar date validation error is displayed.
            error_message_text = "End Date cannot be before Start Date"
            error_message_locator = page.get_by_text(error_message_text)
            await expect(error_message_locator).to_be_visible()
            print(f"Validation Error Message: '{error_message_text}' is displayed.")

            # Verify the leave application is not submitted, and the form remains open.
            # We can check if the 'Submit' button is still visible, implying the form did not close/submit.
            await expect(page.get_by_role("button", name="Submit")).to_be_visible()
            print("The 'Apply Leave' form remains open (application not submitted).")

            print(f"--- Test Case {TEST_CASE_ID} Passed ---")
            
        except Exception as e:
            # Catch any exceptions during the test, print error, take screenshot, and re-raise.
            print(f"--- Test Case {TEST_CASE_ID} Failed ---")
            print(f"Error during test execution: {e}")
            await page.screenshot(path=f"{TEST_CASE_ID}_failure_screenshot.png")
            raise # Re-raise the exception to indicate a test failure to the runner
        finally:
            # Close the browser after the test completes or fails.
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_leave_application_end_date_validation())