import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://dev.urbuddi.com/")

        # Enter email and password
        await page.locator("#inputEmail").fill("srikanth123@optimworks.com")
        await page.locator("#inputPassword").fill("Srikanth@123")

        # Click on login button
        await page.locator("#btnLogin").click()

        # Wait for login to complete
        await page.wait_for_load_state("networkidle")

        # Navigate to Leave Management module
        await page.get_by_text("Leave Management").click()

        # Apply for leave
        await page.locator("#fromDate").fill("2024-09-16")
        await page.locator("#toDate").fill("2024-09-16")
        await page.locator("*[name='subject']").fill("Leave Application")
        await page.locator("*[name='reason']").fill("Taking a day off for personal reasons")
        await page.locator("#leave").click()

        # Click on Apply Leave button
        await page.get_by_text("Apply Leave").click()

        # Wait for leave application to complete
        await page.wait_for_load_state("networkidle")

        # Assert that leave application was successful
        assert await page.get_by_text("Leave Application Successful").is_visible()

        # Close browser
        await browser.close()

asyncio.run(main())