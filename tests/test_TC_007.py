import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("https://dev.urbuddi.com/")
        
        # Login using provided credentials
        await page.get_by_label("Email").fill("srikanth123@optimworks.com")
        await page.get_by_label("Password").fill("Srikanth@123")
        await page.get_by_text("Login").click()
        
        # Navigate to Leave Management module
        await page.get_by_text("Leave Management").click()
        
        # Apply Leave with missing mandatory fields
        await page.locator("#fromDate").fill("")
        await page.locator("#toDate").fill("")
        await page.locator("*[name='subject']").fill("")
        await page.locator("*[name='reason']").fill("")
        await page.get_by_text("Apply Leave").click()
        
        # Verify error message for missing mandatory fields
        error_message = await page.query_selector(".error-message")
        assert error_message is not None, "Error message not found"
        await browser.close()

asyncio.run(main())