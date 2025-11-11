import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai_provider import LLMProvider

llm = LLMProvider()
print(llm.generate("Summarize in one line what AI pair programming means."))
