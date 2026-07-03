"""
Turn the raw, messy HTML filings into clean plain text.

What this does:
- Reads each raw .html 10-K file you downloaded
- Strips out all the HTML tags, scripts, and formatting junk
- Saves a clean .txt version next to it
"""

from bs4 import BeautifulSoup

from config import FILINGS_DIR


def clean_html_file(html_path) -> str:
    """Strip HTML down to plain readable text."""
    raw = html_path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(raw, "lxml")

    # Remove elements that aren't real report content
    for tag in soup(["script", "style", "table"]):
        tag.decompose()

    text = soup.get_text(separator=" ")

    # Collapse excess whitespace left behind by the tag removal
    text = " ".join(text.split())
    return text


def main():
    company_folders = [f for f in FILINGS_DIR.iterdir() if f.is_dir()]
    print(f"Cleaning filings for {len(company_folders)} companies...")

    for i, folder in enumerate(company_folders, start=1):
        html_files = list(folder.glob("*.html"))
        cleaned_count = 0

        for html_path in html_files:
            txt_path = html_path.with_suffix(".txt")
            if txt_path.exists():
                continue  # already cleaned

            try:
                clean_text = clean_html_file(html_path)
                txt_path.write_text(clean_text, encoding="utf-8")
                cleaned_count += 1
            except Exception as e:
                print(f"  FAILED on {html_path.name}: {e}")

        print(f"[{i}/{len(company_folders)}] {folder.name}: {cleaned_count} files cleaned")

    print("\nDone.")


if __name__ == "__main__":
    main()
