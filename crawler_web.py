
def crawl_internal_links(start_url, max_pages=10, max_depth=1):
    from selenium.webdriver.chrome.options import Options
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from urllib.parse import urlparse, urljoin
    from selenium.common.exceptions import WebDriverException, TimeoutException
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    from selenium.common.exceptions import StaleElementReferenceException
    import time

    """
    Crawl internal URLs from a site using Selenium, with support for JavaScript-heavy pages.

    Args:
        start_url (str): The URL to start crawling from.
        max_pages (int): Max number of pages to crawl.
        max_depth (int): Max depth to crawl (0 = just root).

    Returns:
        list: A list of internal URLs that were successfully visited.
    """
    # Selenium Headless Browser Setup
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    visited = set()
    domain = urlparse(start_url).netloc
    to_visit = [(start_url, 0)]

    while to_visit and len(visited) < max_pages:
        url, depth = to_visit.pop(0)
        if url in visited or depth > max_depth:
            continue
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "a")))
            time.sleep(1)  # 🔁 Wait for JS to load

            print(f"Visited ({len(visited)+1}/{max_pages}), Depth {depth}): {url}")
            visited.add(url)

            # If max depth reached, skip link extraction
            if depth == max_depth:
                continue

            # Extract and queue internal links
            links = driver.find_elements(By.TAG_NAME, "a")
            for link in links:
                try:
                    href = link.get_attribute("href")
                    if not href or href.startswith(("mailto:", "tel:", "javascript:")):
                        continue

                    parsed = urlparse(href)
                    if parsed.netloc == domain or parsed.netloc == "":
                        full_url = urljoin(url, href).split("#")[0]
                        if full_url not in visited and all(full_url != q[0] for q in to_visit):
                            to_visit.append((full_url, depth + 1))
                except StaleElementReferenceException:
                    continue

        except (WebDriverException, TimeoutException):
            print(f"⚠️ Skipping (Error): {url}")
            visited.add(url)
            continue

    driver.quit()

    # Print summary
    print(f"\n Total unique internal URLs visited: {len(visited)}")

    if len(visited) < max_pages:
        print("⚠️ Number of crawled URLs is less than max_pages. Possible reasons:")
        print("- Site may not have enough unique pages within the allowed depth.")
        print("- Some links might be hidden behind JavaScript interactions.")
        print("- Some links could be blocked, inaccessible, or slow-loading.")
        print("- Your max_depth may be too shallow to discover deeper links, try changing depth.")
    
    return list(visited)

def change_web_to_meta_data(doc):
    """
    Change the metadata of the web documents to include the content type.
    """
    doc.metadata["type"] = "Web"
    # remove \n from the content
    doc.page_content = doc.page_content.replace("\n", " ")
    # remove multiple spaces
    doc.page_content = ' '.join(doc.page_content.split())
    return doc

def crawler_web(max_pages=3):
    from langchain_community.document_loaders import WebBaseLoader
    print("Web Crawler started ....")

    #### CONFIGURABLE SETTINGS 
    start_url = "https://fidesinnova.io/"
    max_depth = 3     # 0 = only root, 1 = root + links from root

    ####  Run the Crawler
    web_docs_list1 = crawl_internal_links(start_url, max_pages, max_depth)

    #  Load the web documents
    web_docs = []

    for idx in web_docs_list1:
        a = WebBaseLoader(idx)
        print(f"Loading {idx} ...")
        try:
            temp_docs = a.load()
            temp_docs = list(map(change_web_to_meta_data, temp_docs))

            web_docs.extend(temp_docs)
            print(idx + " is loaded.")
        except Exception as e:
            print(f"{idx} is not loaded. Error: {e}")

    print(f"Total web documents loaded: {len(web_docs)}")
    return web_docs


