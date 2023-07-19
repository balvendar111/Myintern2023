
import openai
import PyPDF2
import uvicorn
import docx2txt
import tempfile
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from langchain.memory import ConversationBufferMemory
from langchain import OpenAI, LLMChain, PromptTemplate

app = FastAPI()

# CORS policy
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openai.api_key = "OPENAI_API_KEY"

class Chat(BaseModel):
    role: str
    message: str

template_mapping = {
  "AWS":'''Pretend like you are an AWS Cloud expert  and just provide me the data with actual number of hardware details, also give responses in seperate short and concise bullet points only this is important. Provide the software and hardware configuration details separately with numbers associated for hardware and software details so that the user can implement that in their respective systems  all in bullet points only, If asked for multiple systems then give the result separatly for each sysytems also give the specificed cost for all services and optimize it to reduce costs in month and provide these costs and and its uses so that the user can directly implement it in their system if not accessed for long duration of time then give suggestion that for your use this is not the appropriate instance created and  please use a different instacnce where you will save your cost that and only give answer related to AWS cloud not
   give answer related to another cloud like GCP, AZURE. \n\n.
{AWS_chat_history}
User: {input}
AWS:''',

"AWS_ec2":'''Pretend like you are aws expert and compare the two json array seperated by the '+' sign suggested that if the second system is not viable then tell me the updated instance types details  which will be atleast minimum requirements for the first systems provided  and when giving the response rename  the second system as the modified system and if not viable tell me the updated system or hardware details along with alert message that you cannot change the instance types your system have minium requirement of telling  instances vpcus,memory and cpu utilization and also tell me the updated costs in small and concise bullet points this is important.
{AWS_ec2_history}
User: {input}
AWS_ec2:''',

 "AWS_s3bucket":'''Pretend like you are aws expert and give suggestion that to which storage class it can change according to last access days and if changing storage class from one to another according to last access days  does not impact the file stored in S3 bucket then say yes you can change the storage class and if there is impact for any storage class if changed then warn the user by giving alert message that you can change you storage class till some threshold if changes then your file may get impact give message in bullet points for each buckets listed.\n\n.
{AWS_s3bucket_history}
User: {input}
AWS_s3bucket:''',

"AWS_rds":'''Pretend like you are aws expert and compare the two json array seperated by the '+' sign suggested that if the second system is not viable then tell me the updated instance types details  which will be atleast minimum requirements for the first systems provided  and when giving the response rename  the second system as the modified system and if not viable tell me the updated system or hardware details along with alert message that you cannot change the instance types your system have minium requirement of telling  instances vpcus,memory and cpu utilization and also tell me the updated costs in small and concise bullet points this is important. \n\n.
{AWS_rds_history}
User: {input}
AWS_rds:''',

 "AWS_cost_optimization":'''Pretend like you are an AWS cost optimization expert provide me the details of the threshold system which can be created with the given values individually for every index of the array just provide me the most reduced system   and the system should be such that below those configurations my system would fail it should be the most reduced one  and the details should be provided in bullet points  \n.
{AWS_optimization_history}
User: {input}
AWS_cost_optimization:''',

"AWS_cost_reduction": '''Pretend like you are an AWS reduction expert and give response as a json with same keys   for every value of the json array please this is important it should be only one valid json array with keys and values being strings and  such as if the instance or a storage class is a reduced one the key should be mentioned as a reducedKey in this dont change the instanceId or the bucketName dont change the value only the key should be mentioned as reducedClass or reducedInstance  and values of all keys must be strings and it should have the optimized costs and reduction also  according to that and reduce resources upto some threshold according to actual user data  and compare the reduced and original values so that the user can have a perspective on what extra resources of the  cloud they are using not in terms of cost and suggested the user the reduced methods ,  \n.
{AWS_reduction_history}
User: {input}
AWS_cost_reduction:''',

   "GCP": '''Pretend like you are an Googale Cloud expert  and just provide me the data with actual number of hardware details, also give responses in seperate short and concise bullet points only this is important. Provide the software and hardware configuration details separately with numbers associated for hardware and software details so that the user can implement that in their respective systems  all in bullet points only, If asked for multiple systems then give the result separatly for each sysytems also give the specificed cost for all services and optimize it to reduce costs in month and provide these costs and and its uses so that the user can directly implement it in their system if not accessed for long duration of time then give suggestion that for your use this is not the appropriate instance created and  please use a different instacnce where you will save your cost that and only give answer related to Googale cloud not
   give answer related to another cloud like AWS, AZURE. \n\n.
{GCP_chat_history}
User: {input}
GCP:''',

   "AZURE": '''Pretend like you are an Azure Cloud expert  and just provide me the data with actual number of hardware details, also give responses in seperate short and concise bullet points only this is important. Provide the software and hardware configuration details separately with numbers associated for hardware and software details so that the user can implement that in their respective systems  all in bullet points only, If asked for multiple systems then give the result separatly for each sysytems also give the specificed cost for all services and optimize it to reduce costs in month and provide these costs and and its uses so that the user can directly implement it in their system if not accessed for long duration of time then give suggestion that for your use this is not the appropriate instance created and  please use a different instacnce where you will save your cost that and only give answer related to AZURE cloud not
   give answer related to another cloud like GCP, AWS \n\n.
{AZURE_chat_history}
User: {input}
AZURE:''',
}

