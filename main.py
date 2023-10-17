import openai
from io import StringIO
import streamlit as st
from streamlit_chat import message
import pandas as pd


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
report_text = ""
file_contents = []
with st.sidebar:
    textfile = st.file_uploader("Upload TIP Sheet file", type=["txt","csv"], accept_multiple_files=True)
    if textfile:
        for file in textfile:
            if file.type == "text/csv":
                try:
                    df = pd.read_csv(file)
                    # Calculate the number of unique combinations of the specified columns
                    unique_structures = df.drop_duplicates(
                        subset=['experience number', 'report number', 'sub code', 'claim branch code']).shape[0]
                    structure_tot_text = "Total number of structures are " + str(unique_structures)
                    rpt_unique_values = df['report name'].dropna().astype(str).unique()
                    rpt_unique_values_str = ', '.join(rpt_unique_values)
                    report_text = "List of Report Name: " + rpt_unique_values_str

                    exp_unique_values = df['experience name'].dropna().astype(str).unique()
                    exp_unique_values_str = ', '.join(exp_unique_values)
                    exp_text = "List of Experience Name: " + exp_unique_values_str
                    tip_text_all = tip_text_all + '\n' + structure_tot_text + '\n' + report_text + '\n' + exp_text
                except Exception as e:
                    st.write("Error:", e)
            elif file.type == "text/plain":
                stringio = StringIO(file.getvalue().decode("utf-8"))
                tip_text = stringio.read()
                tip_text_all = tip_text_all + '\n' + tip_text
            else:
                st.warning("Please upload one or more text/csv files.")
    #print(tip_text_all)
    system_text2 = st.text_area("Enter System Prompt",
                                value= "Consider you are an account service specialist for the absence and disability group benefit administrator. "
                                        "The customers of the company are employers with many employees. The employees are grouped into buckets called 'Structure'. "
                                        "Products are defined in the Product list or in the Report name list data where the description is either a "
                                        "life insurance product or a disability or an absence product. "
                                        "For each customer, you have created a document called a TIP sheet. This document describes very important information "
                                        "regarding the customer including but not limited to customer name, customer number, and products offered along with "
                                        "the product-specific instructions based on groupings of employees. "
                                        "This document will describe any exceptions created for the account/customer. The document also describes various plans "
                                        "including benefit calculation and business rules for each plan defined as plan 1, option 1, or plan 1 option 2, etc. "
                                        "Lastly, the document has information related to the pre-disability definition and business rules around it. "
                                        "As an account service specialist, you only answer questions related to the topic of absence and disability benefits "
                                        "and related to the provided TIP sheet document!.", height=250)
    user_text = st.text_area("Enter Prompt",
                                value= "provide following infomation in table fomat. First column as asks and second column as answer to the asks. \n"
                                        "-Customer number and Name \n"
                                        "- identify list of non disability or non absence insurance products from report name \n"
                                        "- identify list of all insurance products from report name \n"
                                        "- Number of unique insurance products (list of life insurance, disability and absence products in the report name column) \n"
                                        "- identify list of absence and disability products from report name. \n"
                                        "- total number of structure \n"
                                        "- Broker contact \n"
                                        "-CSC contact \n"
                                        "- TPA contact \n"
                                        "- Account Rep \n"
                                        "- Definition of pre-disability \n"
                                        "- list of Funding Types ", height=250)
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
