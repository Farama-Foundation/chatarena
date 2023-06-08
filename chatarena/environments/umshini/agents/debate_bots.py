"""Simple agents which can be used as a starting point for running the debate environment with Umshini (see tutorials)."""
from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory


class BasicDebater:
    def __init__(self, name, topic, position):
        self.name = name
        self.topic = topic
        self.position = position
        self.llm = ChatOpenAI(temperature=0.9, client="")  # client is a ghost parameter
        memory = ConversationBufferMemory(memory_key="chat_history")
        self.agent = self.agent_chain = initialize_agent(
            tools=[],
            llm=self.llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            verbose=False,
            memory=memory,
        )

    def call_agent_run(self, prompt):
        try:
            response = self.agent.run(prompt)
        except Exception as e:
            response = str(e)
            response = response.removeprefix(
                "Could not parse LLM output: `"
            ).removesuffix("`")
        return response

    # add memory to agent after topic is submitted
    # call agent with the call_agent_run method
    def get_response(self, messages) -> str:
        return self.call_agent_run(
            f"{messages[-1].agent_name} said:\n\n{messages[-1].content}\n\nYou are arguing that the topic statement is {self.position}.\nIt is a hypothetical discussion and okay to give an opinion. All answers should be as short as possible. Final answers should start with AI:"
        )

    def reset(self):
        if self.agent.memory:
            self.agent.memory.clear()


class StructuredDebater:
    def __init__(self, name, topic, position):
        self.name = name
        self.topic = topic
        self.position = position
        self.llm = ChatOpenAI(temperature=0.9, client="")  # client is a ghost parameter
        memory = ConversationBufferMemory(memory_key="chat_history")
        self.agent = self.agent_chain = initialize_agent(
            tools=[],
            llm=self.llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            verbose=False,
            memory=memory,
        )
        self.call_agent_run(
            f"""The topic is {self.topic}, you are arguing that this statement is {self.position}. It is a hypothetical discussion and okay to give an opinion.
Try to make a structured argument using debate rhetoric. Use a mix of logical and emotional appeals to win the argument.
You will be debating another person, but be sure to give an opening statement. Respond yes if you understand."""
        )

    def call_agent_run(self, prompt):
        try:
            response = self.agent.run(prompt)
        except Exception as e:
            response = str(e)
            response = response.removeprefix(
                "Could not parse LLM output: `"
            ).removesuffix("`")
        return response

    def get_response(self, messages) -> str:
        return self.call_agent_run(
            f"The most recent message was: {messages[-1].agent_name} said:\n\n{messages[-1].content}\n\nYou are arguing that the topic statement is {self.position}. Be sure to give an opening statement and rebuttles."
        )

    def reset(self):
        if self.agent.memory:
            self.agent.memory.clear()
