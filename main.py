import openai
import os
from dotenv import find_dotenv, load_dotenv
import time
from datetime import datetime
import requests
import json
import streamlit as st

load_dotenv()

news_api_key = os.environ.get("NEWS_API_KEY")

client = openai.OpenAI()
model = "gpt-3.5-turbo-0125"

def get_news(topic):
    url = (
        f"https://newsapi.org/v2/everything?q={topic}&apiKey={news_api_key}&pageSize=5"
    )

    try:
        response = requests.get(url)
        if response.status_code == 200:
            news = json.dumps(response.json(), indent=4)
            news_json = json.loads(news)

            data = news_json

            # status = data["status"]
            # total_results = data["totalResults"]
            articles = data["articles"]
            formatted_news = []

            # Loop through articles
            for article in articles:
                source_name = article["source"]["name"]
                author = article["author"]
                title = article["title"]
                description = article["description"]
                url = article["url"]
                # content = article["content"]
                article_info = f""" 
                    Title: {title},
                    Author: {author},
                    Source: {source_name}.
                    Description: {description},
                    URL: {url}
                """
                formatted_news.append(article_info)
            return formatted_news
        else:
            return []

    except requests.exceptions.RequestException as e:
        print("Error occured during API Request", e)

class AssistantManager:
    thread_id = None
    assistant_id = None

    def __init__(self, model: str = model):
        self.client = client
        self.model = model
        self.assistant = None
        self.thread = None
        self.run = None
        self.summary = None

        # Retrieve existing assistant and thread if IDs are already set
        if AssistantManager.assistant_id:
            self.assistant = self.client.beta.assistants.retrieve(
                assistant_id=AssistantManager.assistant_id
            )
        if AssistantManager.thread_id:
            self.thread = self.client.beta.threads.retrieve(
                thread_id=AssistantManager.thread_id
            )

    def create_assistant(self, name, instructions, tools):
        if not self.assistant:
            new_assistant = self.client.beta.assistants.create(
                name=name,
                instructions=instructions,
                tools=tools,
                model=self.model
            )
            AssistantManager.assistant_id = new_assistant.id
            print(new_assistant.id)
            self.assistant = new_assistant

    def create_thread(self):
        if not self.thread:
            new_thread = self.client.beta.threads.create()
            AssistantManager.thread_id = new_thread.id
            print(new_thread.id)
            self.thread = new_thread

    def add_message_to_thread(self, role, content):
        if self.thread:
            self.client.beta.threads.messages.create(
                thread_id=self.thread.id,
                role=role,
                content=content
            )

    def run_assistant(self):
        if self.thread and self.assistant:
            self.run = self.client.beta.threads.runs.create(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id,
            )

    def process_message(self):
        if self.thread:
            messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)
            summary = []

            last_message = messages.data[0]
            # role = last_message.role
            response = last_message.content[0].text.value
            summary.append(response)

            self.summary = "\n".join(summary)

    def call_required_functions(self, required_actions):
        if not self.run:
            return
        tool_outputs = []

        for action in required_actions["tool_calls"]:
            func_name = action["function"]["name"]
            arguments = json.loads(action["function"]["arguments"])

            if func_name == "get_news":
                output = get_news(topic=arguments["topic"])
                final_str = ""
                for item in output:
                    final_str += "".join(item)

                tool_outputs.append({"tool_call_id": action["id"],
                                     "output": final_str})
            else:
                raise ValueError(f"Unknown function: {func_name}")

        print("Submitting outputs back to the Assistant...")
        self.client.beta.threads.runs.submit_tool_outputs(
            thread_id=self.thread.id,
            run_id=self.run.id,
            tool_outputs=tool_outputs
        )

    def get_summary(self):
        return self.summary

    def wait_for_completion(self):
        if self.thread and self.run:
            while True:
                time.sleep(5)
                run_status = self.client.beta.threads.runs.retrieve(
                    thread_id=self.thread.id,
                    run_id=self.run.id
                )

                if run_status.status == "completed":
                    self.process_message()
                    break
                elif run_status.status == "requires_action":
                    self.call_required_functions(
                        required_actions=run_status.required_action.submit_tool_outputs.model_dump()
                    )

    def run_steps(self):
        run_steps = self.client.beta.threads.runs.steps.list(
            thread_id=self.thread.id,
            run_id=self.run.id
        )
        return run_steps.data

def main():
    # news = get_news("bitcoin")
    # print(news[0])

    manager = AssistantManager()

    # Steamlit interface
    st.title("NewsDigest")

    with st.form(key="user_input_form"):
        instructions = st.text_input("Enter topic:")
        submit_button = st.form_submit_button(label="Run Assistant")

        if submit_button:
            manager.create_assistant(
                name="NewsDigest",
                instructions = """Synthesize the provided news articles into a well-organized and insightful summary. For each article, follow this consistent format:

                ## Article Title

                *By [Author Name] | [Source Name]*

                [A concise 2-3 sentence summary capturing the key points from the article description]

                [Read more at [Source Name]](URL)

                After summarizing the individual articles, provide a brief sentiment analysis of the overall news coverage, using the following format:

                ## Sentiment Analysis

                The prevailing sentiment across the articles is [positive/negative/neutral]. [Provide a 2-3 sentence justification for your assessment, citing specific examples from the article summaries].

                Please use the specified format consistently for each article and the sentiment analysis to ensure clarity and readability. The final deliverable should enable the reader to quickly grasp the essential information and overarching narrative from the collection of news articles.""",
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": "get_news",
                            "description": "Get the list of articles / news for the given topic.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "topic": {
                                        "type": "string",
                                        "description": "The topic for the news, e.g. Bitcoin.",
                                    }
                                },
                                "required": ["topic"],
                            },
                        },
                    }
                ]
            )
            manager.create_thread()

            # Add the message and run the assistant
            manager.add_message_to_thread(
                role="user",
                content=f"Summarize the news on this topic: {instructions}."
            )
            manager.run_assistant()

            # Wait for completions and process messages
            manager.wait_for_completion()

            summary = manager.get_summary().replace("$", "\\$")

            st.write(summary)

if __name__ == "__main__":
    main()