memory_mapping = {
   "AWS": ConversationBufferMemory(memory_key="AWS_chat_history"),
   "AWS_ec2": ConversationBufferMemory(memory_key="AWS_ec2_history"),
   "AWS_s3bucket": ConversationBufferMemory(memory_key="AWS_s3bucket_history"),
   "AWS_rds": ConversationBufferMemory(memory_key="AWS_rds_history"),
   "AWS_cost_optimization": ConversationBufferMemory(memory_key="AWS_optimization_history"),
   "AWS_cost_reduction": ConversationBufferMemory(memory_key="AWS_reduction_history"),
   "GCP": ConversationBufferMemory(memory_key="GCP_chat_history"),
   "AZURE": ConversationBufferMemory(memory_key="AZURE_chat_history"),
}

llm_mapping = {
   "AWS": LLMChain(
       #llm=OpenAI(temperature=0.9, model="text-davinci-003", max_tokens=2500),
       llm=OpenAI(temperature=0.5, max_tokens=2000),
       prompt=PromptTemplate(input_variables=["AWS_chat_history", "input"], template=template_mapping["AWS"]),
       verbose=True,
       memory=memory_mapping["AWS"]
   ),
   "AWS_ec2": LLMChain(
       #llm=OpenAI(temperature=0.9, model="text-davinci-003", max_tokens=1500),
       llm=OpenAI(temperature=0.5, max_tokens=2000),
       prompt=PromptTemplate(input_variables=["AWS_ec2_history", "input"], template=template_mapping["AWS_ec2"]),
       verbose=True,
       memory=memory_mapping["AWS_ec2"]
   ),
   "AWS_s3bucket": LLMChain(
       #llm=OpenAI(temperature=0.9, model="text-davinci-003", max_tokens=1500),
       llm=OpenAI(temperature=0.5, max_tokens=2000),
       prompt=PromptTemplate(input_variables=["AWS_s3bucket_history", "input"], template=template_mapping["AWS_s3bucket"]),
       verbose=True,
       memory=memory_mapping["AWS_s3bucket"]
   ),
   "AWS_rds": LLMChain(
       #llm=OpenAI(temperature=0.9, model="text-davinci-003", max_tokens=1500),
       llm=OpenAI(temperature=0.5, max_tokens=2000),
       prompt=PromptTemplate(input_variables=["AWS_rds_history", "input"], template=template_mapping["AWS_rds"]),
       verbose=True,
       memory=memory_mapping["AWS_rds"]
   ),
    "AWS_cost_optimization": LLMChain(
       #llm=OpenAI(temperature=0.9, model="text-davinci-003", max_tokens=1500),
       llm=OpenAI(temperature=0.5, max_tokens=2000),
       prompt=PromptTemplate(input_variables=["AWS_optimization_history", "input"], template=template_mapping["AWS_cost_optimization"]),
       verbose=True,
       memory=memory_mapping["AWS_cost_optimization"]
   ), 
    "AWS_cost_reduction": LLMChain(
       #llm=OpenAI(temperature=0.9, model="text-davinci-003", max_tokens=1500),
       llm=OpenAI(temperature=0.5, max_tokens=2000),
       prompt=PromptTemplate(input_variables=["AWS_reduction_history", "input"], template=template_mapping["AWS_cost_reduction"]),
       verbose=True,
       memory=memory_mapping["AWS_cost_reduction"]
   ),
   "GCP": LLMChain(
       #llm=OpenAI(temperature=0, model="text-davinci-003", max_tokens=1500),
       llm=OpenAI(temperature=0.9, max_tokens=2000),
       prompt=PromptTemplate(input_variables=["GCP_chat_history", "input"], template=template_mapping["GCP"]),
       verbose=True,
       memory=memory_mapping["GCP"]
   ),
   "AZURE": LLMChain(
       #llm=OpenAI(temperature=0, model="text-davinci-003", max_tokens=1500),
       llm=OpenAI(temperature=0.9, max_tokens=1200),
       prompt=PromptTemplate(input_variables=["AZURE_chat_history", "input"], template=template_mapping["AZURE"]),
       verbose=True,
       memory=memory_mapping["AZURE"]
   ),
}

@app.post("/chat")
async def process(res: Chat):
   role = res.role
   
   text_data=res.message
   
   llm_chain = llm_mapping[role]
   return {"text": llm_chain.predict(input=text_data)}

 
# PORT
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5502)


