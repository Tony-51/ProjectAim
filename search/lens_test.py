from pathlib import Path
from playwright.sync_api import sync_playwright


IMAGE_PATH = (
    r"C:\Users\tejas\OneDrive\Desktop"
    r"\face-blockchain-verifier"
    r"\data\test.jpg"
)


with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    page = browser.new_page(
        viewport={
            "width": 1400,
            "height": 900
        }
    )

    print("Opening Google...")

    page.goto(
        "https://www.google.com/?olud",
        wait_until="domcontentloaded"
    )

    page.wait_for_timeout(3000)

    file_input = page.locator(
        'input[type="file"]'
    ).first

    print("Uploading image...")

    file_input.set_input_files(
        IMAGE_PATH
    )

    print("Image uploaded.")

    # Give Lens plenty of time
    page.wait_for_timeout(12000)

    print("\nCollecting page information...")

    # Save complete HTML
    html = page.content()

    Path("data/lens_page.html").write_text(
        html,
        encoding="utf-8"
    )

    print(
        "HTML saved to data/lens_page.html"
    )

    # Extract ALL anchors
    anchors = page.locator("a").all()

    print(
        f"\nTotal <a> elements: {len(anchors)}"
    )

    print("\n" + "=" * 80)
    print("ALL LINKS")
    print("=" * 80)

    for i, anchor in enumerate(anchors[:100], 1):

        try:

            href = anchor.get_attribute("href")
            text = anchor.inner_text().strip()

            print(f"\n[{i}]")
            print("TEXT:", repr(text[:300]))
            print("HREF:", repr(href))

        except Exception:
            pass


    # Extract images
    images = page.locator("img").all()

    print("\n" + "=" * 80)
    print("IMAGES")
    print("=" * 80)

    print(
        f"Total <img> elements: {len(images)}"
    )

    for i, img in enumerate(images[:50], 1):

        try:

            src = img.get_attribute("src")
            alt = img.get_attribute("alt")

            print(f"\n[{i}]")
            print("ALT:", repr(alt))
            print("SRC:", repr(src)[:500])

        except Exception:
            pass


    # Extract visible page text
    text = page.locator("body").inner_text()

    Path("data/lens_text.txt").write_text(
        text,
        encoding="utf-8"
    )

    print(
        "\nVisible text saved to "
        "data/lens_text.txt"
    )

    print("\n" + "=" * 80)
    print("VISIBLE TEXT PREVIEW")
    print("=" * 80)

    print(text[:5000])

    page.screenshot(
        path="data/lens_debug_results.png",
        full_page=True
    )

    print(
        "\nScreenshot saved to "
        "data/lens_debug_results.png"
    )

    input(
        "\nPress ENTER to close..."
    )

    browser.close()