from search_faiss import search

# ---------------------- Example Usage ----------------------
results = search("what's zkIoT?", k=3)
for i, res in enumerate(results, 1):
    print(f"\nResult {i}")
    print("Metadata:", res.metadata)
    print("Content:", res.page_content)
    