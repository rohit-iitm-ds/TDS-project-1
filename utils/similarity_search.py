import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json
import pickle
import os

class SimilaritySearch:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.embeddings = None
        self.documents = None
        
    def load_documents(self, posts_file, content_file=None):
        """Load documents from JSON files"""
        documents = []
        
        # Load discourse posts
        if os.path.exists(posts_file):
            with open(posts_file, 'r', encoding='utf-8') as f:
                posts = json.load(f)
                
            for post in posts:
                doc = {
                    'type': 'discourse_post',
                    'content': post.get('raw_content', ''),
                    'title': post.get('topic_title', ''),
                    'url': post.get('topic_url', ''),
                    'username': post.get('username', ''),
                    'created_at': post.get('created_at', ''),
                    'post_number': post.get('post_number', 1),
                    'like_count': post.get('like_count', 0)
                }
                
                if doc['content'].strip():  # Only add non-empty posts
                    documents.append(doc)
        
        # Load course content if available
        if content_file and os.path.exists(content_file):
            with open(content_file, 'r', encoding='utf-8') as f:
                content = json.load(f)
                
            for item in content:
                doc = {
                    'type': 'course_content',
                    'content': item.get('content', ''),
                    'title': item.get('title', ''),
                    'url': item.get('url', ''),
                    'section': item.get('section', '')
                }
                
                if doc['content'].strip():
                    documents.append(doc)
        
        self.documents = documents
        return len(documents)
    
    def create_embeddings(self, force_recreate=False):
        """Create embeddings for all documents"""
        embeddings_file = 'data/embeddings.pkl'
        
        if not force_recreate and os.path.exists(embeddings_file):
            print("Loading existing embeddings...")
            with open(embeddings_file, 'rb') as f:
                self.embeddings = pickle.load(f)
            return
        
        if not self.documents:
            raise ValueError("No documents loaded. Call load_documents first.")
        
        print(f"Creating embeddings for {len(self.documents)} documents...")
        
        # Prepare texts for embedding
        texts = []
        for doc in self.documents:
            # Combine title and content for better context
            text = f"{doc['title']} {doc['content']}"
            texts.append(text)
        
        # Create embeddings in batches to avoid memory issues
        batch_size = 32
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = self.model.encode(batch)
            embeddings.extend(batch_embeddings)
            print(f"Processed {min(i + batch_size, len(texts))}/{len(texts)} documents")
        
        self.embeddings = np.array(embeddings)
        
        # Save embeddings for future use
        os.makedirs('data', exist_ok=True)
        with open(embeddings_file, 'wb') as f:
            pickle.dump(self.embeddings, f)
        
        print("Embeddings created and saved!")
    
    def search(self, query, top_k=5, min_similarity=0.3):
        """Search for similar documents"""
        if self.embeddings is None or self.documents is None:
            raise ValueError("Embeddings and documents must be loaded first.")
        
        # Create query embedding
        query_embedding = self.model.encode([query])
        
        # Calculate similarities
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        
        # Get top results
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            similarity = similarities[idx]
            if similarity >= min_similarity:
                result = {
                    'document': self.documents[idx],
                    'similarity': float(similarity),
                    'index': int(idx)
                }
                results.append(result)
        
        return results
    
    def get_context_for_llm(self, query, max_context_length=4000):
        """Get relevant context for LLM"""
        results = self.search(query, top_k=10, min_similarity=0.2)
        
        context_parts = []
        current_length = 0
        
        for result in results:
            doc = result['document']
            
            # Format the context
            if doc['type'] == 'discourse_post':
                context = f"Forum Post - {doc['title']}\n"
                context += f"User: {doc['username']}\n"
                context += f"Content: {doc['content'][:500]}...\n"
                context += f"URL: {doc['url']}\n\n"
            else:
                context = f"Course Content - {doc['title']}\n"
                context += f"Content: {doc['content'][:500]}...\n"
                context += f"URL: {doc['url']}\n\n"
            
            if current_length + len(context) <= max_context_length:
                context_parts.append(context)
                current_length += len(context)
            else:
                break
        
        return "\n".join(context_parts), results