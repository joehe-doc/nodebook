# Phase 3 产出 · 服务命名表 v1

> **本表从 `docs/design.md` 第 3 章两张骨架图的源码中机械抽取**，不是另行命名。
> 抽取方式：`grep -oE "helios-[a-z0-9-]+" docs/design.md | sort -u`，再与 `design/02-decisions.md` 第 1.2 节交叉核对。
>
> **约束力**：Phase 4 起的所有图（时序图、状态机、服务依赖、数据链路、安全架构）与正文，**必须逐字使用本表名称**。
> 新增服务时先改本表、再画图。本表一经评审冻结不得重命名——Kafka topic、监控项、审计记录、IAM 应用注册都引用它。
>
> ⚠️ 本项目为 playbook 流程验证用途，约束为虚构但自洽。

---

## 1. 服务与部署单元（23 项）

### 1.1 自研微服务与边缘运行时（20 项）

| # | 规范名称 | 职责（一句话） | 部署形态 | SLA 档 | 能力域 | 出现于 |
|---|---|---|---|---|---|---|
| 1 | `helios-mqtt-broker` | MQTT 协议终结、认证、限流、桥接 Kafka；不承载业务逻辑 | ACK `pool-connect` · EMQX 集群 · 每 AZ ≥2 节点 | 99.95% | 1 | 图 3-1、3-2 |
| 2 | `helios-device-auth` | X.509 双向 TLS + 一机一密双轨、自建 CA 客户端、证书轮换与 OCSP 吊销 | ACK `pool-connect` | 99.95% | 1 | 图 3-1、3-2 |
| 3 | `helios-ingest-service` | 解码、时间戳修正、块级幂等去重、召测波形分流、背压反馈 | ACK `pool-connect` · 无状态水平扩 | 99.95% | 1+4 | 图 3-1、3-2 |
| 4 | `helios-edge-runtime` | **边缘网关进程**：采集解析、整站聚合、本地规则告警、≥72h 分级缓存、块级补传、双活连接、A/B 签名 OTA | **电站侧 ARM64 2C4G，非 ACK** | 边缘自治 | 2 | 图 3-1 |
| 5 | `helios-edge-manager` | 边缘控制面：配置与规则集编译下发、OTA 编排、**召测任务队列与令牌调度**、边缘台账 | ACK `pool-app` | 99.9% | 2+4 | 图 3-1、3-2 |
| 6 | `helios-stream-processor` | Flink 作业集：分钟/小时/日多级聚合、变化率、质量校验与缺口检测 | ACK `pool-app` · StatefulSet（有状态） | 99.9% | 4 | 图 3-1、3-2 |
| 7 | `helios-tsdb-writer` | 时序批量写入、攒批、优先级队列、背压 | ACK `pool-app` · KEDA 按 lag 弹性 | 99.9% | 4 | 图 3-1、3-2 |
| 8 | `helios-file-service` | 录波文件 OSS 直传的 STS 凭证签发、分片状态、文件元数据索引与查询 | ACK `pool-app` · 随召测峰值弹性 | 99.9% | 4 | 图 3-1、3-2 |
| 9 | `helios-data-lifecycle` | **所有保留策略的单点管理者**：13 月原始 / 5 年聚合 / 3 年审计、冷热分层、归档回捞、成本水位上报、每日核对"应删已删" | ACK `pool-app` · CronJob 批处理 · 低优先级 | 99% | 4+6 | 图 3-1、3-2 |
| 10 | `helios-alarm-engine` | Flink CEP 云端规则（跨站关联、长历史窗口）；规则用 broadcast state 热更新 | ACK `pool-app` · StatefulSet · 近无状态（状态外置 Redis） | 99.95% | 5 | 图 3-1、3-2 |
| 11 | `helios-alarm-service` | 告警台账、去重/抑制/分级、确认与闭环；**边缘直报告警的快路径终点** | ACK `pool-app` | **99.95%** | 5 | 图 3-1、3-2 |
| 12 | `helios-notify-dispatcher` | App 推送 / 短信 / 公司告警中心 Webhook 三通道适配；各自独立线程池、独立熔断、持久化重试队列 | ACK `pool-app` | **99.95%** | 5 | 图 3-1、3-2 |
| 13 | `helios-query-service` | 遥测查询：跨层路由、**降采样下推**、结果缓存 | ACK `pool-app` | **99.9%** | 7 | 图 3-1、3-2 |
| 14 | `helios-report-service` | 报表与批量导出（仅读聚合层） | ACK `pool-app` · **独立资源配额** | **99.9%** | 7 | 图 3-1、3-2 |
| 15 | `helios-asset-registry` | 电站-设备-点位三级拓扑、分组标签、生命周期状态机（低频写、强一致） | ACK `pool-app` | 99.9% | 3 | 图 3-1、3-2 |
| 16 | `helios-thing-model` | 物模型定义与版本、量纲换算、设备影子（期望态/上报态） | ACK `pool-app` · 与 #15 共享 RDS 实例不同 schema | 99.9% | 3 | 图 3-1、3-2 |
| 17 | `helios-access-control` | 公司 IAM 适配 + RBAC + 多租户 + 电站级数据范围，**统一鉴权决策点 PDP** | ACK `pool-app` | 99.95% | 8+7 | 图 3-1、3-2 |
| 18 | `helios-openapi-gateway` | 对外 API 网关：IAM 令牌校验、签名、限流、版本管理、H5 大屏数据出口、**北向数据订阅出口** | ACK `pool-connect` · **DMZ 子网** | 99.9% | 7 | 图 3-1、3-2 |
| 19 | `helios-audit-service` | 下行指令（重启/参数下发/OTA/召测）全量审计，≥3 年，防篡改，三权分立 | ACK `pool-app` + OSS WORM | 99.95% | 6 | 图 3-1、3-2 |
| 20 | `helios-observability` | 平台自身指标与链路追踪、设备在线率、数据完整率（由心跳与块序号缺口推导）、容量与成本水位 | ACK `pool-app` | 99.9% | 6 | 图 3-1、3-2 |

