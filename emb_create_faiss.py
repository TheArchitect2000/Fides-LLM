
def create_faiss(all_split_docs):
    from langchain_openai import OpenAIEmbeddings
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    from langchain_community.vectorstores import FAISS
    from langchain_community.docstore.in_memory import InMemoryDocstore
    import numpy as np
    import pickle
    import faiss
    import os

    # ---------------------- Step 1: Embed All ----------------------
    base_embedder = OpenAIEmbeddings(model="text-embedding-3-small")
    texts_docs = [(doc.page_content, doc) for doc in all_split_docs if doc.page_content.strip()]
    texts, docs = zip(*texts_docs)
    raw_vectors = np.array(base_embedder.embed_documents(list(texts)))

    # ---------------------- Step 2: Filter Invalid Vectors ----------------------
    filtered_vectors = []
    filtered_docs = []
    for vec, doc in zip(raw_vectors, docs):
        if np.all(np.isfinite(vec)) and np.linalg.norm(vec) > 1e-6:
            filtered_vectors.append(vec)
            filtered_docs.append(doc)

    # raw_vectors = np.array(filtered_vectors)

    # ---------------------- Step 3: Clip Outliers ----------------------
    filtered_vectors = np.clip(filtered_vectors, -1000, 1000)

    # ---------------------- Step 4: Normalize ----------------------
    scaler = StandardScaler()
    normalized_vectors = scaler.fit_transform(filtered_vectors)

    # ---------------------- Step 4.5: Drop Low-Variance Features ----------------------
    variances = np.var(normalized_vectors, axis=0)
    stable_mask = variances > 1e-6
    normalized_vectors = normalized_vectors[:, stable_mask]
    print(f"✅ Retained {np.sum(stable_mask)} stable features out of {len(stable_mask)}.")

    # ---------------------- Step 5: PCA Fit ----------------------
    pca = PCA(n_components=256, svd_solver='full')
    pca.fit(normalized_vectors)

    # ---------------------- Step 6: Final Check Before PCA Transform ----------------------
    clean_vector = []
    clean_docs = []

    for vec, doc in zip(normalized_vectors, filtered_docs):
        if np.all(np.isfinite(vec)) and np.linalg.norm(vec) < 100:  # tighter threshold
            clean_vector.append(vec)
            clean_docs.append(doc)

    clean_vector = np.array(clean_vector)

    # Now safely transform
    transformed_vectors = pca.transform(clean_vector)

    print("PCA transformation completed successfully.")

    print("PCA transformed vectors:")
    print("Transformed vectors shape:", transformed_vectors.shape)
    print("Any NaN in transformed vectors?", np.isnan(transformed_vectors).any())
    print("Max component magnitude:", np.max(np.abs(transformed_vectors)))

    print("PCA components:")
    print("PCA components shape:", pca.components_.shape)
    print("Any NaN in PCA components?", np.isnan(pca.components_).any())
    print("Max component magnitude:", np.max(np.abs(pca.components_)))

    # ---------------------- Step 7: Create FAISS Index ----------------------
    index = faiss.IndexFlatL2(transformed_vectors.shape[1])
    index.add(transformed_vectors.astype("float32"))

    docstore = InMemoryDocstore(dict(enumerate(clean_docs)))  # <-- use aligned docs
    index_to_docstore_id = {i: i for i in range(len(clean_docs))}

    faiss_index = FAISS(
        embedding_function=None,
        index=index,
        docstore=docstore,
        index_to_docstore_id=index_to_docstore_id
    )

    # ---------------------- Step 8: Save Everything ----------------------
    save_dir = "fides_faiss_crawled_data"
    os.makedirs(save_dir, exist_ok=True)

    faiss_index.save_local(os.path.join(save_dir, "fides_faiss_pca_256"))

    with open(os.path.join(save_dir, "fides_pca_256_model.pkl"), "wb") as f:
        pickle.dump(pca, f)

    with open(os.path.join(save_dir, "fides_scaler.pkl"), "wb") as f:
        pickle.dump(scaler, f)

    with open(os.path.join(save_dir, "fides_feature_mask.npy"), "wb") as f:
        np.save(f, stable_mask)

    print("✅ All components saved: FAISS index, PCA model, Scaler, and feature mask.")
    return

