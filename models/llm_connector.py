from models.claude import ClaudeModel
from models.llama import LlamaModel
    
class Models:
    claude = ClaudeModel,
    llama = LlamaModel
    

class LLMConnector:
    models ={
        "claude": ClaudeModel,
        "llama": LlamaModel
    }

    def get_model(name: str):
        if not name :
            return LLMConnector.models['llama']
        model = LLMConnector.models.get(name, "llama")
        return model