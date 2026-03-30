import asyncio
from playwright.async_api import async_playwright, expect

async def test_login_and_navigate_to_leave_application():
    """
    Test Case ID: TC-LOGIN-001
    Description: Verify that a user can successfully log in with valid credentials
                 and navigate to the 'Leave Application' page.
    """
    async with async_playwright() as p:
        # 1. Launch the browser in headed mode
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            # Navigate to the login page
            await page.goto("https://dev.urbuddi.com/")
            print("Navigated to login page.")

            # --- Test Steps ---

            # Step 1: Enter Email
            # Using the exact locator provided: page.locator("#userEmail")
            await page.locator("#userEmail").fill("srikanth123@optimworks.com")
            print("Entered email.")

            # Step 2: Enter Password
            # Using the exact locator provided: page.locator("#userPassword")
            await page.locator("#userPassword").fill("Srikanth@123")
            print("Entered password.")

            # Step 3: Click the 'Login' button
            # Using the exact locator provided: page.get_by_text("Login")
            await page.get_by_text("Login").click()
            print("Clicked login button.")

            # Step 4: Verify successful redirection to the dashboard/home page.
            # Expect the URL to change from the base login URL.
            # Wait for the URL to contain a common dashboard segment, or for a key element to appear.
            # We'll wait for the "Leave Application" link to be visible, which implies dashboard loaded.
            await expect(page).not_to_have_url("https://dev.urbuddi.com/") # Ensure it's not still on the login page
            await expect(page.get_by_text("Leave Application")).to_be_visible()
            print("Verified redirection to dashboard (Leave Application link is visible).")

            # Step 5: Locate and click on the 'Leave Application' link/menu item.
            # Since this element is post-login and not in the initial login form DOM/locators,
            # we use a robust Playwright text-based locator.
            await page.get_by_text("Leave Application").click()
            print("Clicked 'Leave Application' link.")

            # Step 6: Verify that the 'Leave Application' page loads correctly.
            # Expect the URL to indicate the Leave Application page
            # And verify a key text element that confirms the page content.
            await expect(page).to_have_url("https://dev.urbuddi.com/leave-application")
            await expect(page.get_by_text("Apply For Leave")).to_be_visible() # Assuming this text is on the page
            print("Verified 'Leave Application' page loaded correctly.")

            print("\nTest Passed: User successfully logged in and navigated to 'Leave Application' page.")

        except Exception as e:
            print(f"\nTest Failed: {e}")
            # Optionally take a screenshot on failure
            await page.screenshot(path="failure_screenshot.png")
            raise
        finally:
            # Close the browser
            await browser.close()
            print("Browser closed.")

if __name__ == "__main__":
    asyncio.run(test_login_and_navigate_to_leave_application())