from OpenAi import OpenAi
from ..LLMEnums import LLMEnums, OpenAIEnums
from ..LLMInterface import LLMInterface
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenAIProvider:
    def __init_(self, api_key:str, api_url:str=None,
    default_input_max_characters:int=1000, 
    default_generation_max_output_tokens:int=1000,
    default_generation_temperature:float=0.1):
        self.api_key = api_key
        self.api_url = api_url

        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature
        
        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        self.client = OpenAi(
            api_key=self.api_key,
            api_url=self.api_url
        )
        self.logger = logging.getLogger(__name__)

        set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def generate_text(self, prompt:str, chat_history: list=[], max_output_token:int, temperature:float=None):
       # raise NotImplementedError("generate_text method is not implemented yet.")
        if not self.client:
            self.logger.error("OpenAI client was not set")
            return None
        if not self.generation_model_id:
            self.logger.error("Generation model for OpenAI was not set")
            return None
        max_output_token = max_output_token if max_output_token else self.default_generation_max_output_tokens
        temperature = temperature if temperature else self.default_generation_temperature

        chat_history.append(
            self.construct_prompt(
                prompt=prompt,
                "role": OpenAIEnums.Role.USER.value)
        )

        response = self.client.chat.completions.create(
        
            model = self.generation_model_id,
            messages = chat_history,
            max_tokens = max_output_token,
            temperature = temperature
            )

        if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message or not response.choices[0].message["content"]:
            self.logger.error("Invalid response from OpenAI chat completions OpenAPI")
            return None
        #return response.choices[0].message.content
        return response.choices[0].message["content"]
    
    def embed_text(self, text: str, document_type: str=None):
        if not self.client:
            self.logger.error("OpenAI client was not set")
            return None
        
        if not self.embedding_model_id:
            self.logger.error("Embedding model for OpenAI was not set")
            return None

        response = self.client.embeddings.create(
            model = self.embeddding_model_id,
            input = text,
        )

        if not response or not response.data or len(response.data) == 0 or not response.data[0].embedding:
            self.logger.error("Invalid response from OpenAI embeddings OpenAPI")
            return None 
        return response.data[0].embedding


    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "content": prompt
        }

    # def generate_text(self, prompt: str, input_max_characters: int = None, 
    #                     generation_max_output_tokens: int = None, generation_temperature: float = None):
    #     if self.generation_model_id is None:
    #         raise ValueError("Generation model ID is not set. Please set it using set_generation_model() method.")
        
    #     input_max_characters = input_max_characters or self.default_input_max_characters
    #     generation_max_output_tokens = generation_max_output_tokens or self.default_generation_max_output_tokens
    #     generation_temperature = generation_temperature or self.default_generation_temperature

    #     if len(prompt) > input_max_characters:
    #         raise ValueError(f"Input prompt exceeds the maximum allowed characters of {input_max_characters}.")

    #     response = self.client.chat.completions.create(
    #         model=self.generation_model_id,
    #         messages=[{"role": "user", "content": prompt}],
    #         max_tokens=generation_max_output_tokens,
    #         temperature=generation_temperature
    #     )
    #     return response.choices[0].message.content