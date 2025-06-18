from crawler_github import crawler_github
from crawler_pdf import crawler_pdf
from crawler_pptx import crawler_pptx
from crawler_web import crawler_web
from crawler_youtube import crawler_youtube
from emb_combine_docs import combine_docs
from emb_create_faiss import create_faiss

print("Starting crawlers and creating FAISS ...")

github_docs = crawler_github()
pdf_docs = crawler_pdf()
pptx_docs = crawler_pptx()
web_docs = crawler_web(100)
youtube_docs = crawler_youtube(100)

create_faiss(combine_docs(web_docs, github_docs, youtube_docs, pdf_docs, pptx_docs))
