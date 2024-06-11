from openai import OpenAI
import os


client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "<key>"))

docker = ""
system_prompt = """
You are a security researcher, expert in detecting security vulnerabilities. Carefully analyze the given code snippet and track the data flows from various sources to sinks. 
Assume that any call to an unknown external API is unsanitized. Please provide a response only in the following format: Here is a data flow analysis of the given code snippet: 
A. Sources: <numbered list of input sources> 
B. Sinks: <numbered list of output sinks> 
C. Sanitizers: <numbered list of sanitizers, if any> 
D. Unsanitized Data Flows: <numbered list of data flows that are not sanitized in the format (source, sink, why this flow could be vulnerable)> 
E. Vulnerability analysis verdict: vulnerability: <YES or NO> | vulnerability type: <CWE_ID> | vulnerability name: <NAME_OF_CWE> | explanation: <explanation for prediction>
"""

with open("DockerRegistryEndpoint.txt") as file:
    docker = file.read()

print(docker)

MODEL = "gpt-4o"
response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Is the following code snippet prone to CWE-78 (respond using the framework above)?" + "\n\n" + docker},
    ],
    temperature=0,
)

print(response.choices[0].message.content)