### 1.2 中间件形态部署单元（3 项，需独立命名以便容量与告警归属）

| # | 规范名称 | 内容 | 部署形态 | 出现于 |
|---|---|---|---|---|
| 21 | `helios-kafka-telemetry` | 遥测集群：`uplink.raw` / `telemetry.norm` / `recall.burst` / `block.late`；acks=1；8~12 台 NVMe；峰值 200MB/s、常态 6.8MB/s；**允许 lag 千万级** | ACK `pool-data` · 本地 NVMe · 跨 AZ 反亲和 | 图 3-1、3-2 |
| 22 | `helios-kafka-alarm` | 告警集群：`alarm.edge` / `alarm.fired` / `alarm.notify` / `cmd.down`；**acks=all · min.insync.replicas=2 · rack awareness**；3~5 台小规格；**零堆积容忍** | ACK `pool-data` | 图 3-1、3-2 |
| 23 | `helios-tsdb-cluster` | IoTDB 自建集群；3 副本跨 AZ；写入 quorum=2；L1 热层 90 天本地 NVMe；3~6 数据节点（**按稳态 66,700 样本/s +50% 建，非峰值**） | ACK `pool-data` | 图 3-1、3-2 |

> **托管服务不进本表**：RDS MySQL、Redis、OSS、ACK、SLS、云监控、RAM、SSL 证书服务、云防火墙、堡垒机、NLB/SLB、NAT、智能接入网关、VPN 网关——它们由阿里云 SLA 兜底，命名遵循云产品名，不需要冻结。
>
> **图 3-2 的图标约定本身携带信息**：`kubernetes.sts`/`deploy`/`cronjob` 图标 = 自建组件（高可用、备份、升级由我们负责）；阿里云产品图标 = 托管服务（云厂商 SLA 兜底）。Phase 4 画图请沿用此约定。

