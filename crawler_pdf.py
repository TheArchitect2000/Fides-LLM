
def change_pdf_doc(doc):
    doc.metadata['type']='PDF'
    return doc

def crawler_pdf():
    from langchain_community.document_loaders import PyPDFLoader
    print("PDF Crawler started ....")

    pdf_docs = []
    pdf_files = [
        "PDF/zkIoT.pdf",
        "PDF/Consensus Algorithms.pdf",
        "PDF/Data Monetization.pdf",
        "pdf/Decentralized Delegated Proof.pdf",
        "pdf/Digital Twins.pdf",
        "pdf/Fides service contracts.pdf",
        "pdf/fides_innova_gitbook_placeholder.pdf",
        "pdf/IoT Startups.pdf",
        "pdf/MIoTN.pdf",
        "pdf/MQTT and MQTTS protocols.pdf",
        "pdf/Service Contract.pdf",
        "pdf/Service Market.pdf",
        "pdf/What’s Web 3.0.pdf"
    ]

    for path in pdf_files:
        try:
            loader = PyPDFLoader(path)
            pdf_docs.extend(loader.load())
#            print(len(pdf_docs))
        except Exception as e:
            print(f"Error loading PDF {path}: {e}")

    pdf_docs = list(map(change_pdf_doc, pdf_docs))

    print("Loaded all PDF files:", len(pdf_files))
    print("Created docs:", len(pdf_docs))
    return pdf_docs

