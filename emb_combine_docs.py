def combine_docs(web_docs, github_docs, youtube_docs, pdf_docs, pptx_docs):
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    print("Splitter started ....")

    splitter = RecursiveCharacterTextSplitter(chunk_size = 500, chunk_overlap = 100)
    print("Splitting web_docs ...")
    split_web_docs = splitter.split_documents(web_docs or [])
    print("Splitting github_docs ...")
    split_github_docs = splitter.split_documents(github_docs or [])
    print("Splitting youtube_docs ...")
    split_youtube_docs = splitter.split_documents(youtube_docs or [])
    print("Splitting pdf_docs ...")
    split_pdf_docs = splitter.split_documents(pdf_docs or [])
    print("Splitting pptx_docs ...")
    split_pptx_docs = splitter.split_documents(pptx_docs or [])


    # --- Step 8: Store in Vector DB ---
    # Combine all split documents
    all_split_docs = (
        split_youtube_docs +
        split_pdf_docs +
        split_pptx_docs +
        split_web_docs +
        split_github_docs
    )
    print("Splitting done.", len(all_split_docs), " documents created.")
    return all_split_docs

