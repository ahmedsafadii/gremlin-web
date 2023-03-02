import openai
from gremlin.settings_dev import OPENAI_KEYS
from utils.helper import get_setting_value


class OpenAIManager:
    def __init__(
        self,
        model=str(get_setting_value("model")),
        max_tokens=int(get_setting_value("max_tokens")),
        temperature=float(get_setting_value("temperature")),
        top_p=float(get_setting_value("top_p")),
        frequency_penalty=float(get_setting_value("frequency_penalty")),
        presence_penalty=float(get_setting_value("presence_penalty")),
        is_general_chat=True,
    ):

        self.api_keys = OPENAI_KEYS
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.is_general_chat = is_general_chat
        self.current_api_key = 0
        self.model_messages = []

        openai.api_key = self.api_keys[self.current_api_key]

    def create_completion(self, messages=None):
        try:
            print(messages)
            response = openai.ChatCompletion.create(model=self.model, messages=messages)
            # temperature = self.temperature,
            # max_tokens = self.max_tokens,
            # top_p = self.top_p,
            # frequency_penalty = self.frequency_penalty,
            # presence_penalty = self.presence_penalty,
            return True, response
        except openai.error.RateLimitError:
            # TODO: I need to create a notification center for each key, to balance the usage
            self.current_api_key += 1
            if self.current_api_key < len(self.api_keys):
                openai.api_key = self.api_keys[self.current_api_key]
                self.create_completion(messages)
            else:
                return (
                    False,
                    "We have a high demand usage, please try again in a minute",
                )
        except (Exception,) as e:
            return False, str(e)

    @staticmethod
    def calculate_cost(prompt):
        return len(prompt)
