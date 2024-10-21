from openai import OpenAI
from http import HTTPStatus
import dashscope
import colorama
import sys
import json
colorama.init()

dashscope.api_key = "sk-cb45636db397409f8efbb0fb764b0874"

def print_colored(text, color, is_visual=True):
    if is_visual:
        print(getattr(colorama.Fore, color.upper()) + text + colorama.Fore.RESET)

def create_client(model, api_key, base_url):
    try:
        return OpenAI(api_key=api_key, base_url=base_url)
    except Exception as e:
        print_colored(f"Error creating client for {model}: {e}", "RED", True)
        return None

def handle_dashscope_model(model, question, msg, is_visual=True):
    messages = [{'role': 'system', 'content': 'You are a helpful assistant.'}]
    messages.extend(msg) if msg else messages.append({'role': 'user', 'content': question})
    
    try:
        response = dashscope.Generation.call(
            model=model,
            messages=messages,
            result_format='message',
        )
        if response.status_code == HTTPStatus.OK:
            return response.output['choices'][0]['message']['content']
        else:
            print_colored(f'Request failed: {response.status_code}, {response.code}, {response.message}', "RED", True)
    except Exception as e:
        print_colored(f"Error with dashscope model: {e}", "RED", True)
    return None

def llm_api(question, model="deepseek-chat", temperature=0.7, msg=None, is_visual=True):
    '''
    arguments:
    question: string
    model: deepseek-chat, Qwen, llama3.1, GPT4o, Baichuan4, qwen-max, qwen-plus, GLM-4, GLM-4-Flash, llama3-8b-instruct
    temperature: 0.7
    msg: [{"role": "user", "content": "你好"}, {"role": "assistant", "content": "你好呀"}]
    is_visual: boolean, default True
    '''
    if is_visual:
        print_colored(f"\n-----------{model}---------\n", "YELLOW")
        print_colored(f"Question: {question}", "BLUE")

    client = None
    if model == "deepseek-chat":
        deepseek_list = ['sk-5d3680cbdca64fc1af04d21617fe104e', 'sk-53d4d5d9be4c4ad39eaa49c9326c8320', 'sk-029ef31805dc4a2e944e89a161367a8e', 'sk-6b5c25f704af49a690652befcdc0a541', 'sk-d7f5a176ad7546429ca5c9681c81b899', 'sk-5d3680cbdca64fc1af04d21617fe104e', 'sk-6b5c25f704af49a690652befcdc0a541', 'sk-739b33c3782249acb8f258f8a905b964', 'sk-d7f5a176ad7546429ca5c9681c81b899', 'sk-36119dc49cd846daa3e641222aea6b14', 'sk-c1ece558bdf3469099b52a63be9a6803', 'sk-be93207081af4f60a4a84f073e409bd8', 'sk-e92fee47f85845d6aa6a2de8fbea4b23', 'sk-36119dc49cd846daa3e641222aea6b14', 'sk-029ef31805dc4a2e944e89a161367a8e', 'sk-dbfe46812522413b8a85f450bdba3525', 'sk-e8224e2c0d194e91a2830bb8893cf3c3', 'sk-7885a3110d2646f0bfb7e8a5732045fe', 'sk-be93207081af4f60a4a84f073e409bd8', 'sk-c1ece558bdf3469099b52a63be9a6803', 'sk-e92fee47f85845d6aa6a2de8fbea4b23', 'sk-7885a3110d2646f0bfb7e8a5732045fe', 'sk-573ab2d3d0c4452cb7cb190d130bd1e0', 'sk-573ab2d3d0c4452cb7cb190d130bd1e0','sk-ed6548a7a33541e2b4d0dce50de5f64a']
        for key in deepseek_list:
            client = create_client(model, key, "https://api.deepseek.com")
            if client:
                break
    elif model in ["GLM-4", "GLM-4-Flash"]:
        client = create_client(model, "257adc3075c5f755314974b7b81c6a8f.IXlsqeqHsffGNqEi", "https://open.bigmodel.cn/api/paas/v4/")
    elif model == "Baichuan4":
        client = create_client(model, "sk-6a2d8920e740fbeed084813975e2e25f", "https://api.baichuan-ai.com/v1/")
    elif model in ["qwen-max", "qwen-plus"]:
        client = create_client(model, "sk-cb45636db397409f8efbb0fb764b0874", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    elif model in ["qwen2-72b-instruct", "llama3__1-70b-instruct", "reflection-llama-3___1-70b", "reflection-70b", "llama3.1"]:
        model = "reflection-llama-3___1-70b" if model == "reflection-70b" else "llama3__1-70b-instruct" if model == "llama3.1" else model
        client = create_client(model, "EMPTY", "http://82.157.171.144:6374/v1")
    elif model in ["gpt-4o-mini", "gpt-4o"]:
        gpt_list = ['sk-3sAIcSk9UWxVcOglj5xTy0Lr8EIrHtUaQ5j7M1c22bkVS3cq', 'sk-Swi6dHHVWDY342vVaCwFLwmguz6YXfVlSXAfNxzukMtsScfP', 'sk-6ktjARpTQuanwCV3s8qTwzCeXe2orB7UZgz80Jy6N3bUBEma']
        for key in gpt_list:
            client = create_client(model, key, "https://api.chatanywhere.tech/v1")
            if client:
                break
    elif model == "llama3.1-405b-instruct":
        return handle_dashscope_model(model, question, msg, is_visual)
    else:
        print_colored(f"{model} is not supported!", "RED", True)
        return None

    if not client:
        print_colored("Failed to create a client for any available API key.", "RED", True)
        return None
    
    try:
        messages = msg if msg else [{"role": "user", "content": question}]
        chat_completion = client.chat.completions.create(
            messages=messages,
            temperature=temperature,
            model=model,
            max_tokens=4096
        )
        response = chat_completion.choices[0].message.content
        if is_visual:
            print_colored(f"Response: {response}", "GREEN")
        try:
            response = json.loads(response)
        except:
            if response.startswith("```json"):
                response = response[7:-3]
                response = json.loads(response)
            else:
                pass
        return response
    except Exception as e:
        print_colored(f"Error during API call: {e}", "RED", True)
        return None

# Example usage:
# msg = [{"role": "user", "content": "你好呀,我是eddie"}, {"role": "assistant", "content": "你好呀"}, {"role": "user", "content": "我叫什么名字"}]
# llm_api("你好", model="qwen2-72b-instruct", temperature=0.7, msg=msg, is_visual=True)