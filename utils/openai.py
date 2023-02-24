import openai
from gremlin.settings_dev import OPENAI_KEYS


class OpenAIManager:
    def __init__(
        self,
        model="text-davinci-003",
        max_tokens=256,
        temperature=0.7,
        top_p=0.5,
        frequency_penalty=0.7,
        presence_penalty=0.7,
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

    def create_completion(self, prompt):
        try:
            if self.is_general_chat:
                stop = [" Human:", " AI:"]
            else:
                stop = None

            response = openai.Completion.create(
                model=self.model,
                prompt=prompt,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
                frequency_penalty=self.frequency_penalty,
                presence_penalty=self.presence_penalty,
                stop=stop,
            )

            return True, response
        except openai.error.RateLimitError:
            # TODO: I need to create a notification center for each key, to balance the usage
            self.current_api_key += 1
            if self.current_api_key < len(self.api_keys):
                openai.api_key = self.api_keys[self.current_api_key]
                self.create_completion(prompt)
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
