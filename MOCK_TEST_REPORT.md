# Mock 测试报告与设计修订记录

## 1. Mock 测试目的

在正式实现前，先用 mock 测试验证设计中的接口、帧结构、同步流程和端到端链路是否可行。mock 测试重点不是追求最终性能，而是提前发现设计风险、缺陷和接口不一致问题。

## 2. Mock 测试场景

### Mock 1：UTF-8 源编码可逆性

- 目标：验证中文文本经过 Source Encode 和 Source Decode 后能完全恢复。
- 方法：使用包含中文标点的课程描述文本，转为 bitstream 后再转回字符串。
- 结果：要求恢复文本与原文完全一致，且 bitstream 长度为 8 的整数倍。
- 设计影响：确认 length 字段应记录源编码后的原始 payload bit 数，而不是 QPSK padding 后长度。

### Mock 2：奇数 bit 长度与 QPSK padding

- 目标：验证 payload bit 数为奇数时不会破坏 Frame Build / Frame Parse。
- 方法：构造 255 bit 随机 payload，封装、QPSK 调制、无噪声解调、解析。
- 结果：接收端根据 length 和 payload_length 字段恢复有效 payload，忽略调制补零。
- 发现的问题：如果只记录 payload 字节数，奇数 bit payload 会在恢复时歧义。
- 修订内容：DESIGN.md 中加入明确的 bit 级 length 字段，并在帧中增加 payload_length 字段辅助解析。

### Mock 3：前导相关同步

- 目标：验证接收端不能假设帧从第 0 个符号开始。
- 方法：在帧前加入 25 个随机符号，对接收序列和已知 preamble 做相关检测。
- 结果：SNR 12 dB 下同步误差应不超过 1 个符号。
- 风险：短 preamble 在噪声较强时可能出现错误峰值。
- 修订内容：将 preamble 设计为 64 bit，即 32 个 QPSK 符号，并输出 `sync_peak.png` 便于分析。

### Mock 4：AWGN 固定 seed 复现

- 目标：验证公开测试和隐藏测试可复现。
- 方法：对固定 QPSK 符号序列用相同 seed 添加 AWGN 两次。
- 结果：两次输出在数值容差内一致。
- 修订内容：所有随机过程均从 CLI 的 `--seed` 派生，metrics 中记录 seed 和随机同步偏移。

## 3. 设计风险或缺陷

主要风险包括：

- 帧头字段如果在低 SNR 下出错，会导致 payload 长度解析失败。
- 3 次重复码纠错能力有限，低 SNR 下仍可能产生误码。
- CRC32 只能检测错误，不能恢复错误。
- 如果实现中直接复制 `Test.txt` 到 `received.txt`，虽然端到端文本一致，但违反 PRD 和 TC-T-020。

## 4. DESIGN.md 修订记录

- 修订 1：明确 `length` 字段表示 Source Encode 后、Scramble 前的原始 payload bit 数。
- 修订 2：增加 `payload_length` 字段，使 Channel Encode 后的帧内 payload 可以被准确解析。
- 修订 3：明确 QPSK Gray 映射和单位功率归一化方式。
- 修订 4：明确 SNR 定义为调制符号平均功率与复高斯噪声平均功率之比。
- 修订 5：增加低 SNR 失败原因分析，要求 metrics 记录 `failure_reason`。

## 5. 结论

mock 测试表明该设计能够覆盖公开测试的基础功能，并能解释主要通信模块。根据 mock 发现的问题，DESIGN.md 已完成相应修改，最终实现采用 PN 扰码、3 次重复码、CRC32 帧校验、Gray QPSK、AWGN 和前导相关同步。
