# MemoryLink

MemoryLink 是一个可运行的对比实验环境，用于比较六种 AI 记忆系统策略，包含：

- 基于 FastAPI 的后端，内置六种可切换的记忆引擎
- 跨会话召回与一致性检查的基准测试运行器
- 基于 Next.js 的前端，支持对话、记忆状态查看与基准结果展示
- 可选接入 OpenAI 生成回复；未配置密钥时使用本地确定性回退模式

## 界面预览

![AI 记忆系统实验室 — 对话、记忆检视与基准测试](./assets/imgs/main.png)

## 记忆系统

- `m1-short-long`：短期缓冲 + 长期摘要
- `m2-episodic`：带情绪与时间线标注的情节记忆
- `m3-semantic`：基于 SQLite 与图模型的事实抽取
- `m4-procedural`：规则提炼与偏好记忆
- `m5-working`：按重要性评分的工作集与归档
- `m6-hierarchical`：原始、片段、会话与个人档案等多层压缩

## 运行后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --reload
```

若设置了 `OPENAI_API_KEY`，后端会使用 `MEMORYLINK_MODEL` 调用真实大模型生成回复。  
若未设置密钥，则使用本地确定性回复生成器，实验环境仍可完整运行。

## 运行前端

```bash
cd frontend
npm install
npm run dev
```

若后端不是运行在 `http://127.0.0.1:8000`，请设置环境变量 `NEXT_PUBLIC_API_BASE_URL`。
