from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.memory import RedisChatMessageHistory, ConversationBufferMemory
from langchain.chains import ConversationChain, LLMChain
from langchain.prompts import PromptTemplate


from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma, DocArrayInMemorySearch
from langchain.document_loaders import TextLoader
from langchain.chains import RetrievalQA,  ConversationalRetrievalChain
from langchain.document_loaders import TextLoader
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders.csv_loader import CSVLoader
import param
import frappe
import os
import json
from frappe.model.document import Document

custom_template ="""When a user requests the creation of a sales order,You have to ask user please provide the "Customer Name" and "Item Name."  \n
Then generate a JSON format using  "Customer Name" and "Item Name" that has been provided by user and respond with the formatted data.
Remember you are strictly instructed to identify the "Customer Name" and "Item Name" and generate only JSON response. Don't make extra response
 that could raise error for JSON handeling.

Do not make any response if the question is not related to sales order, simply reply "I am here assist you to place a order". 
But it's okay if the user wants you to greetings.
If there's information I'm not familiar with, I'll let you know."
Question: {question}
Helpful Answer:
"""


prompt = PromptTemplate(
    input_variables=["question"],
    template=custom_template
)


os.environ["OPENAI_API_KEY"] = "YOUR_OPEN_API_KEY"

llm = OpenAI(model_name="gpt-3.5-turbo", temperature=0, openai_api_key="YOUR_OPEN_API_KEY")


class getChat():
    items = []
    def get_response(self, user_input):
        # prompt.format(name="Shuvo", question=user_input)
        # response = llm(user_input)
        # response = prompt.format(user_question=user_input)
        chain = LLMChain(llm=llm, prompt=prompt)
        response = chain.run(question=user_input)
        try:
            # Parse the data as JSON
            data_dict = json.loads(response)

            # Iterate through the data
            for key, value in data_dict.items():
                print(f"{key}: {value}")

                # If the value is a list, iterate through it
                if isinstance(value, list):
                    for item in value:
                        # print(f"  - {item}")
                        self.items.append(item)
                        note = frappe.get_doc({"doctype": "Auto", "item": item})
                        note.insert()
                        frappe.db.commit()
            response = f"Thanks for ordering! You have been charged total 20$, including VAT, type YES for confirm"
            print(response)
            return response
        except json.JSONDecodeError: 
            print(response)

            return response
    def get_chat(self):
        jsn = self.items
        for item in jsn:
            note = frappe.get_doc({"doctype": "Auto", "item": item})
            note.insert()
            frappe.db.commit()
        print(jsn)

chats = getChat()
# while True:
#     user_input = input("> ")
#     chats.get_response(user_input)
  

@frappe.whitelist()
def get_chat_response(user_input):
    response = chats.get_response(user_input)
    return response 



