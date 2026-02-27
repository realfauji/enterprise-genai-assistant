from langchain_classic.memory import ConversationBufferMemory
from langchain_core.messages import AIMessage, HumanMessage


def build_memory(messages):
    memory = ConversationBufferMemory(return_messages=True)

    for msg in messages:
        if msg.role == "user":
            memory.chat_memory.add_message(HumanMessage(content=msg.content))
        else:
            memory.chat_memory.add_message(AIMessage(content=msg.content))

    return memory