### 1.3 ACK 节点池（3 项）

| 规范名称 | 弹性模型 | 承载服务 | 关键约束 |
|---|---|---|---|
| `pool-connect` | **每 AZ 常驻 100% 容量** | #1 #2 #3 #18 | **禁用抢占式实例**；长连接扩容会触发重连风暴，事后扩容无效 |
| `pool-app` | HPA + KEDA（按 Kafka lag） | #5~#20 | 召测类消费者可用按量弹性节点组 |
| `pool-data` | **固定容量** | #21 #22 #23 | 本地 NVMe/ESSD，跨 AZ 反亲和打散 |

> 划分依据是**扩容时机**，不是服务分类。三类混在一个节点池里，任何一类的弹性策略都会伤害另外两类。

---

## 2. Kafka Topic 命名（8 项）

**规范全名 = `helios.<域>.<语义>`**，与服务名同构。

| 规范全名 | 所属集群 | 分区 | 保留 | 关键配置 | 用途 |
|---|---|---|---|---|---|
| `helios.uplink.raw` | telemetry | 128 | 24h | acks=1 · 单报文 ≤64KB | 边缘上行原始块 |
| `helios.telemetry.norm` | telemetry | 128 | 6h | acks=1 | 规范化遥测 |
| `helios.recall.burst` | telemetry | 64 | 3h | **独立 client 配额** | 召测突发流量 |
| `helios.block.late` | telemetry | 64 | 7d | **补传专道** | 72h 离线补传，不污染主链路 watermark |
| `helios.alarm.edge` | alarm | — | 7d | acks=all | 边缘已判定告警（快路径） |
| `helios.alarm.fired` | alarm | — | 7d | acks=all | 云端 CEP 产生的告警 |
| `helios.alarm.notify` | alarm | — | 7d | acks=all | 通知分发队列 |
| `helios.cmd.down` | alarm | — | 7d | acks=all | 下行指令 |

**统一约定**：分区键一律 `stationId`（保证同站有序 → 块级去重与状态局部性）；分区数一次设到终态（**分区只能扩不能缩**，128 分区的常态成本极低）。**文件不入 Kafka。**

### ⚠️ 2.1 已发现的命名漂移（Phase 3 抽取时拦下）

图 3-1 与 3-2 的节点标签中，8 个 topic **全部使用了缩写形式**（`uplink.raw`、`alarm.edge` 等），省略了 `helios.` 前缀；而 `02-decisions.md` 第 2.4 节使用规范全名。

| | 缩写（图中） | 规范全名（唯一正确形式） |
|---|---|---|
| 示例 | `uplink.raw` | `helios.uplink.raw` |

- **原因**：图节点标签空间受限，为可读性省略了前缀。
- **裁定**：**规范全名为准**。缩写仅限图 3-1/3-2 的节点标签内使用，**不得**出现在正文、配置、代码、监控项、Phase 4 的任何图中。
- **处置**：登记为 Phase 6 审查项。若 Phase 4 的图需要引用 topic，一律写全名；如空间不足，改为在图后用文字列出，而不是在图里缩写。

> 这正是命名表要在 Phase 3 就抽取、而不是等到 Phase 6 才审查的原因：**漂移在只有 2 张图时最容易纠正**，等到 8 张图各自缩写，成本会高一个量级。

---

## 3. MQTT Topic 命名

**冻结后不得变更**——边缘固件升级周期长，向后兼容成本极高。

| 方向 | 模式 |
|---|---|
| 上行 | `helios/{env}/up/{region}/{stationId}/{telemetry\|alarm\|block\|file-meta\|health}` |
| 下行 | `helios/{env}/dn/{stationId}/{cmd\|config\|rules\|ota\|cert\|recall}` |

