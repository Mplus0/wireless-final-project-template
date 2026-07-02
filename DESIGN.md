# 无线通信期末项目设计文档

## 1. 系统目标

本项目实现一个端到端无线通信基带仿真系统，将 `Test.txt` 中的 UTF-8 文本通过发送端、AWGN 信道和接收端恢复为 `results/received.txt`。系统遵循 PRD 中的固定链路：

`Test.txt -> Source Encode -> Encrypt/Scramble -> Channel Encode -> Frame Build -> QPSK Modulate -> Channel -> Synchronization -> QPSK Demodulate -> Channel Decode -> Decrypt/Descramble -> Source Decode -> received.txt -> Metrics/Plots`

基础调制方式为 QPSK，信道为 AWGN。系统输出 `results/metrics.json`，并生成 QPSK 星座图、BER-SNR 曲线和同步相关峰值图。

## 2. 模块设计

### 2.1 Source Encode / Source Decode

`src/source.py` 负责源编码。发送端将 UTF-8 文本编码为 bytes，再按高位到低位展开为 bitstream。接收端按 8 bit 重组 bytes 并进行 UTF-8 解码。该模块保证中文文本可逆恢复，且 bitstream 长度为 8 的整数倍。

接口：

- `source_encode(text)` / `text_to_bits(text)`
- `source_decode(bits)` / `bits_to_text(bits)`

### 2.2 Encrypt / Scramble 与 Decrypt / Descramble

本系统采用 PN 序列 XOR 扰码，属于可逆的轻量 Encrypt/Scramble 处理。发送端使用固定 seed 生成伪随机 0/1 序列并与 payload bitstream 异或；接收端使用同一 seed 再异或一次恢复原始 bitstream。

接口：

- `scramble(bits, seed=2026)`
- `descramble(bits, seed=2026)`

### 2.3 Channel Encode / Channel Decode

信道编码采用 3 次重复码。`Channel Encode` 将每个 bit 重复 3 次；`Channel Decode` 对每 3 bit 分组做多数判决。该方案编码率为 1/3，牺牲传输效率换取 AWGN 下的抗噪能力，便于解释和测试。

接口：

- `channel_encode(bits)`
- `channel_decode(bits)`

### 2.4 Frame Build 与 Frame Parse

帧结构包含：

| 字段 | 长度 | 说明 |
|---|---:|---|
| preamble | 64 bit | 已知前导序列，用于 Synchronization |
| length | 32 bit | Source Encode 后、Scramble 前的原始 payload bit 数 |
| payload_length | 32 bit | 帧内 payload bit 数 |
| payload | 可变 | 本实现中为信道编码后的发送载荷 |
| CRC32 | 32 bit | 覆盖帧内 payload bitstream |

`length` 字段用于接收端去除 QPSK padding 和信道编码后的多余 bit，保证 UTF-8 文本恢复时长度准确。CRC32 用于判断帧内 payload 是否通过校验，并写入 `checksum_pass`。

接口：

- `build_frame(payload_bits, original_payload_length=None)`
- `parse_frame(frame_bits)`

### 2.5 QPSK Modulate / QPSK Demodulate

QPSK 采用 PRD 指定的 Gray 编码映射，并归一化为单位平均符号功率：

| bit pair | symbol |
|---|---|
| 00 | `(1+j)/sqrt(2)` |
| 01 | `(-1+j)/sqrt(2)` |
| 11 | `(-1-j)/sqrt(2)` |
| 10 | `(1-j)/sqrt(2)` |

若进入调制的 bit 数不是 2 的整数倍，调制器在尾部补 0；接收端依据帧字段恢复有效长度。

接口：

- `qpsk_modulate(bits)`
- `qpsk_demodulate(symbols)`

### 2.6 Channel

基础信道为 AWGN。SNR 定义为接收端调制符号平均功率与复高斯噪声平均功率之比，单位 dB。复噪声的实部和虚部独立同分布，单维方差为 `noise_power / 2`。固定 seed 保证公开测试和隐藏测试可复现。

接口：

- `awgn(symbols, snr_db=12, seed=2026)`
- `awgn_channel(symbols, snr_db=12, seed=2026)`

### 2.7 Synchronization

同步模块使用前导序列相关检测帧起点。接收端不知道随机前置偏移，先对接收符号序列和已知 QPSK preamble 做滑动相关，相关峰值最大的位置作为帧起点。该方法可处理 PRD 要求的 0 到 128 个 QPSK 符号随机偏移。

接口：

- `synchronize(received_symbols, preamble=None)`
- `detect_frame_start(received_symbols, preamble=None)`
- `find_preamble(received_symbols, preamble=None)`

## 3. 端到端流程

发送端：

1. 读取 `Test.txt`。
2. `Source Encode` 得到原始 payload bits。
3. 使用 seed 做 `Encrypt/Scramble`。
4. 对扰码结果做 `Channel Encode`。
5. 执行 `Frame Build`，记录原始 payload bit 数。
6. 执行 `QPSK Modulate`。
7. 加入可复现的随机前置偏移并通过 AWGN `Channel`。

接收端：

1. 通过 `Synchronization` 检测帧起点。
2. 对齐后执行 `QPSK Demodulate`。
3. 解析帧并检查 CRC。
4. 执行 `Channel Decode`。
5. 执行 `Decrypt/Descramble`。
6. 按 length 字段截断恢复 `Source Decode`。
7. 写出 `received.txt`、`metrics.json` 和图表。

## 4. Metrics

`results/metrics.json` 至少包含：

- `snr_db`
- `seed`
- `modulation`
- `channel`
- `payload_bits`
- `ber`
- `fer`
- `text_match_rate`
- `checksum_pass`
- `sync_start_index`

额外记录 `sync_offset_symbols`、`frame_bits`、`coded_bits`、`coding_rate`、`failure_reason` 等辅助分析字段。

## 5. 结果分析

QPSK 星座图应在四个象限聚类。SNR 较高时，AWGN 噪声较小，接收点靠近理想星座点，QPSK Demodulate 判决更稳定；SNR 较低时，噪声可能把符号推过 I/Q 判决边界，产生 bit error，随后导致 BER 上升、CRC 失败或 UTF-8 解码异常。

BER 或 `text_match_rate` 随 SNR 的变化体现了系统可靠性。高 SNR 下重复码多数判决可以修正少量误码，使 `text_match_rate` 接近 1.0；低 SNR 下同步峰值可能变弱，QPSK 判决错误增加，帧头或 payload 错误会造成失败。主要失败原因包括 AWGN 噪声过强、同步峰值误检、帧头 length 字段受损和重复码纠错能力不足。

## 6. 设计风险

- 3 次重复码编码率较低，传输效率不高。
- 帧头字段未单独加强保护，极低 SNR 下 length 或 payload_length 出错会影响解析。
- CRC32 只能检错不能纠错，低 SNR 下需要依赖信道编码降低误码。
- 前导相关同步在强噪声或短前导条件下可能出现错误峰值。

上述风险在 mock 测试后被记录，并通过较长 preamble、固定 seed、CRC 检查和 metrics 中的失败原因字段进行缓解。
