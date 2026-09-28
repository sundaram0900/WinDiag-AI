import requests

from bs4 import BeautifulSoup

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


sources = {
    "performance": [
        "https://support.microsoft.com/en-us/windows/experience/performance-optimization/tips-to-improve-pc-performance-in-windows",
    ],

    "networking": [
        "https://support.microsoft.com/en-us/windows/experience/connectivity-networking/fix-wi-fi-connection-issues-in-windows",
        "https://learn.microsoft.com/en-us/windows-server/networking/dns/troubleshoot/troubleshoot-dns-data-collection",
    ],

    "storage": [
        "https://support.microsoft.com/en-us/windows/experience/storage-filemanagement/manage-drive-space-with-storage-sense",
    ],

    "drivers": [
        "https://learn.microsoft.com/en-us/windows-hardware/drivers/install/troubleshooting-device-and-driver-installations",
        "https://learn.microsoft.com/en-us/windows-hardware/drivers/install/using-device-manager",
    ],

    "windows_update": [
        "https://learn.microsoft.com/en-us/troubleshoot/windows-client/installing-updates-features-roles/troubleshoot-windows-update-issues",
        "https://learn.microsoft.com/en-us/troubleshoot/windows-client/installing-updates-features-roles/common-windows-update-errors",
    ],

    "system_errors": [
        "https://support.microsoft.com/en-us/windows/experience/backup-recovery/use-the-system-file-checker-tool-to-repair-missing-or-corrupted-system-files",
        "https://support.microsoft.com/en-US/Windows/Experience/Startup-Boot/startup-repair",
    ],

    "troubleshooting": [
        "https://support.microsoft.com/en-us/windows/experience/startup-boot/windows-startup-settings",
    ],
}


documents = []


# ============================================================
# DOCUMENT EXTRACTION
# ============================================================

for category, urls in sources.items():

    for url in urls:

        print("\n" + "=" * 80)
        print("LOADING:")
        print(url)
        print("=" * 80)

        response = requests.get(url)

        print("Status code:", response.status_code)

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")


        # ----------------------------------------------------
        # MICROSOFT SUPPORT
        # ----------------------------------------------------

        if "support.microsoft.com" in url:

            article = soup.find(
                "div",
                class_="learnArticleContent"
            )


        # ----------------------------------------------------
        # MICROSOFT LEARN
        # ----------------------------------------------------

        elif "learn.microsoft.com" in url:

            main = soup.find(
                "main",
                id="main"
            )

            if not main:
                raise ValueError(
                    f"Could not find <main id='main'> for {url}"
                )

            reading_width = main.find(
                "div",
                class_="reading-width"
            )

            if not reading_width:
                raise ValueError(
                    f"Could not find reading-width container for {url}"
                )

            outer_content = reading_width.find_all(
                recursive=False
            )[0]

            content_divs = outer_content.find_all(
                "div",
                class_="content",
                recursive=False
            )

            if len(content_divs) < 2:
                raise ValueError(
                    f"Could not find article body for {url}"
                )

            article = content_divs[1]


        # ----------------------------------------------------
        # UNKNOWN DOMAIN
        # ----------------------------------------------------

        else:

            raise ValueError(
                f"Unknown website domain: {url}"
            )


        # ----------------------------------------------------
        # CHECK EXTRACTION
        # ----------------------------------------------------

        if not article:

            raise ValueError(
                f"Could not extract article content from {url}"
            )


        text = article.get_text(
            separator="\n",
            strip=True
        )


        # ----------------------------------------------------
        # CREATE LANGCHAIN DOCUMENT
        # ----------------------------------------------------

        document = Document(
            page_content=text,
            metadata={
                "source": url,
                "category": category
            }
        )

        documents.append(document)


# ============================================================
# DOCUMENT INSPECTION
# ============================================================

print("\n\n")
print("=" * 80)
print("DOCUMENT EXTRACTION RESULT")
print("=" * 80)

print("Total documents:", len(documents))


for i, doc in enumerate(documents):

    print("\n" + "-" * 80)

    print("DOCUMENT:", i)

    print("Category:", doc.metadata.get("category"))

    print("Source:", doc.metadata.get("source"))

    print("Length:", len(doc.page_content))

    print("\nFirst 1000 characters:")

    print(doc.page_content[:1000])


# ============================================================
# TEXT SPLITTING
# ============================================================

print("\n\n")
print("=" * 80)
print("TEXT SPLITTING")
print("=" * 80)


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)


chunks = text_splitter.split_documents(documents)


print("Total chunks:", len(chunks))


# ============================================================
# CHUNK QUALITY CHECK
# ============================================================

print("\n\n")
print("=" * 80)
print("CHUNK QUALITY CHECK")
print("=" * 80)


suspicious_phrases = [
    "Was this page helpful?",
    "Ask Learn",
    "Reading mode",
    "Copy Markdown",
    "Exit editor mode",
    "Table of contents",
]


suspicious_chunks = 0


for i, chunk in enumerate(chunks):

    content = chunk.page_content

    found_phrases = [
        phrase
        for phrase in suspicious_phrases
        if phrase in content
    ]

    if found_phrases:

        suspicious_chunks += 1

        print("\nSuspicious chunk:", i)

        print("Category:", chunk.metadata.get("category"))

        print("Source:", chunk.metadata.get("source"))

        print("Found:", found_phrases)

        print("\nContent:")

        print(content[:1000])


print("\nTotal suspicious chunks:", suspicious_chunks)


# ============================================================
# EMBEDDINGS
# ============================================================

print("\n\n")
print("=" * 80)
print("BUILDING EMBEDDINGS")
print("=" * 80)


embeddings = HuggingFaceEmbeddings(
    model_name="Qwen/Qwen3-Embedding-0.6B"
)


# ============================================================
# CHROMA
# ============================================================

vector_store = Chroma(
    collection_name="winddiag_knowledge",
    embedding_function=embeddings,
    persist_directory="../vector_store"
)




vector_store.add_documents(chunks)

print(f"Added {len(chunks)} chunks to Chroma.")