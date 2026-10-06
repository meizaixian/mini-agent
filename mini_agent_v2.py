from openai import OpenAI
import json
from datetime import datetime

client = OpenAI(
    api_key="sk-你的KEY（上传前请替换成自己的）",
    base_url="https://api.deepseek.com"
)

# ========== ① 工具函数（Day 5 已写，原样保留）==========
def calculator(expression):
    expr = expression.replace("×", "*").replace("÷", "/").replace(" ", "")
    result = eval(expr)
    return str(result)


def get_time():
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


def get_weather(city):
    return f"{city}今天多云，气温25℃，适合出门"


# ========== ② 工具说明书（Day 5 已写，原样保留）==========
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
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "获取当前时间，返回年月日时分秒",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询某城市的天气情况",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名，如 '广州'"}
                },
                "required": ["city"]
            }
        }
    }
]

# ========== ③ Day 6 新增：上下文管理 ==========
MAX_TOKENS = 1500

# TODO 6-1：estimate_tokens —— 估算 messages 里所有消息的总 token 数
# 提示：遍历 messages，每条取 m["content"]，用 len() 求长度，累加起来返回
def estimate_tokens(messages):
    total=0
    for m in messages:
        total+=len(m["content"])
    return total


messages = [
    {"role": "system", "content": "你是一个会用工具的助手。需要计算时用 calculator，需要时间时用 get_time，需要天气时用 get_weather。"}
]

print("Agent 已启动（上下文管理版），输入'退出'结束对话")

# ========== ④ 多轮对话主循环 ==========
while True:
    user_input = input("你：")
    if user_input == "退出":
        print("再见！")
        break

    messages.append({"role": "user", "content": user_input})

    # TODO 6-2：截断——只要超限且还有可删的消息（只剩system时停手），就删最旧的
    # 提示：del messages[1] 会删掉第2条（index 0 是 system，永远保留）
    # 写法：while estimate_tokens(messages) > MAX_TOKENS and len(messages) > 2:
    #          del messages[1]
    while estimate_tokens(messages)>MAX_TOKENS and len(messages)>2:
        del messages[1]

    # 内层：Agent 工具循环（Day 5 逻辑，自己敲进来）
    while True:
        resp = client.chat.completions.create(model="deepseek-chat", messages=messages, tools=tools)
        msg = resp.choices[0].message
        if msg.tool_calls:
            messages.append(msg.model_dump())
            # TODO 6-3：把 Day 5 的 for + if/elif 分派敲进来（calculator/get_time/get_weather）
            for tc in msg.tool_calls:
                print(f"模型点名：{tc.function.name},参数：{tc.function.arguments}")
                tool_name=tc.function.name
                args=json.loads(tc.function.arguments)
                if tool_name=="calculator":
                    result=calculator(args["expression"])
                elif tool_name=="get_time":
                    result=get_time()
                elif tool_name=="get_weather":
                    result=get_weather(args["city"])
                messages.append({"role":"tool","tool_call_id":tc.id,"content":result})
                print(f"工具{tool_name}返回{result}")
        else:
            print("AI：", msg.content)
            break
