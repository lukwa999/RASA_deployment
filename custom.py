from typing import Optional, Dict, Text, Any, List
from rasa.engine.graph import ExecutionContext, GraphComponentException
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.engine.graph import GraphComponent
from rasa.shared.nlu.constants import TEXT_TOKENS
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.training_data.training_data import TrainingData
import spacy
import spacy_pythainlp.core

@DefaultV1Recipe.register(
    [DefaultV1Recipe.ComponentType.MESSAGE_TOKENIZER], is_trainable=False
)
class SpacyPythainlpTokenizer(GraphComponent):
    def __init__(
        self,
        config: Optional[Dict[Text, Any]] = None,
        model_storage: Optional[ModelStorage] = None,
        resource: Optional[Resource] = None,
        execution_context: Optional[ExecutionContext] = None,
    ) -> None:
        try:
            # Initialize spaCy with PyThaiNLP
            self.nlp = spacy.blank("th")
            self.nlp.add_pipe("pythainlp")
        except Exception as e:
            raise GraphComponentException(f"Error initializing SpacyPythainlpTokenizer: {str(e)}")

    @classmethod
    def create(
        cls,
        config: Optional[Dict[Text, Any]],
        model_storage: Optional[ModelStorage],
        resource: Optional[Resource],
        execution_context: Optional[ExecutionContext],
    ) -> GraphComponent:
        return cls(config, model_storage, resource, execution_context)

    def train(self, training_data: TrainingData) -> Resource:
        # Implement the training logic if needed
        pass

    def process(self, messages: List[Message]) -> List[Message]:
        for message in messages:
            try:
                doc = self.nlp(message.get("text"))
                tokens = [
                    {
                        "text": token.text,
                        "start": token.idx,
                        "end": token.idx + len(token),
                        "lemma": token.lemma_,
                        "pos": token.pos_,
                        "entity_type": token.ent_type_,
                    }
                    for token in doc
                ]   
                message.set(TEXT_TOKENS, tokens)
            except Exception as e:
                raise GraphComponentException(f"Error processing message: {str(e)}")

        return messages

    def process_training_data(self, training_data: TrainingData) -> TrainingData:
        # Implement the logic to process training data if needed
        # This method is required for message tokenizers
        return training_data

    def persist(self, file_name: str, model_dir: str) -> Optional[Dict[Text, Any]]:
        # Implement model persistence logic if needed
        pass

    @classmethod
    def load(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
        **kwargs: Any,
    ) -> "SpacyPythainlpTokenizer":
        try:
            return cls(config, model_storage, resource, execution_context)
        except Exception as e:
            raise GraphComponentException(f"Error loading SpacyPythainlpTokenizer: {str(e)}")