约定：MQTT 5.0 为主路径（User Properties 携带 `blockSeq`/`traceId`/`schemaVersion`；Reason Code 用 `Server Busy` 做背压；Topic Alias 降头部开销；Shared Subscription 做云侧消费均衡），3.1.1 为兼容降级路径 —— 因此 **payload 必须自包含**，不得依赖 5.0 独有特性。

---

## 4. 禁止创建名单

| 名称 | 为什么禁止 | 来源 |
|---|---|---|
| `helios-northbound-service` | 待拍板 #7 未确认前**不得创建**。约束清单第 9 节明确平台是 SCADA/EMS 的数据**消费方**（经边缘 Modbus TCP / IEC 104 读取），北向输出暂由 `helios-openapi-gateway` 提供数据订阅 API。若业务方确认需要独立北向服务，先改本表再画图 | `02-decisions.md` 待拍板 #7 |
| 任何 `-core` / `-common` / `-misc` / `-util` 后缀 | 命名规则禁用缩写歧义词，这类名字会吸引无关逻辑聚集 | `02-decisions.md` 1.3 |
| 任何面向 Ⅰ/Ⅱ 区的下行控制服务 | 合规红线：平台只监视不控制。边缘固件层面不实现 Modbus 写功能码（0x05/0x06/0x10）、IEC 104 不实现遥控遥调 ASDU | `02-decisions.md` 4.4 |

---

## 5. Phase 3 退出标准核对

| 退出标准（usage 手册 6.5） | 状态 | 证据 |
|---|---|---|
| 命名表里每个名字都在至少一张图里出现过（无幽灵服务） | ✅ | 23 项均由 `grep` 从 `docs/design.md` 抽取；#4 `helios-edge-runtime` 仅出现于图 3-1（边缘侧不在 ACK 部署图中，符合预期） |
| 两张图里没有同物异名 | ⚠️ **一处** | Kafka topic 缩写漂移，见 2.1，已裁定并登记为 Phase 6 审查项 |
| 与 `02-decisions.md` 服务清单一致 | ✅ | 交叉核对唯一差异是 `helios-northbound-service`，而它在决策文档中是作为"**不要建**"出现的 → 已列入第 4 节禁止创建名单 |
| 在 Markdown Viewer 里实际渲染过 | ❌ **未执行** | 本机未安装 Markdown Viewer 扩展，无法验证渲染。**这是本次流程验证的一个缺口**，见第 6 节 |
| 每张图前后都有文字，没有裸图 | ✅ | 图 3-1 前有 1 段引导、后有 5 条要点；图 3-2 同样 |
| 图中服务都能在 `02-decisions.md` 找到决策依据 | ✅ | 23 项对应决策文档 1.2 节 #1~#20 + 3 个中间件单元 |

---

## 6. 本次验证遗留项

| # | 遗留项 | 说明 | 处置建议 |
|---|---|---|---|
| 1 | **未做渲染验证** | 本机无 Markdown Viewer 扩展，两张图只做了语法与图标名核对（所有 `mxgraph.*` 名称均经 `grep` 在 stencils 中确认存在），未实际出图 | 装扩展后打开 `docs/design.md` 目视检查；或在有 PlantUML 的环境跑一次 `plantuml -syntax` |
| 2 | **Phase 2 闸门被有意越过** | `02-decisions.md` 有 8 项待拍板未确认，按 usage 手册 5.3 不应进入 Phase 3。本次为验证流程，采用其第 7 节的临时处理继续 | 真实项目必须停下等业务方确认。受影响的图内假设已列在 `docs/design.md` 3.3 节 |
| 3 | 图规模偏大 | 图 3-1 约 40 个节点、图 3-2 约 45 个节点，PlantUML 自动布局可能不理想 | 若渲染后布局混乱：拆成"主链路图 + 治理/旁路图"两张，或改用 `graphviz`（自动布局对大图更稳） |
| 4 | 图标语义近似 | 无 EMQX / Kafka / IoTDB / Flink 的专属图标，自建组件统一用 `kubernetes.sts`/`deploy`/`cronjob` 表示 | 已在 1.2 节注明该约定的含义；若需更精确可改用 `architecture` skill（HTML/CSS，可自由标注） |

