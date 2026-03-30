import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        # Launch the browser in headed mode
        browser = await p.chromium.launch(headless=False)
        # Create a new browser context
        context = await browser.new_context()
        # Create a new page
        page = await context.new_page()
        # Navigate to the login page
        await page.goto("https://dev.urbuddi.com/")
        
        # Login using the provided credentials
        await page.get_by_label("Email").fill("srikanth123@optimworks.com")
        await page.get_by_label("Password").fill("Srikanth@123")
        await page.get_by_text("Login").click()
        
        # Navigate to the leave management module
        await page.get_by_text("Leave Management").click()
        
        # Apply for leave with insufficient balance
        await page.get_by_text("Apply Leave").click()
        await page.locator("#fromDate").fill("2024-09-16")
        await page.locator("#toDate").fill("2024-09-16")
        await page.locator("*[name='subject']").fill("Leave Application")
        await page.locator("*[name='reason']").fill("Taking a day off for personal reasons")
        await page.locator("#leave").click()
        await page.get_by_text("Submit").click()
        
        # Assert that the system handles leave application with insufficient balance correctly
        await page.wait_for_timeout(2000)
        assert await page.get_by_text("Insufficient balance").is_visible()

        # Close the browser
        await browser.close()

asyncio.run(main())