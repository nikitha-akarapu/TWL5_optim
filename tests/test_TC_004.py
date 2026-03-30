import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("https://dev.urbuddi.com/")

        # Login to the application
        await page.locator("#login-email").fill("srikanth123@optimworks.com")
        await page.locator("#login-password").fill("Srikanth@123")
        await page.locator("#login-button").click()

        # Navigate to Leave Management module
        await page.wait_for_timeout(2000)
        await page.get_by_text("Leave Management").click()

        # Apply for leave
        await page.wait_for_timeout(2000)
        await page.locator("*[name='fromDate']").fill("2024-09-16")
        await page.locator("*[name='toDate']").fill("2024-09-16")
        await page.locator("*[name='subject']").fill("Leave Application")
        await page.locator("*[name='reason']").fill("Taking a day off for personal reasons")
        await page.locator("#leave").click()

        # Submit the leave application
        await page.get_by_text("Submit").click()

        # Verify if the leave application is submitted successfully
        await page.wait_for_timeout(2000)
        assert await page.get_by_text("Leave Application").is_visible()

        # Verify the test steps are completed successfully
        assert await page.get_by_text("Leave Management").is_visible()
        assert await page.get_by_text("Apply Leave").is_visible()

        # Close the browser
        await browser.close()

asyncio.run(main())