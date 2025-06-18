
# Add metadata
def change_pptx_doc(doc):
    doc.metadata['type'] = 'PPTX'
    return doc

def crawler_pptx():
    from langchain_community.document_loaders import UnstructuredPowerPointLoader 
    print("PPTX Crawler started ....")

    pptx_docs = []
    pptx_files = [
        "PPTX/FidesinnovaDeck-v11.pptx"
    ]

    for path in pptx_files:
        print(f"Loading PPTX file: {path}")
        try:
            loader = UnstructuredPowerPointLoader(path)
            pptx_docs.extend(loader.load())
        except Exception as e:
            print(f"❌ Error loading PPTX {path}: {e}")

    pptx_docs = list(map(change_pptx_doc, pptx_docs))

    print("Loaded PPTX files:", len(pptx_files))
    print("Created docs:", len(pptx_docs))
    return pptx_docs


