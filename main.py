import os
import streamlit as st
import pandas as pd 
import pyodbc
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI()
st.title('Purchasing Assistant')

driver = 'SQL Server'
database = 'AdventureWorks2022'
server = 'ATISL400'

def get_prompt(question):
    prompt = f"""
    You are a records keeper at a company. You will help in inserting, retrieving, updating, and deleting records in the database.
    The database you are working with is the AdventureWorks2022 database.
    
    You are specifically meant to assist in the purchasing department. You will be asked questions about the purchasing department only.
    
    The user will first tell you what action they want to perform.
    Then your job is to ask the user questions to get more information about the action they want to perform.
    
    Example:
    User: I want to add a purchase order.
    
    Chatbot: Sure! Let’s add a purchase order. First, I’ll gather all the necessary details.
    What is the VendorID for this purchase order?
    (This is the vendor who will supply the goods.)
    
    User: VendorID is 102.

    Chatbot: Got it! VendorID is 102.
    What is the ShipMethodID for this purchase order?
    (This is the shipping method you’d like to use, e.g., Air, Ground, etc.)
    
    User: Use ShipMethodID 5.

    Chatbot: Noted. ShipMethodID is 5.
    What is the Order Date for this purchase order?
    (You can provide today’s date if that works for you.)
    
    User: Use today’s date.

    Chatbot: Alright, using today’s date.
    Do you know the Tax Amount and Freight cost for this purchase order?
    (If you don’t have the exact values, we can set these to 0 for now.)
    
    User: Set Tax Amount to 10$ and Freight to 5$.

    Chatbot: Got it! Tax Amount is 10$, and Freight is 5$.
    What products are you ordering?
    (Please provide the product names, quantities, and unit prices.)
    
    User: I need:
    2 units of "Mountain Bike" at 50$ each
    1 unit of "Touring Bike" at 90$ each
    
    Chatbot: Thanks! Let me retrieve the ProductIDs for these products.
    (Chatbot performs a query on the Products table to find the corresponding ProductIDs.)

    ProductID Lookup:
    Mountain Bike → ProductID: 301
    Touring Bike → ProductID: 302
    Chatbot: I’ve found the ProductIDs for the items you mentioned.
    
    At the end of the conversation you will summarise the information you have gathered and dump it in a JSON.
    """
    
    return prompt

def ask_question(question):
    prompt  = get_prompt(question)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": question}
        ],
        temperature=0
    )
    return response.choices[0].message.content

def get_connection(driver, server, database):
    """Create a connection to the SQL Server database."""
    try:
        connection_string = f"""
            DRIVER={driver};
            SERVER={server};
            DATABASE={database};
            Trusted_Connection=yes;
            """
        connection = pyodbc.connect(connection_string)
        return connection
    except Exception as e:
        print(f"Error: {e}")

connection = get_connection(driver, server, database)

def main():
    logo_url = 'Ellicium-Website-Logo.svg'
    
    st.logo(logo_url, size="large")
    
    with st.chat_message('ai'):
        st.write("""Hello! I'm your purchasing assistant. I am here to assist you in interacting with the database. 
                 How may I be of service to you today?""")
        
    if 'conversation' not in st.session_state:
        st.session_state.conversation = []
    
    user_input = st.chat_input('>')
    
    if user_input:
        # with st.chat_message('user'):
        #     st.write(user_input)
        
        st.session_state.conversation.append({"role": "user", "content": user_input})
    
    answer = ask_question(user_input)
    st.session_state.conversation.append({"role": "assistant", "content": answer})
    
    for message in st.session_state.conversation:
        with st.chat_message(message['role']):
            st.write(message['content'])
            

if __name__ == "__main__":
    main()

