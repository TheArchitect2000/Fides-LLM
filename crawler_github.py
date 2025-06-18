
def change_GitHub_to_meta_data(doc):
    """
    Change the metadata of the web documents to include the content type.
    """
    doc.metadata["type"] = "GitHub"
    # remove \n from the content
    doc.page_content = doc.page_content.replace("\n", " ")
    # remove multiple spaces
    doc.page_content = ' '.join(doc.page_content.split())
    return doc

def crawler_github():
    from langchain_community.document_loaders import GitLoader

    # loading GitHub Repos
    github_repos = [
        "https://github.com/TheArchitect2000/Fides-Innova-WiKi",
        "https://github.com/TheArchitect2000/Blockchain-based-IoT-Server",
        "https://github.com/TheArchitect2000/zk-IoT",
        "https://github.com/TheArchitect2000/Smart-Contract-Protocol",

    #    "https://github.com/TheArchitect2000/zkiot-riscv-qemu-c", 
    #    "https://github.com/TheArchitect2000/ZKP-Blockchain-Explorer",
       "https://github.com/TheArchitect2000/evm-server",
    #    "https://github.com/TheArchitect2000/New-IoT-Device-Integration",
    #   "https://github.com/TheArchitect2000/zkiot-riscv-qemu-rust"
    ]
    
    github_docs = []
    for url in github_repos:
        print(f"📥 Loading repository: {url}")
        repo_name = url.split("/")[-1]
        local_path = f"./cloned_repos/{repo_name}"

        loader = GitLoader(
            repo_path=local_path,
            clone_url=url,
            branch="main",
            file_filter=lambda f: f.endswith((
                # ".py", ".md", ".c", ".cpp", ".rs", ".json", ".html",
                # ".js", ".ts", ".css", ".java", ".txt", ".yml", ".yaml", ".sh"
                ".md"
            ))
        )
        
        temp_docs = loader.load()
        temp_docs = list(map(change_GitHub_to_meta_data, temp_docs))
        github_docs.extend(temp_docs)
        
        print(f"✅ Loaded {len(github_docs)} documents from {repo_name}")

    print("GitHub Crawler started ....")

    print(f"Total GitHub documents loaded: {len(github_docs)}")
    return github_docs


