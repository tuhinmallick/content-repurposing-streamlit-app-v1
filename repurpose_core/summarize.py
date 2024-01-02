import os
import dotenv
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from openai import OpenAI

dotenv.load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
client = OpenAI(api_key=OPENAI_API_KEY)


def summarize_transcription(transcription: str, video_title=None):
    llm = ChatOpenAI(temperature=0)

    text_splitter = CharacterTextSplitter()
    texts = text_splitter.split_text(transcription)
    docs = [Document(page_content=t) for t in texts]
    map_prompt_template = """
                      Write a summary of this chunk of text that includes the main points and any important details.
                      {text}
                      """

    map_prompt = PromptTemplate.from_template(map_prompt_template)
    map_chain = LLMChain(llm=llm, prompt=map_prompt)
    reduce_template = """The following is set of summaries:
        {docs}
        Take these and distill it into a final, consolidated summary of the main themes. 
        Helpful Answer:"""
    reduce_prompt = PromptTemplate.from_template(reduce_template)

    combine_prompt_template = """
                        Write a concise summary of the following text delimited by triple backquotes.
                        Return your response in bullet points which covers the key points of the text.
                        ```{text}```
                        BULLET POINT SUMMARY:
                        """

    combine_prompt = ChatPromptTemplate.from_template(template=combine_prompt_template)
    chain = load_summarize_chain(
        llm,
        chain_type="map_reduce",
        map_prompt=map_prompt,
        combine_prompt=combine_prompt,
        return_intermediate_results=True,
    )
    result = chain.run({"text": transcription})
    print(result)
    return result


def summarize_transcript(transcription: str, video_title=None):
    prompt = ChatPromptTemplate.from_template("tell me a joke about {foo}")
    model = ChatOpenAI()
    chain = prompt | model


def map_reduce_summarize_text(input, video_title=None):
    try:
        llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-16k")
        text_splitter = CharacterTextSplitter()
        texts = text_splitter.split_text(input)
        docs = [Document(page_content=t) for t in texts]
        chain = load_summarize_chain(llm, chain_type="map_reduce")
        return chain.run(docs)
    except Exception as e:
        return f"An error occured: {e}"


def summarize_with_gpt_4(input, video_title=None):
    human_message_promp_template = """
    Below is a transcript of an audio file delimited by <t> tags:
    ---
    <t>
    # TRANSCRIPT
    {transcript}
    # END TRANSCRIPT
    </t>
    --- 
    You task is to give a detailed summary of what the video talks about. We are going to repurpose this transcript and its contents into other content so try to extract from the transcript what is the main point of the video too. Begin!


    """
    try:
        human_message_prompt = human_message_promp_template.format(transcript=input)
        formatted = {"role": "user", "content": human_message_prompt}
        result = client.chat.completions.create(
            model="gpt-4-1106-preview", messages=[formatted]
        )
        print(result)
        return result.choices[0].message.content
    except Exception as e:
        return f"An error occured: {e}"
