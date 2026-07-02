# AI 辅助编程日志

## 交互 1

- Prompt：请阅读当前文件夹内容，根据 PRD、README 和公开测试整理需要完成的内容。
- AI 生成内容：梳理了必须提交的文档、代码目录、统一 CLI、metrics 字段、QPSK/AWGN/同步等要求。
- 人工修改：保留了需求清单，但决定按课程项目形式继续补齐完整代码，而不是只做摘要。
- 采纳理由：该输出准确对应 PRD 和公开测试，有助于确定开发范围。

## 交互 2

- Prompt：请将本次项目划分成多个阶段，然后逐步完成全部内容。
- AI 生成内容：给出阶段计划，包括需求固化、文档、核心模块、CLI、结果生成和公开测试修复。
- 人工修改：将实现方案限定为 PN 扰码、3 次重复码、CRC32 帧、Gray QPSK、AWGN 和前导相关同步，避免引入过复杂扩展。
- 采纳理由：该方案满足 Level 2 要求，且代码逻辑适合答辩解释。

## 交互 3

- Prompt：根据公开测试函数名实现可导入模块。
- AI 生成内容：生成 `src/source.py`、`src/framing.py`、`src/modulation.py`、`src/channel.py`、`src/synchronization.py` 等模块。
- 人工修改：对接口命名、metrics 字段和图表生成做了约束，确保与公开测试和 PRD 一致。
- 采纳理由：公开测试会通过模块名和函数名自动发现函数，因此接口稳定比内部复杂度更重要。

## 交互 4

- Prompt：运行公开测试并根据失败结果修复。
- AI 生成内容：根据 pytest 输出定位失败项，修复帧解析、同步、CLI 输出或文档关键词问题。
- 人工修改：保留通过测试所需的最小修复，同时避免直接复制输入文件到输出文件。
- 采纳理由：测试驱动修复可以减少隐藏问题，并保留真实无线链路处理流程。

## 最终采纳说明

本项目使用 AI 辅助完成需求整理、文档草稿、模块代码和测试修复。人工重点检查了通信链路是否真实经过 Source Encode、Scramble、Channel Encode、Frame Build、QPSK、AWGN、Synchronization、QPSK Demodulate、Channel Decode、Descramble 和 Source Decode，拒绝任何直接复制 `Test.txt` 到 `received.txt` 的捷径。最终采纳的代码以可解释、可复现、能通过公开测试为主要标准。
