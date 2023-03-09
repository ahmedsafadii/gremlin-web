import json
from .models import Topic, Prompt, SubTopic
import os
from django.conf import settings

current_dir = os.path.join(settings.BASE_DIR, "core")

file_path = os.path.join(current_dir, "Prompts.json")

with open(file_path) as f:
    data = json.load(f)
    Topic.objects.all().delete()
    for p in data:
        if int(p["Usages"]) > 5000:
            category = p["Category"]
            community = p["Community"].split("-")
            placeholder = p["PromptHint"]
            title = p["Title"]
            prompt = p["Prompt"]
            description = p["Teaser"]
            topic_object, topic_created = Topic.objects.update_or_create(title=category)
            sub_topic_object, sub_topic_created = SubTopic.objects.update_or_create(
                title=community[0], topic=topic_object
            )
            new_prompt = Prompt()
            new_prompt.sub_topic = sub_topic_object
            new_prompt.placeholder = placeholder
            new_prompt.title = title
            new_prompt.is_active = False
            new_prompt.hidden_prompt = prompt
            new_prompt.content = description
            print(title)
            print(prompt)
            print(description)
            new_prompt.save()
