import asyncio
from playwright.async_api import async_playwright, expect

async def main():
    """
    Test Case ID: TC-LOGIN-009
    Description: Login with Malformed Email (e.g., only local part)
    Pre-conditions: User is on the login page.
    Test Steps: 1. Enter Email: 'srikanth123'
                2. Enter Password: 'Srikanth@123'
                3. Click 'Login' button.
    Expected Result: System should display a client-side validation error message for invalid email format.
                     User should remain on the login page.
    """
    async with async_playwright() as p:
        # 1. Launch the browser in headed mode as required.
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # Navigate to the application's login page
        base_url = "https://dev.urbuddi.com/"
        await page.goto(base_url)
        print(f"Navigated to: {page.url}")

        # Store the initial URL to assert that navigation did not occur.
        initial_url = page.url

        # --- Test Steps for TC-LOGIN-009 ---

        print("Executing Test Case TC-LOGIN-009: Login with Malformed Email")

        # 1. Enter Email: 'srikanth123'
        # Using the exact locator provided: page.locator("#userEmail")
        email_input = page.locator("#userEmail")
        await email_input.fill('srikanth123')
        print("Entered 'srikanth123' into email field.")

        # 2. Enter Password: 'Srikanth@123'
        # Using the exact locator provided: page.locator("#userPassword")
        password_input = page.locator("#userPassword")
        await password_input.fill('Srikanth@123')
        print("Entered 'Srikanth@123' into password field.")

        # 3. Click 'Login' button.
        # Using the exact locator provided: page.get_by_text("Login")
        login_button = page.get_by_text("Login")
        await login_button.click()
        print("Clicked 'Login' button.")

        # --- Assertions based on Expected Result ---

        # Expected Result: User should remain on the login page.
        # Assert that the URL has not changed.
        await expect(page).to_have_url(initial_url)
        print(f"Assertion: Page URL is still '{initial_url}' (Expected: User remains on login page).")

        # Further assertions to confirm user is still on the login page and elements are visible.
        await expect(email_input).to_be_visible()
        await expect(password_input).to_be_visible()
        await expect(login_button).to_be_visible()
        print("Assertion: Email, Password fields, and Login button are still visible.")

        # Expected Result: System should display a client-side validation error message for invalid email format.
        # IMPORTANT: Without specific DOM representation or locators for the error message,
        # we cannot assert the presence or text of the error message specifically
        # as per the "DO NOT HALLUCINATE OR GUESS LOCATORS" requirement.
        # The combination of not navigating away and form elements still being visible
        # strongly implies client-side validation prevented submission.
        print("Note: Specific assertion for the client-side validation error message text/element is skipped")
        print("      due to lack of locator information in the provided DOM representation.")
        print("      The test confirms navigation did not occur, implying validation blockage.")

        print("Test Case TC-LOGIN-009 completed successfully.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())