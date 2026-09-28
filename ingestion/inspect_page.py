import requests
from bs4 import BeautifulSoup


url = "https://learn.microsoft.com/en-us/windows-server/networking/dns/troubleshoot/troubleshoot-dns-data-collection"


response = requests.get(url)

print("Status code:", response.status_code)


soup = BeautifulSoup(response.text, "html.parser")


main = soup.find("main", id="main")

if not main:
    print("Could not find main")
    exit()


container = main.find(
    "div",
    class_="reading-width"
)

if not container:
    print("Could not find reading-width")
    exit()


outer_content = container.find_all(recursive=False)[0]


content_divs = outer_content.find_all(
    "div",
    class_="content",
    recursive=False
)


print("\nNUMBER OF CONTENT DIVS:", len(content_divs))


for i, div in enumerate(content_divs):

    print("\n" + "=" * 80)
    print("CONTENT DIV:", i)
    print("=" * 80)

    print("ID:", div.get("id"))
    print("Classes:", div.get("class"))

    text = div.get_text(" ", strip=True)

    print("Length:", len(text))

    print("\nTEXT:\n")
    print(text[:2000])