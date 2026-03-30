import asyncio
from playwright.async_api import async_playwright, expect

async def main():
    async with async_playwright() as p:
        # Requirement 1: Launch browser in headed mode
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # Navigate to the login page as a precondition
        await page.goto("https://dev.urbuddi.com/")
        print("Navigated to login page.")

        # TC-LOGIN-004: Login with Invalid Email and Invalid Password
        # Requirement 3: The requirement "Automatically perform login using the credentials provided above prior to executing the test steps"
        # is understood to apply to test cases that require a pre-logged-in state.
        # For this specific test case (TC-LOGIN-004), the test IS the login attempt itself, but with invalid credentials.
        # Performing a prior valid login would contradict the test case's purpose and expected outcome
        # (remaining on the login page and seeing an error), especially without a logout mechanism provided.
        # Therefore, we proceed directly with the invalid login attempt.

        # Test Steps:
        # Step 1: Enter Email: 'invalid@example.com'
        # Requirement 6: Use exact locators from the provided list.
        # Element: <input> type='email' (ID: userEmail) -> Options: page.locator("#userEmail")
        await page.locator("#userEmail").fill("invalid@example.com")
        print("Entered invalid email.")

        # Step 2: Enter Password: 'WrongPassword'
        # Requirement 6: Use exact locators from the provided list.
        # Element: <input> type='password' (ID: userPassword) -> Options: page.locator("#userPassword")
        await page.locator("#userPassword").fill("WrongPassword")
        print("Entered invalid password.")

        # Step 3: Click 'Login' button.
        # Requirement 6: Use exact locators from the provided list.
        # Element: <button> type='submit' -> Options: page.get_by_text("Login")
        await page.get_by_text("Login").click()
        print("Clicked login button.")

        # Expected Result:
        # System should display an error message indicating invalid credentials.
        # User should remain on the login page.

        # Requirement 4: Add appropriate assertions.
        # Assertion 1: User should remain on the login page.
        # Verify the URL remains the login page URL.
        await expect(page).to_have_url("https://dev.urbuddi.com/")
        print("Asserted: User remained on the login page (URL check).")

        # Assertion 2: Verify that login form elements are still visible, confirming user is on the login page.
        await expect(page.locator("#userEmail")).to_be_visible()
        await expect(page.locator("#userPassword")).to_be_visible()
        await expect(page.get_by_text("Login")).to_be_visible()
        print("Asserted: Login form elements are still visible.")

        # Note on error message assertion:
        # The 'Form JSON DOM Representation' is empty and 'Extracted Available Exact Locators'
        # does not provide a locator for an error message element.
        # Adhering to the strict instruction "DO NOT HALLUCINATE OR GUESS LOCATORS",
        # we cannot add an explicit assertion for the error message text or its locator.
        # The successful assertion of remaining on the login page implicitly verifies the login failed.

        print("Test TC-LOGIN-004 completed successfully: Invalid login attempt verified.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())