from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.llms import HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from typing import Dict, List, Optional
import logging
import uuid
from services.vector_store import vector_store_service

logger = logging.getLogger(__name__)

class ChatbotService:
    """RAG-based chatbot service for answering business queries."""
    
    def __init__(self):
        """Initialize the chatbot with RAG pipeline."""
        self.sessions: Dict[str, List[Dict]] = {}
        self.qa_chain = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the language model and QA chain."""
        try:
            # For production, you can use OpenAI or other API-based models
            # This uses a local model for demonstration
            logger.info("Initializing language model...")
            
            # Using a smaller model for CPU inference
            # You can change this to use OpenAI API instead
            model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
            
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                device_map="cpu",
                low_cpu_mem_usage=True
            )
            
            # Create pipeline
            pipe = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                max_new_tokens=512,
                temperature=0.7,
                top_p=0.95,
                repetition_penalty=1.15
            )
            
            llm = HuggingFacePipeline(pipeline=pipe)
            
            # Create prompt template
            prompt_template = """You are a helpful AI assistant for a business website. Use the following context to answer the user's question. If you don't know the answer based on the context, say so politely.

Context: {context}

Question: {question}

Answer: """
            
            PROMPT = PromptTemplate(
                template=prompt_template,
                input_variables=["context", "question"]
            )
            
            # Create QA chain
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=vector_store_service.vectorstore.as_retriever(
                    search_kwargs={"k": 3}
                ),
                return_source_documents=True,
                chain_type_kwargs={"prompt": PROMPT}
            )
            
            logger.info("Language model initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing LLM: {e}")
            logger.warning("Falling back to simple retrieval-based responses")
            self.qa_chain = None
    
    def get_or_create_session(self, session_id: Optional[str] = None) -> str:
        """Get existing session or create a new one."""
        if session_id and session_id in self.sessions:
            return session_id
        
        new_session_id = str(uuid.uuid4())
        self.sessions[new_session_id] = []
        return new_session_id
    
    def add_to_history(self, session_id: str, role: str, content: str):
        """Add message to session history."""
        if session_id in self.sessions:
            self.sessions[session_id].append({
                "role": role,
                "content": content
            })
    
    async def chat(self, message: str, session_id: Optional[str] = None) -> Dict:
        """
        Process a chat message and return response.
        
        Args:
            message: User's message
            session_id: Optional session ID
            
        Returns:
            Dictionary with response, session_id, and sources
        """
        try:
            # Get or create session
            session_id = self.get_or_create_session(session_id)
            
            # Add user message to history
            self.add_to_history(session_id, "user", message)
            
            if self.qa_chain:
                # Use RAG pipeline
                result = self.qa_chain.invoke({"query": message})
                response = result['result']
                
                # Extract source documents
                sources = []
                if 'source_documents' in result:
                    for doc in result['source_documents']:
                        if 'filename' in doc.metadata:
                            sources.append(doc.metadata['filename'])
                
                sources = list(set(sources))  # Remove duplicates
            else:
                # Fallback to simple retrieval
                search_results = vector_store_service.similarity_search(message, k=3)
                
                if search_results:
                    # Combine top results
                    context = "\n\n".join([r['content'] for r in search_results])
                    response = f"Based on the available information:\n\n{context[:500]}..."
                    
                    sources = list(set([
                        r['metadata'].get('filename', 'Unknown')
                        for r in search_results
                    ]))
                else:
                    response = "I don't have enough information to answer that question. Please upload relevant documents or contact our support team."
                    sources = []
            
            # Add assistant response to history
            self.add_to_history(session_id, "assistant", response)
            
            return {
                "response": response,
                "session_id": session_id,
                "sources": sources
            }
            
        except Exception as e:
            logger.error(f"Error processing chat message: {e}")
            return {
                "response": "I apologize, but I encountered an error processing your request. Please try again.",
                "session_id": session_id or self.get_or_create_session(),
                "sources": []
            }
    
    def get_session_history(self, session_id: str) -> List[Dict]:
        """Get chat history for a session."""
        return self.sessions.get(session_id, [])
    
    def clear_session(self, session_id: str) -> bool:
        """Clear a chat session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

# Global instance
chatbot_service = ChatbotService()
