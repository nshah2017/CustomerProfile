import openai
from io import StringIO
import streamlit as st
from streamlit_chat import message


def read_text_file(file_path):
    try:
        with open(file_path, 'r') as file:
            raw_text = file.read()
        return raw_text
    except FileNotFoundError:
        print("File not found.")


def generate_customer_profile(api_key, system_text1, user_text1):
    openai.api_key = api_key
    resp_message = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        temperature=0.5,
        max_tokens=8000,
        messages=[
            {"role": "system",
             "content": system_text1
             },
            {"role": "user",
             "content": user_text1
             }
        ])
    return resp_message["choices"][0]["message"]["content"]


tip_text = ""
tip_text_all = ""
file_contents = []
with st.sidebar:
    textfile = st.file_uploader("Upload TIP Sheet file", type=None, accept_multiple_files=True)
    if textfile:
        for file in textfile:
            stringio = StringIO(file.getvalue().decode("utf-8"))
            tip_text = stringio.read()
            tip_text_all = tip_text_all + '\n' + tip_text
    else:
        st.warning("Please upload one or more text files.")
    system_text2 = st.text_area("Enter System Prompt",
                                value="Consider you are an account specialist for the absence and disability "
                                      "insurance company. You are working on important accounts. For each account you have created document "
                                      "call TIP sheet. This document describes very important information regarding the customer including "
                                      "but not limited to customer name, number, products offered (AMS : Absence Management Product) and "
                                      "lives covered. Document also describes structures which is comprised of experience + report + subplan "
                                      "+ subcode or branch. This document will describe any exceptions created for the account/customer. "
                                      "Document also describes various plans including benefit calculation and business rules for each plan. "
                                      "Lastly document has information related to prediability definition and business rules around it. "
                                      "I will be supplying one such document and I need your help to extract some information. Here is the "
                                      "texts from the TIP sheet.", height=250)
    user_text = st.text_area("Enter Prompt", value="Can you extract following information from the TIP sheet.\n"
                                                   "- customer name and number.\n"
                                                   "- products offered along with number of lives and funding type where available else just mention the product.\n"
                                                   "-  No. of unique structures (structure is experience + report + sub + branch)\n"
                                                   "- Does customer has TPA?\n"
                                                   "- What is the definition of predisability earnings?\n"
                                                   " who are the main contacts for this customer (CSC, Broker, Account Rep etc.)",
                             height=250)
    m = st.markdown("""
            <style>
                div.stButton > button:first-child {
                    background-color: #0099ff;
                color:#ffffff;
                }
            </style>""", unsafe_allow_html=True)
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    response_message = ""

tab1, tab2 = st.tabs(["Customer Profile", "Chat with TIP Sheet"])

with tab1:
    st.header("Customer Profile")
    if st.button("Generate Customer Profile"):
        with st.spinner("processing..."):
            system_text2 = system_text2 + " " + tip_text_all
            response_message = generate_customer_profile(openai_api_key, system_text2, user_text)
            st.write(response_message)
with tab2:
    st.header("Chat with TIP Sheet")
    if 'generated' not in st.session_state:
        st.session_state['generated'] = []

    if 'past' not in st.session_state:
        st.session_state['past'] = []
    if st.button('Clear Chat'):
        st.session_state.past = []
        st.session_state.generated = []
        if input not in st.session_state:
            st.session_state.input = ""
        for i in range(len(st.session_state['generated']) - 1, -1, -1):
            message(st.session_state["generated"][i], key=str(i))
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')

    def get_text():
        input_text = st.text_input("", key="input")
        return input_text


    user_input = get_text()
    system_text2 = system_text2 + " " + tip_text_all
    if user_input:
        output = generate_customer_profile(openai_api_key, system_text2, user_input)
        st.session_state.past.append(user_input)
        st.session_state.generated.append(output)
    if st.session_state['generated']:
        for i in range(len(st.session_state['generated']) - 1, -1, -1):
            message(st.session_state["generated"][i], key=str(i))
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
