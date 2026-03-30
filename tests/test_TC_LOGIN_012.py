import asyncio
from playwright.async_api import async_playwright, expect

async def main():
    async with async_playwright() as p:
        # 1. Launch browser in headed mode as required
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # Define URLs and credentials
        base_url = "https://dev.urbuddi.com"
        login_url = f"{base_url}/login"
        
        # Login Credentials to use in the script
        correct_email = "srikanth123@optimworks.com"
        correct_password = "Srikanth@123"

        # Long password for the specific test case TC-LOGIN-012
        long_password = "ThisIsAVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryLongPassword123"

        # --- Automatically perform login as a prerequisite for the overall feature ---
        print("--- Initiating prerequisite login for 'Login with srikanth123@optimworks.com and Srikanth@123, then open Leave Application' ---")
        print("STEP: Navigating to the login page...")
        await page.goto(login_url)
        await page.wait_for_load_state('networkidle') # Wait for the page to be fully loaded

        print(f"STEP: Entering Email: '{correct_email}'")
        # Use exact locator: page.locator("#userEmail")
        await page.locator("#userEmail").fill(correct_email)

        print(f"STEP: Entering Password: '{correct_password}'")
        # Use exact locator: page.locator("#userPassword")
        await page.locator("#userPassword").fill(correct_password)

        print("STEP: Clicking 'Login' button.")
        # Use exact locator: page.get_by_text("Login")
        await page.get_by_text("Login").click()

        # 4. Add appropriate assertions for successful initial login
        # We expect to navigate away from the login page to a dashboard or home page.
        try:
            # Wait for the URL to change from the login page, indicating successful navigation.
            await page.wait_for_url(lambda url: url != login_url, timeout=15000)
            print("ASSERT: Successfully logged in and navigated away from the login page (initial setup).")
            # Explicitly assert that the current URL is not the login URL.
            expect(page.url).not_to_equal(login_url) 
            print(f"INFO: Current URL after initial login: {page.url}")
            
            # The "then open Leave Application" part implies successful access to the application.
            # Without specific post-login DOM for "Leave Application", we assert successful login by URL change.

        except Exception as e:
            print(f"ERROR: Prerequisite login failed or navigation did not occur as expected: {e}")
            await page.screenshot(path="initial_login_failure.png")
            raise

        # --- Test Case ID: TC-LOGIN-012: Login with very long Password (boundary condition) ---
        print(f"\n--- Executing Test Case ID: TC-LOGIN-012 ---")
        print("DESCRIPTION: Login with very long Password (boundary condition)")

        # Pre-conditions: User is on the login page.
        # To meet this, we navigate back to the login page after the initial successful login.
        print("PRE-CONDITION: Navigating back to the login page for TC-LOGIN-012 execution.")
        await page.goto(login_url)
        await page.wait_for_load_state('networkidle')

        # Test Steps:
        # Step 1: Enter Email: 'srikanth123@optimworks.com'
        print(f"TEST STEP 1: Entering Email: '{correct_email}'")
        # Use exact locator: page.locator("#userEmail")
        await page.locator("#userEmail").fill(correct_email)

        # Step 2: Enter Password: 'ThisIsAVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryVeryLongPassword123'
        print(f"TEST STEP 2: Entering Password (very long - length: {len(long_password)}): '{long_password}'")
        # Use exact locator: page.locator("#userPassword")
        await page.locator("#userPassword").fill(long_password)

        # Step 3: Click 'Login' button.
        print("TEST STEP 3: Clicking 'Login' button.")
        # Use exact locator: page.get_by_text("Login")
        await page.get_by_text("Login").click()

        # 4. Add appropriate assertions for the expected result
        # Expected Result: If the system has a length limit, an error message indicating the password is too long should be displayed,
        # or the field should truncate input. If within limits, it should be treated as an invalid password.
        # In all these scenarios, a successful login with this very long password is NOT expected.
        # Therefore, we assert that the user remains on the login page, indicating login failure.
        
        # Give some time for the server to respond and any client-side validation/redirects to occur.
        await page.wait_for_timeout(2000) 

        print("ASSERT: Verifying login with very long password failed (user remains on login page).")
        # Assert that the current URL is still the login page URL.
        # This confirms that login with the very long password was unsuccessful.
        expect(page).to_have_url(login_url)
        print("ASSERT: User remains on the login page, confirming login failure with very long password.")
        
        # Additionally, verify the login button is still visible, which further confirms being on the login page.
        await expect(page.get_by_text("Login")).to_be_visible()
        print("ASSERT: 'Login' button is still visible on the page, reinforcing login failure.")

        print(f"--- Test Case TC-LOGIN-012 PASSED ---")

        # Keep the browser open for a few seconds to observe the final state
        await page.wait_for_timeout(3000) 
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())