---

## 7. 交给 Phase 4 的使用规则

Phase 4 每个委派 prompt 都必须包含本文件路径，并附以下三条指令：

1. **服务名逐字使用第 1 节规范名称**，不得另创、不得缩写、不得改大小写或连字符风格。
2. **Kafka topic 一律写第 2 节规范全名**（含 `helios.` 前缀），图内空间不足时改在图后文字说明。
3. **需要新增服务时，先提 PR 改本表，再画图**；本表未收录的名称一律视为错误。
4. **图标约定沿用图 3-1/3-2**（三条，违反会让图产生错误暗示）：
   - `mxgraph.alibaba_cloud.*` 仅用于**真实使用的阿里云托管服务**（OSS、RDS、Redis、ACK、SLS、NLB/SLB、云防火墙、RAM、SSL 证书服务、堡垒机、智能接入网关、VPN 网关、云监控）。
   - `mxgraph.kubernetes.sts` / `deploy` / `cronjob` 用于**跑在 ACK 上的自建组件**（EMQX、Kafka、IoTDB、Flink 及全部自研微服务）。`sts`=有状态、`deploy`=无状态、`cronjob`=批处理，这个区分本身携带"谁负责高可用与备份"的信息。
   - `mxgraph.aws4.*` 用于**与云厂商无关的通用实体**（边缘网关、现场设备与传感器、外部通知系统、用户 App、MQTT 协议、IoT 语义类组件）。
   - 无 EMQX / Kafka / IoTDB / Flink 的专属图标，**不要**借用 `alibaba_cloud.kafka` 或 `realtime_compute`——那两个是**托管产品**图标，用来表示自建集群会误导读者以为有云厂商 SLA 兜底。
   - 新增图标前必须 `grep` 验证存在：`grep -E "mxgraph\.<prov>\.<name>([^a-z0-9_]|$)" ~/.claude/skills/uml/stencils/<prov>.md`。本次验证中凭记忆写的 `alibaba_cloud.mobile_client` 即不存在（已改 `aws4.mobile_client`），另 `kms_key_management_service`、`cloud_firewall`、`ssl_certificates_service` 三个猜测名也均不存在（正确名为 `cas_ssl_central_authentication_service`、`cfw_cloud_firewall`）。

Phase 4 待画的图（见 playbook 6.4 与 usage 手册第 8 节）：

| 图 | Skill | 要回答的具体问题 |
|---|---|---|
| 设备首次接入时序 | `uml` sequence | X.509 双向认证如何完成、设备影子如何建立、`mqtt-broker`/`device-auth`/`thing-model`/`ingest-service` 四方交互、认证失败的重试与退避、双活连接如何建立 |
| 72h 离线补传时序 | `uml` sequence | 块级幂等如何保证零重复、`block.late` 专道如何避免污染 watermark、聚合如何定向重算、补传告警如何抑制 |
| 召测削峰时序 | `uml` sequence | 令牌桶如何调度、波形如何分流至 OSS 不入 TSDB、`rate_budget` 如何在边缘整形、背压如何回推到源头 |
| 告警端到端时序 | `uml` sequence | 快路径与 CEP 路径的分叉、10s 时延预算各环节、三通道并行与独立熔断 |
| 设备生命周期状态机 | `uml` state-machine | 未激活/在线/离线/补传中/OTA中/故障/已注销 的全部迁移与触发条件；与 `asset-registry` 的归属 |
| 服务依赖图 | `graphviz` | 23 个单元的依赖与**故障传播路径**；按节点池/SLA 档 cluster 分组 |
| 数据链路图 | `data-analytics` | 采集→Kafka→Flink→IoTDB→OSS 冷热四层→BI；标出吞吐与延迟 |
| 安全架构图 | `security` | 四网络分区信任边界、证书轮换链路、"只监视不控制"的可验证点、审计流 |
