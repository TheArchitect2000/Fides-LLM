
def load_faiss_components():
    from langchain_community.vectorstores import FAISS
    import numpy as np
    import pickle
    import os

    # ---------------------- Step 1: Load Components ----------------------
    save_dir = "fides_faiss_crawled_data"

    # Load FAISS index
    global faiss_db
    faiss_db = FAISS.load_local(
        folder_path=os.path.join(save_dir, "fides_faiss_pca_256"),
        embeddings=None,
        index_name="index",  # default inside LangChain
        allow_dangerous_deserialization=True
    )

    # Load PCA
    with open(os.path.join(save_dir, "fides_pca_256_model.pkl"), "rb") as f:
        global pca
        pca = pickle.load(f)

    # Load scaler
    with open(os.path.join(save_dir, "fides_scaler.pkl"), "rb") as f:
        global scaler
        scaler = pickle.load(f)

    # Load feature mask
    global stable_mask
    stable_mask = np.load(os.path.join(save_dir, "fides_feature_mask.npy"))
    return

# ---------------------- Step 2: Embed and Preprocess Query ----------------------
def preprocess_query(text: str):
    import numpy as np
    
    # Load environment variables from .env file
    from dotenv import load_dotenv
    import os
    load_dotenv()
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
    print("Environment setup complete.")

    # Load FAISS components
    from langchain_openai import OpenAIEmbeddings
    embedder = OpenAIEmbeddings(model="text-embedding-3-small")
    vector = embedder.embed_query(text)

    # Ensure vector is safe
    if not np.all(np.isfinite(vector)) or np.linalg.norm(vector) <= 1e-6:
        raise ValueError("Invalid or zero vector produced by embedder.")

    # Load PCA and scaler
    from sklearn.preprocessing import StandardScaler
    vector = np.clip(vector, -1000, 1000)
    vector = scaler.transform([vector])
    vector = vector[:, stable_mask]
    vector = pca.transform(vector)

    return vector.astype("float32")

# ---------------------- Step 3: Perform Similarity Search ----------------------
def search(query: str, k=3):
    load_faiss_components()
    query_vector = preprocess_query(query)
    return faiss_db.similarity_search_by_vector(query_vector[0], k=k)

