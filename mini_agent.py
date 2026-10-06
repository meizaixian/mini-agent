from openai import OpenAI
import json
from datetime import datetime  # ← 新 import：get_time 要用

client = OpenAI(
    api_key="sk-你的KEY（上传前请替换成自己的）",
    base_url="https://api.deepseek.com"
)

# ========== ① 工具函数 ==========
def calculator(expression):
    expr = expression.replace("×", "*").replace("÷", "/").replace(" ", "")
    result = eval(expr)
    return str(result)


# TODO 5-1：get_time —— 无参数，返回当前时间字符串
# 提示：datetime.now().strftime("%Y-%m-%d %H:%M:%S") 能返回 "2026-10-04 16:30:12"
def get_time():
    now=datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


# TODO 5-2：get_weather —— 接收城市名 city，返回模拟天气字符串
# 提示：f-string 写法 f"{city}今天多云，25°C"
def get_weather(city):
    return f"{city}今天多云，气温25℃，适合出门"


# ========== ② 工具说明书 ==========
tools = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "计算加减乘除等数学表达式",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "数学表达式，如 '23*45'"}
                },
                "required": ["expression"]
            }
        }
    },

    {
        "type":"function",
        "function":{
            "name":"get_time",
            "description":"获取当前时间，返回年月日时分秒",
            "parameters":{"type":"object","properties":{},"required":[]}
        }
    },

    {
        "type":"function",
        "function":{
            "name":"get_weather",
            "description":"查询某城市的天气情况",
            "parameters":{
                "type":"object",
                "properties":{"city":{"type":"string","description":"城市名，如'广州'"}},
                "required":["city"]
            }
        }
    }
]

# ========== ③ 主循环 ==========
messages = [
    {"role": "system", "content": "你是一个会用工具的助手。需要计算时用 calculator，需要时间时用 get_time，需要天气时用 get_weather。"},
    {"role": "user", "content": "现在几点了？顺便算一下 23×45"}
]

while True:
    resp = client.chat.completions.create(model="deepseek-chat", messages=messages, tools=tools)
    msg = resp.choices[0].message

    if msg.tool_calls:
        messages.append(msg)   # 点名记录只加一次（在循环外面）
        for tc in msg.tool_calls:
           tool_name=tc.function.name
           args=json.loads(tc.function.arguments)
           if tool_name=="calculator":
               result=calculator(args["expression"])
           elif tool_name=="get_time":
               result=get_time()
           elif tool_name=="get_weather":
               result=get_weather(args["city"])
           messages.append({"role":"tool","tool_call_id":tc.id,"content":result})
    else:                # 模型没调工具 = 它在直接回答
        print("AI：", msg.content)
        break
