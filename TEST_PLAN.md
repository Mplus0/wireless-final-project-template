# 测试计划

## 1. 测试目标

测试计划覆盖 PRD 和公开测试集中的核心要求，验证系统能完成 `Test.txt -> results/received.txt` 的端到端无线基带仿真，并能输出指标和图表。

## 2. 单元测试计划

| 编号 | 模块 | 测试内容 | 期望结果 |
|---|---|---|---|
| UT-01 | Source Encode / Source Decode | 中文 UTF-8 文本转 bitstream 后再恢复 | 文本完全一致，bit 长度为 8 的整数倍 |
| UT-02 | Encrypt/Scramble | 固定 seed 扰码再解扰 | bitstream 完全一致 |
| UT-03 | Channel Encode / Channel Decode | 无噪声重复码编码译码 | bitstream 完全一致 |
| UT-04 | Frame Build / Frame Parse | 随机 payload 封装解析 | payload、length 和 checksum_pass 正确 |
| UT-05 | QPSK Modulate | 输入 00、01、11、10 | 分别落入第一、第二、第三、第四象限 |
| UT-06 | QPSK Demodulate | 无噪声调制解调 | bitstream 完全一致 |
| UT-07 | Channel | 固定 seed AWGN 运行两次 | 输出数值可复现 |
| UT-08 | Synchronization | 前置 25 个随机符号 | 检测误差不超过 1 个符号 |

## 3. 集成测试计划

| 编号 | 场景 | 输入参数 | 期望结果 |
|---|---|---|---|
| IT-01 | 公开基础运行 | `--snr 12 --seed 2026 --mod qpsk --channel awgn` | 正常退出，生成 `received.txt` 和 `metrics.json` |
| IT-02 | 端到端恢复 | 中文 `Test.txt` | `received.txt` 与输入完全一致 |
| IT-03 | 图表生成 | 同 IT-01 | 至少生成 `constellation.png`、`ber_curve.png`、`sync_peak.png` 中两项 |
| IT-04 | 低 SNR 行为 | `--snr 2` | 程序不崩溃，输出 BER、FER、text_match_rate 和失败原因 |
| IT-05 | 不同 seed | `--seed 1/2026/4096` | AWGN 和前置偏移可复现，程序正常运行 |

## 4. 公开测试映射

- TC-T-001 到 TC-T-003：检查提交物、DESIGN.md 和 MOCK_TEST_REPORT.md。
- TC-T-004：验证 Source Encode / Source Decode。
- TC-T-005 到 TC-T-006：验证 Frame Build / Frame Parse。
- TC-T-007：验证 Encrypt/Scramble 可逆。
- TC-T-008：验证 Channel Encode / Channel Decode。
- TC-T-009 到 TC-T-011：验证 QPSK 映射、解调和 padding。
- TC-T-012：验证 AWGN 固定 seed。
- TC-T-013：验证 Synchronization。
- TC-T-014 到 TC-T-017：验证 CLI、metrics、端到端恢复和图表。
- TC-T-018 到 TC-T-020：验证 AI_LOG、结果分析和反直接复制。

## 5. 运行命令

安装依赖：

```bash
pip install -r requirements.txt
```

公开测试：

```bash
pytest public_tests -q
```

端到端手工测试：

```bash
python main.py --input Test.txt --output results/received.txt --snr 12 --seed 2026 --mod qpsk --channel awgn
```

检查输出：

```text
results/received.txt
results/metrics.json
results/constellation.png
results/ber_curve.png
results/sync_peak.png
```
