# MemoryLink应用说明

本文档面向**部署、使用与集成**：如何运行 Web应用、配置环境变量、调用 HTTP API，以及各记忆模式在界面与接口中的含义。不含研究命题与工程实施清单。

---

## 应用是什么

MemoryLink 是一个可运行的 Web 应用：在**同一套对话流程**下，可在六种记忆策略之间切换，对比助手在多轮对话中的上下文组织方式。包含：

- **后端**：FastAPI，提供对话、记忆检视、清空与基准跑分接口
- **前端**：Next.js，聊天、记忆状态展示、基准结果展示
- **模型**：配置 OpenAI API 时使用真实模型回复；未配置或调用失败时使用本地占位回复，便于离线演示接口与记忆管线

---

## 功能概览

| 能力 | 说明 |
|------|------|
| 多轮对话 | 按 `session_id` 区分会话，同一会话内记忆持续累积 |
| 记忆模式切换 | 六种 `system` 标识对应六种记忆实现，切换后仅影响后续写入与检索逻辑 |
| 记忆检视 | 查看当前会话在某套记忆下的内部状态（结构化 JSON） |
| 清空记忆 | 按 `system` + `session_id` 清空该组合下的记忆 |
| 基准跑分 | 一键对六种系统在相同用例上跑分并返回汇总（依赖后端评测逻辑与可选 LLM） |

---

## 本地运行

### 后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --reload
```

默认监听 `http://127.0.0.1:8000`。服务文档：`http://127.0.0.1:8000/docs`（Swagger）。

### 前端

```bash
cd frontend
npm install
npm run dev
```

若后端不是本机 8000 端口，设置：

```bash
export NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

---

## 环境变量（后端）

在 `backend` 目录创建 `.env`（可参考 `.env.example`）：

| 变量 | 说明 |
|------|------|
| `OPENAI_API_KEY` | OpenAI API 密钥；为空则不走真实模型，使用占位回复 |
| `MEMORYLINK_MODEL` | 模型名，默认 `gpt-4o-mini` |
| `MEMORYLINK_USE_REAL_LLM` | `true` / `false`，为 `false` 时即使配置了 Key 也使用占位回复 |

---

## 记忆模式（应用侧说明）

请求体或查询参数中的 `system` 必须为下列之一：

| `system` | 用户可见含义 |
|----------|----------------|
| `m1-short-long` | 近期对话窗口 + 长期摘要/向量检索类长期记忆 |
| `m2-episodic` | 按事件与时间线组织，带情绪等标签的情节记忆 |
| `m3-semantic` | 从对话中抽取事实关系，便于按“知识”检索 |
| `m4-procedural` | 偏好与行为规则类记忆，影响系统侧指令组合 |
| `m5-working` | 带重要性评分的工作集，容量有限时优先保留重要内容 |
| `m6-hierarchical` | 多层压缩（细粒度到会话级/画像级），按需展开上下文 |

同一 `session_id` 下，不同 `system` 使用各自独立的记忆实例（后端中为不同引擎对象），切换模式不会自动合并历史。

---

## HTTP API

### `GET /health`

健康检查。

**响应示例**

```json
{ "status": "ok" }
```

---

### `POST /chat`

发送用户消息，写入记忆、检索上下文、生成助手回复并再次写入记忆。

**请求体**（JSON）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `system` | string | 否 | 默认 `m1-short-long`，取值见上表 |
| `session_id` | string | 否 | 默认 `default` |
| `user_message` | string | 是 | 非空 |

**响应**（JSON）

| 字段 | 说明 |
|------|------|
| `system` | 使用的记忆模式 |
| `session_id` | 会话 ID |
| `reply` | 助手回复正文 |
| `recalled` | 本轮用于拼上下文的检索结果列表（结构化） |
| `summary` | 记忆摘要及 LLM 状态（如是否启用真实模型、模型名） |

---

### `GET /memory/inspect`

查看指定记忆模式与会话下的内部状态（供调试与前端「记忆面板」）。

**查询参数**

| 参数 | 必填 | 说明 |
|------|------|------|
| `system` | 是 | 记忆模式 ID |
| `session_id` | 否 | 默认 `default` |

**响应**（JSON）

| 字段 | 说明 |
|------|------|
| `system` | 记忆模式 |
| `session_id` | 会话 ID |
| `state` | 各引擎自定义的字典结构 |

---

### `POST /memory/clear`

清空指定记忆模式与会话的记忆。

**请求体**（JSON）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `system` | string | 是 | 记忆模式 ID |
| `session_id` | string | 否 | 不传则按各引擎约定处理（可能为全局或默认会话） |

**响应示例**

```json
{ "status": "cleared" }
```

---

### `GET /benchmark`

对六种记忆系统运行内置基准并返回汇总结果。

**响应**（JSON）

| 字段 | 说明 |
|------|------|
| `systems` | 列表，每项对应一种记忆系统的分数与明细（结构以后端 `BenchmarkResponse` 为准） |

注意：完整跑分可能较慢，且部分评分依赖 LLM；无 Key 时行为以后端实现为准。

---

## 前端与 API 对应关系

前端 `frontend/src/lib/api.ts` 已封装：

- `sendChat(system, sessionId, userMessage)` → `POST /chat`
- `inspectMemory(system, sessionId)` → `GET /memory/inspect`
- `runBenchmark()` → `GET /benchmark`

---

## 依赖与数据位置

- **Python依赖**：见 `backend/requirements.txt`
- **Node 依赖**：见 `frontend/package.json`
- 各记忆引擎可能在本机写入 SQLite、向量库等数据目录；清理数据时除调用 `/memory/clear` 外，可按需删除后端工作目录下的数据文件（具体路径以实现为准）

---

## 与《设计方案》文档的区别

- [ai-memory-systems-lab-design.md](./ai-memory-systems-lab-design.md)：架构设想、研究命题、目录规划与评测维度设计。
- **本文**：如何把 MemoryLink **当作应用**跑起来、如何配置、如何调接口、各模式在参数层面的含义。
