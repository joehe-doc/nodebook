# Helios 分布式光伏与储能电站物联监控平台 · 概要设计（HLD）

| 项 | 值 |
|---|---|
| 文档版本 | v0.3（Phase 0~3 产出） |
| 文档类型 | 概要设计，不含接口字段、表结构、代码、UI |
| 依据 | `design/00-constraints.md` v1、`design/01-capability-map.md` v1.1、`design/02-decisions.md` |
| 命名基准 | `design/03-naming-table.md` v1 —— **全文服务名以此为准** |
| 状态 | ⚠️ **Phase 2 退出标准未完全满足**：8 项待拍板未确认，第 3 章按 `02-decisions.md` 第 7 节的临时处理推进 |

> ⚠️ **本文档是 `design-doc-playbook.md` 的流程验证产物**，业务约束为虚构但自洽，不代表任何真实系统。
> 用途是检验 Phase 0~3 能否顺畅跑通、产出格式是否可用。

---

## 文档结构与阶段对应

| 章 | 内容 | 来源阶段 | 状态 |
|---|---|---|---|
| 1 | 设计约束 | Phase 0 | ✅ 见 `design/00-constraints.md` |
| 2 | 能力全景 | Phase 1 | ✅ 见 `design/01-capability-map.md` |
| 3 | 总体架构与部署架构 | Phase 3 | ✅ 本文 |
| 4~8 | 时序图、状态机、服务依赖、数据链路、安全架构 | Phase 4 | ⏳ 未执行 |
| 9~11 | 术语表、非功能需求、演进路线 | Phase 5 | ⏳ 未执行 |

第 1、2 章内容不在此重复，直接引用 `design/` 下的阶段产出文件——这是 playbook 的刻意设计：**阶段产出单独成文件，便于 Phase 4 委派时按路径交给 subagent**。

---

## 3. 总体架构与部署架构

### 3.1 图 3-1 · 端到端总体架构（Device → Edge → Cloud）

本图给出从电站现场设备到云端消费的完整数据通路与控制通路，是后续所有细化图的命名与边界基准。图中特别标出了两处**合规硬边界**（Ⅰ/Ⅱ 区不可接入）与一处**可用性核心机制**（边缘跨 AZ 双活连接）。

```plantuml
@startuml
left to right direction
skinparam defaultTextAlignment center
skinparam shadowing false
skinparam nodesep 45
skinparam ranksep 70
skinparam rectangle {
  BorderColor #607D8B
  BackgroundColor #FCFCFC
  FontSize 12
}

' ══════════════ 电站现场 ══════════════
rectangle "电站现场（客户侧 · 终态 50 万座）" as SITE {

  rectangle "生产控制大区 Ⅰ/Ⅱ 区\n【合规红线：平台不得接入】" #FFEBEE {
    mxgraph.aws4.iot_thing_plc "PLC / 保护装置" as PLC
    mxgraph.aws4.factory "客户 SCADA / EMS\n（上游数据源）" as SCADA
  }

  rectangle "客户侧 Ⅱ/Ⅲ 区隔离装置\n【客户建设 · 交付前置条件】" #FFF3E0 {
    mxgraph.aws4.gateway "正向/反向\n物理隔离" as ISO
  }

  rectangle "管理信息大区 Ⅲ 区（平台可接入）" as ZONE3 {
    mxgraph.aws4.iot_thing_plc "组串逆变器\nModbus TCP 只读 0x03/0x04" as INV
    mxgraph.aws4.sensor "智能电表\nIEC 104 只读" as METER
    mxgraph.aws4.iot_thing_industrial_pc "储能 PCS\nModbus TCP 只读" as PCS
    mxgraph.aws4.iot_thing_temperature_humidity_sensor "环境传感器\n辐照 / 温湿度" as ENV
  }

  rectangle "边缘网关 ARM64 2C4G\nhelios-edge-runtime" as EDGE #E3F2FD {
    mxgraph.aws4.greengrass "采集 · 协议解析\n整站聚合（5min 块）" as EG_COL
    mxgraph.aws4.iot_greengrass_component_nucleus "本地规则告警\n云侧中断仍运行" as EG_RULE
    mxgraph.aws4.iot_greengrass_stream_manager "分级环形缓存 ≥72h\n淘汰留痕" as EG_BUF
    mxgraph.aws4.iot_over_the_air_update "A/B 双分区\n签名 OTA · 失败回滚" as EG_OTA
  }
}

' ══════════════ 传输 ══════════════
rectangle "传输网络（4G/5G 或专线）" as NET {
  mxgraph.aws4.mqtt_protocol "MQTT 5.0 主路径\n3.1.1 兼容降级\nQoS 1 · keepalive 15s" as MQTT
}

' ══════════════ 云端：接入层 ══════════════
rectangle "接入层（ACK pool-connect · 每 AZ 常驻 100% 容量）" as ACCESS {
  mxgraph.aws4.iot_core "helios-mqtt-broker\nEMQX 集群 · 100 万连接\n（双活后 = 50 万 × 2）" as BROKER
  mxgraph.aws4.certificate_manager "helios-device-auth\nX.509 双向 TLS + 一机一密\n90 天证书 · OCSP 吊销" as AUTH
  mxgraph.aws4.iot_device_gateway "helios-ingest-service\n解码 · 时间戳修正\n块级幂等去重 · 分流" as INGEST
  mxgraph.aws4.api_gateway "helios-openapi-gateway\nDMZ 子网" as OAPI
}

' ══════════════ 云端：边缘控制面 ══════════════
rectangle "边缘控制面（ACK pool-app）" as ECTRL {
  mxgraph.aws4.iot_device_management "helios-edge-manager\n配置/规则集编译下发\n召测队列 + 令牌调度" as EDM
}

' ══════════════ 云端：消息与流处理 ══════════════
rectangle "消息与流处理" as STREAM {
  mxgraph.aws4.kinesis_data_streams "helios-kafka-telemetry\n遥测集群 · acks=1\n128 分区 · 保留 24h/6h/3h" as KTEL
  mxgraph.aws4.kinesis_data_streams "helios-kafka-alarm\n告警集群 · acks=all\nmin.insync.replicas=2" as KALM
  mxgraph.aws4.iot_analytics_pipeline "helios-stream-processor\nFlink · 分钟/小时/日聚合\n质量校验 · 缺口检测" as FLINK
}

' ══════════════ 云端：存储 ══════════════
rectangle "存储层（ACK pool-data + OSS）" as STORE {
  mxgraph.aws4.iot_analytics_channel "helios-tsdb-writer\n攒批 · 优先级队列 · 背压" as TSW
  mxgraph.aws4.timestream "helios-tsdb-cluster\nIoTDB 3 副本跨 AZ\nL1 热 90 天（本地 NVMe）" as TSDB
  mxgraph.aws4.iot_analytics_dataset "helios-file-service\nSTS 凭证签发\n分片状态 · 元数据索引" as FSVC
  mxgraph.aws4.s3 "OSS（境内）\nL4 录波 ≈2.1PB/13月\nL2/L3 冷层 · 审计 WORM" as OSS
  mxgraph.aws4.iot_analytics_data_store "helios-data-lifecycle\n保留策略单点管理\n每日核对'应删已删'" as LIFE
}

' ══════════════ 云端：告警 ══════════════
rectangle "告警链路（99.95% 档 · P99 < 10s）" as ALARM {
  mxgraph.aws4.iot_events "helios-alarm-engine\nFlink CEP · 规则热更新\n（跨站/长历史规则）" as AENG
  mxgraph.aws4.iot_button "helios-alarm-service\n去重 · 抑制 · 分级 · 闭环\n边缘直报走快路径" as ASVC
  mxgraph.aws4.aws_user_notifications "helios-notify-dispatcher\n三通道独立线程池\n独立熔断 · 持久化重试" as NOTIFY
}

' ══════════════ 云端：建模与开放 ══════════════
rectangle "建模与开放能力（99.9% 档）" as APP {
  mxgraph.aws4.iot_sitewise_asset_model "helios-thing-model\n物模型版本 · 量纲换算\n设备影子（期望/上报态）" as TM
  mxgraph.aws4.iot_sitewise_asset_hierarchy "helios-asset-registry\n电站-设备-点位三级拓扑\n生命周期状态机" as REG
  mxgraph.aws4.iot_analytics "helios-query-service\n跨层路由 · 降采样下推\nP99 < 2s" as QUERY
  mxgraph.aws4.iot_analytics_dataset "helios-report-service\n独立资源配额\n批量导出" as REPORT
  mxgraph.aws4.users "helios-access-control\n统一 PDP · RBAC\n多租户 · 电站级数据范围" as ACL
}

' ══════════════ 云端：治理 ══════════════
rectangle "治理与可观测" as GOV {
  mxgraph.aws4.iot_device_defender "helios-audit-service\n下行指令全量审计\n≥3 年 · 三权分立" as AUDIT
  mxgraph.aws4.cloudwatch "helios-observability\n指标 · 链路追踪\n在线率 · 完整率 · 成本水位" as OBS
}

' ══════════════ 外部系统 ══════════════
rectangle "外部系统（平台不自建）" as EXT #F3E5F5 {
  mxgraph.aws4.user "公司统一 IAM" as IAM
  mxgraph.aws4.aws_user_notifications "公司告警中心\nWebhook" as CORPALARM
  mxgraph.aws4.mobile_client "短信网关\nApp 推送网关" as MSG
  mxgraph.aws4.mobile_application "用户 App / H5 大屏" as USERAPP
}

' ─────────── 现场内部：只读采集 ───────────
INV --> EG_COL : Modbus TCP\n只读功能码
METER --> EG_COL : IEC 104\n无遥控遥调
PCS --> EG_COL
ENV --> EG_COL

' ─────────── 合规隔离边界 ───────────
SCADA --> ISO : 客户侧北向
ISO --> EG_COL : Ⅲ 区侧接入
PLC ..> ISO

' ─────────── 边缘内部 ───────────
EG_COL --> EG_BUF
EG_BUF --> EG_RULE
EG_RULE ..> MQTT : 告警 QoS 1

' ─────────── 上行主通道 ───────────
EG_BUF ..> MQTT : 遥测 5min 块\nhelios/{env}/up/.../telemetry
MQTT ..> BROKER : ①主连接 → AZ-A
MQTT ..> BROKER : ②备连接 → AZ-B\n告警双发·遥测主备

' ─────────── 文件旁路（不经 MQTT）───────────
EG_BUF ..> FSVC : 申请 STS\nfile-meta
FSVC ..> EG_BUF : 临时凭证 ≤15min
EG_BUF ..> OSS : 录波分片直传\n≈5.5 TB/日

' ─────────── 接入层内部 ───────────
BROKER --> AUTH : 鉴权回调\n结果短 TTL 缓存
BROKER --> INGEST : uplink.raw
INGEST ..> KTEL : 常规遥测
INGEST ..> KALM : 边缘已判定告警\n（快路径）
INGEST ..> OSS : 召测波形 → 分流\n不入时序库

' ─────────── 流处理与存储 ───────────
KTEL --> FLINK
FLINK --> TSW
TSW --> TSDB
TSDB ..> OSS : L2/L3 冷热分层\nTsFile 分级存储
LIFE --> TSDB : 保留策略
LIFE --> OSS : 生命周期规则

' ─────────── 告警链路 ───────────
KALM --> ASVC : alarm.edge（不经 Flink）
KTEL --> AENG : 云端规则
AENG ..> KALM : alarm.fired
KALM --> ASVC
ASVC --> NOTIFY : alarm.notify
NOTIFY ..> CORPALARM : Webhook
NOTIFY ..> MSG : 短信 / 推送\n三通道并行
MSG ..> USERAPP
ASVC --> USERAPP

' ─────────── 下行控制面 ───────────
EDM ..> BROKER : config / rules / ota / recall\nhelios/{env}/dn/{stationId}/...
BROKER ..> EG_OTA : 下行 QoS 1 + 应用层 ACK
EDM --> AUDIT : 全量埋点
EDM ..> EG_BUF : rate_budget\n（削峰第一级）

' ─────────── 建模与开放 ───────────
REG --> TM : 拓扑 + 物模型版本
TM ..> EG_COL : 已签名快照\n离线 72h 可解析
INGEST --> REG
QUERY --> TSDB
QUERY --> OSS : 冷层异步回捞
REPORT --> TSDB : 仅读聚合层
OAPI --> QUERY
OAPI --> REPORT
OAPI --> ACL : 统一鉴权决策
ACL --> IAM
USERAPP --> OAPI
OAPI ..> SCADA : 北向数据订阅\n（待拍板 #7）

' ─────────── 治理 ───────────
OBS ..> BROKER
OBS ..> KTEL
AUDIT --> OSS : WORM 归档
@enduml
```

**这张图要让人注意到的五点：**

1. **合规边界是架构性的，不是文档性的。** Ⅰ/Ⅱ 区（红色）与平台之间隔着**客户侧**的隔离装置，平台不提供任何通往 Ⅰ/Ⅱ 区的通道。更关键的是现场采集只实现 Modbus **只读功能码 0x03/0x04**、IEC 104 不实现遥控遥调 ASDU——"只监视不控制"因此在固件层面可验证、可审计，而不只是声明。隔离装置由客户建设，是**交付前置条件**（待拍板 #4）。

2. **边缘网关不是薄客户端。** 它承载采集解析、本地规则告警、≥72h 分级环形缓存、块级补传、A/B 签名 OTA 五项能力。云侧全断时本地告警逻辑继续运行——这是约束清单的硬约束，也是 3.1 节削峰的第一级缓冲（`rate_budget` 让 72h 缓存同时成为容量红利）。

3. **双活连接是 99.95% + P99<10s 的唯一低成本解。** 边缘同时持有 AZ-A / AZ-B 两条 MQTT 连接：告警双发（云侧按 `(stationId, alarmSeq)` 幂等去重），遥测只走主连接、探测失败 <1s 切备。代价是 broker 连接数从 50 万翻倍到 **100 万**，节点数由连接数而非消息速率驱动。单连接+快速切换方案在数学上无法达标（keepalive 超时判定 22.5s，且 AZ 故障影响 50% 站点时 P99 就等于故障期时延）。

4. **召测波形走旁路，不进时序库。** 这是削峰的核心：录波文件由边缘分片直传 OSS（不经 MQTT、不入 Kafka 主体），时序库只写召测窗口的摘要特征值。效果是把 TSDB 峰值写入从 2,000,000 样本/s 压回约 100,000，节点数降约一个数量级，年省 ¥45~115 万。

5. **告警有两条入口，快路径不经 Flink。** 边缘已判定的告警直接进 `helios-kafka-alarm` → `helios-alarm-service`（跳数最少）；只有需要跨站关联或长历史窗口的云端规则才走 `helios-alarm-engine`。两个 Kafka 集群物理隔离——page cache 与磁盘调度无法用 quota 隔离，共用集群会让遥测峰值吃掉告警的时延预算。

---

### 3.2 图 3-2 · 阿里云部署架构（VPC 四分区 · ACK 三节点池）

本图给出图 3-1 中云端部分的物理部署形态：四个网络分区、三个 ACK 节点池（对应三类完全不同的弹性模型）、Kafka 双集群与数据层的跨 AZ 布局。节点池的划分依据是**扩容时机**而非服务分类——这是本图最重要的一条信息。

```plantuml
@startuml
left to right direction
skinparam defaultTextAlignment center
skinparam shadowing false
skinparam nodesep 40
skinparam ranksep 65
skinparam rectangle {
  BorderColor #607D8B
  BackgroundColor #FCFCFC
  FontSize 12
}

' ══════════ 入口 ══════════
mxgraph.alibaba_cloud.user "运维 / 业主 / EPC\n（多租户）" as USERS
mxgraph.aws4.mobile_client "用户 App" as APP
mxgraph.aws4.greengrass "50 万座边缘网关\n（双活连接 → 100 万）" as GWS

' ══════════ 云外防护 ══════════
rectangle "云外防护与入口" as EDGESEC {
  mxgraph.alibaba_cloud.ddos_protection "DDoS 防护" as DDOS
  mxgraph.alibaba_cloud.waf_web_application_firewall "WAF" as WAF
  mxgraph.alibaba_cloud.dns_domain_name_system "云解析 DNS" as DNS
}

cloud "阿里云 · 华东1（杭州）· 单 Region 双 AZ · 数据不出境" as ALI {

  rectangle "VPC 10.0.0.0/16" as VPC {

    ' ───── DMZ 区 ─────
    rectangle "① DMZ 区（有公网入口）" as DMZ #FFF8E1 {
      mxgraph.alibaba_cloud.nlb_network_load_balancer_01 "NLB-接入\nAZ-A VIP" as NLBA
      mxgraph.alibaba_cloud.nlb_network_load_balancer_02 "NLB-接入\nAZ-B VIP" as NLBB
      mxgraph.alibaba_cloud.slb_server_load_balancer_01 "SLB-业务\n（OpenAPI / H5）" as SLB
      mxgraph.alibaba_cloud.nat_gateway "NAT 网关\n（仅出向）" as NAT
    }

    ' ───── 边缘接入区 ─────
    rectangle "② 边缘接入区" as EDGEZONE #E8F5E9 {
      mxgraph.alibaba_cloud.sag_smart_access_gateway_01 "智能接入网关\n（专线客户）" as SAG
      mxgraph.alibaba_cloud.vpn_gateway "VPN 网关\n（4G/5G 客户）" as VPNGW
    }

    ' ───── 应用区：ACK ─────
    rectangle "③ 应用区（无公网入口）· ACK 集群" as APPZONE {

      rectangle "pool-connect\n【每 AZ 常驻 100% · 禁用抢占式】\n长连接事后扩容无效 → 必须预留" as POOLC #E3F2FD {
        mxgraph.kubernetes.sts "helios-mqtt-broker\nEMQX · 每 AZ ≥2 节点\n集群 ≥4 节点" as D_BROKER
        mxgraph.kubernetes.deploy "helios-device-auth\n自建 CA 链 · OCSP" as D_AUTH
        mxgraph.kubernetes.deploy "helios-ingest-service\n无状态水平扩" as D_INGEST
        mxgraph.kubernetes.deploy "helios-openapi-gateway" as D_OAPI
      }

      rectangle "pool-app\n【HPA + KEDA 按 Kafka lag 弹性】\n召测类消费者用按量弹性节点组" as POOLA #F3E5F5 {
        mxgraph.kubernetes.deploy "helios-edge-manager\n（含召测令牌调度）" as D_EDM
        mxgraph.kubernetes.sts "helios-stream-processor\nFlink on ACK / 全托管\nRocksDB + 增量 ckpt" as D_FLINK
        mxgraph.kubernetes.deploy "helios-tsdb-writer\n（KEDA 按 lag）" as D_TSW
        mxgraph.kubernetes.deploy "helios-file-service" as D_FSVC
        mxgraph.kubernetes.cronjob "helios-data-lifecycle\n批处理 · 低优先级" as D_LIFE
        mxgraph.kubernetes.sts "helios-alarm-engine\nFlink CEP · 近无状态\n（状态外置 Redis）" as D_AENG
        mxgraph.kubernetes.deploy "helios-alarm-service\n99.95% 档" as D_ASVC
        mxgraph.kubernetes.deploy "helios-notify-dispatcher\n99.95% 档 · 三通道隔离" as D_NOTIFY
        mxgraph.kubernetes.deploy "helios-query-service\n99.9% 档" as D_QUERY
        mxgraph.kubernetes.deploy "helios-report-service\n99.9% 档 · 独立配额" as D_REPORT
        mxgraph.kubernetes.deploy "helios-asset-registry" as D_REG
        mxgraph.kubernetes.deploy "helios-thing-model" as D_TM
        mxgraph.kubernetes.deploy "helios-access-control\n统一 PDP" as D_ACL
        mxgraph.kubernetes.deploy "helios-audit-service" as D_AUDIT
        mxgraph.kubernetes.deploy "helios-observability" as D_OBS
      }
    }

    ' ───── 数据区 ─────
    rectangle "④ 数据区（无公网入口 · 仅安全组白名单可达 · 禁止北向发起连接）" as DATAZONE #FFEBEE {

      rectangle "helios-kafka-telemetry（遥测集群）\n8~12 台 NVMe · 峰值 200MB/s\n常态 6.8MB/s · 允许 lag 千万级" as KAFKAT #E8EAF6 {
        mxgraph.kubernetes.sts "uplink.raw 128p/24h" as T1
        mxgraph.kubernetes.sts "telemetry.norm 128p/6h" as T2
        mxgraph.kubernetes.sts "recall.burst 64p/3h\n独立 client 配额" as T3
        mxgraph.kubernetes.sts "block.late 64p/7d\n补传专道" as T4
      }

      rectangle "helios-kafka-alarm（告警集群）\n3~5 台小规格 · 零堆积容忍\nacks=all · rack awareness 跨 AZ" as KAFKAA #E8EAF6 {
        mxgraph.kubernetes.sts "alarm.edge / alarm.fired\nalarm.notify / cmd.down" as A1
      }

      rectangle "helios-tsdb-cluster（IoTDB 自建）\n3 副本跨 AZ · 写入 quorum=2\nL1 热层 90 天本地 NVMe" as TSDBC #E0F2F1 {
        mxgraph.kubernetes.sts "数据节点 3~6（分流后）\n按稳态 66,700 样本/s +50%" as TS1
      }

      mxgraph.alibaba_cloud.mysql "RDS MySQL 8.0 高可用版\n主备跨 AZ（切换 <30s）\n+ 只读实例供报表" as RDS
      mxgraph.alibaba_cloud.redis_kvstore "Redis 集群版 跨 AZ 主从\n设备影子 · 告警抑制窗口\n在线态 · 令牌桶 · 幂等键" as REDIS
      mxgraph.alibaba_cloud.disk_block_storage "ESSD / 本地 NVMe\n（pool-data 专用）" as DISK
    }

    ' ───── Region 级服务 ─────
    rectangle "Region 级托管服务" as REGIONAL {
      mxgraph.alibaba_cloud.oss_object_storage_service "OSS（境内）\n录波 2.1PB · 冷层 L2/L3\n审计 WORM ≥3年\n备份 · Flink ckpt · OTA 固件" as OSS
      mxgraph.alibaba_cloud.ask_ack_container_service_for_kubernetes "ACK 容器服务\n三节点池 · 跨 AZ 反亲和" as ACK
      mxgraph.alibaba_cloud.cas_ssl_central_authentication_service "SSL 证书服务\n+ 自建 CA 层级\n离线 Root → 中间 CA → 设备证书" as CAS
      mxgraph.alibaba_cloud.cfw_cloud_firewall "云防火墙\n+ 安全组 / NACL" as CFW
      mxgraph.alibaba_cloud.ram_resource_access_management "RAM\n（对接公司统一 IAM）" as RAM
      mxgraph.alibaba_cloud.sls_simple_log_service "SLS 日志服务" as SLS
      mxgraph.alibaba_cloud.cms_cloud_monitor_service "云监控\n+ ARMS / Prometheus" as CMS
      mxgraph.alibaba_cloud.bastionhost "堡垒机\n运维入口强制双因素" as BASTION
    }
  }
}

' ══════════ 外部系统 ══════════
rectangle "公司既有系统（复用，不自建）" as CORP #F3E5F5 {
  mxgraph.alibaba_cloud.user "统一 IAM" as CIAM
  mxgraph.alibaba_cloud.sms_short_message_service "短信网关" as CSMS
  mxgraph.aws4.aws_user_notifications "公司告警中心\nWebhook" as CCENTER
}

' ─────────── 入口链路 ───────────
USERS --> DNS
APP --> DNS
DNS --> DDOS
DDOS --> WAF
WAF --> SLB
SLB --> D_OAPI

GWS ..> SAG : 专线客户
GWS ..> VPNGW : 4G/5G 客户
SAG --> NLBA
SAG --> NLBB
VPNGW --> NLBA
VPNGW --> NLBB

' ─────────── 双活连接落点 ───────────
NLBA --> D_BROKER : AZ-A
NLBB --> D_BROKER : AZ-B\n告警双发 · 遥测主备
D_BROKER --> D_AUTH : 鉴权回调
D_AUTH ..> CAS : 证书链 / OCSP
D_BROKER --> D_INGEST

' ─────────── 遥测主链 ───────────
D_INGEST ..> KAFKAT
D_INGEST ..> KAFKAA : 边缘告警快路径
D_INGEST ..> OSS : 召测波形分流
KAFKAT --> D_FLINK
D_FLINK --> D_TSW
D_TSW --> TSDBC
KAFKAT --> D_AENG
D_AENG ..> KAFKAA
KAFKAA --> D_ASVC
D_ASVC --> D_NOTIFY
D_ASVC --> REDIS : 抑制窗口状态
D_FLINK --> REDIS

' ─────────── 通知出口 ───────────
D_NOTIFY ..> CSMS
D_NOTIFY ..> CCENTER
D_NOTIFY ..> APP : 推送\n三通道并行·独立熔断

' ─────────── 下行控制 ───────────
D_EDM ..> D_BROKER : cmd.down
D_EDM --> D_AUDIT : 全量埋点
D_EDM ..> GWS : config/rules/ota/recall

' ─────────── 数据层访问 ───────────
D_QUERY --> TSDBC
D_QUERY --> REDIS : 降采样结果缓存
D_QUERY ..> OSS : L3 异步回捞
D_REPORT --> TSDBC : 仅读聚合层
D_REPORT --> RDS
D_REG --> RDS
D_TM --> RDS : 同实例不同 schema
D_TM --> REDIS : 设备影子上报态
D_ACL --> CIAM
D_OAPI --> D_ACL
D_LIFE --> TSDBC : 保留策略
D_LIFE --> OSS : 生命周期规则
D_FSVC ..> OSS : STS 凭证
D_AUDIT --> OSS : WORM
TSDBC ..> OSS : TsFile 分级存储
D_FLINK ..> OSS : checkpoint / savepoint

' ─────────── 基础设施与治理 ───────────
ACK --> POOLC
ACK --> POOLA
CFW --> DMZ
CFW --> DATAZONE
BASTION --> POOLA : 运维入口
D_OBS ..> CMS
D_OBS ..> SLS
KAFKAT --> DISK
TSDBC --> DISK

note bottom of POOLC
  **为什么 pool-connect 必须每 AZ 常驻 100%**
  长连接扩容会触发重连风暴，
  事后扩容无效，必须预留。
  这是"单 AZ 不中断"的真实价格：
  2× 容量成本，须在预算中明示。
end note

note bottom of DATAZONE
  **Kafka 双集群物理隔离的理由**
  遥测峰值 200MB/s 会占满 broker 的
  磁盘 IO 与 page cache，使告警消费
  退化为磁盘读。Kafka quota 只能限
  客户端速率，无法隔离 page cache
  与磁盘调度 → 必须分集群。
end note
@enduml
```

**这张图要让人注意到的五点：**

1. **三个节点池对应三类完全不同的弹性模型，划分依据是"扩容时机"而非服务分类。** `pool-connect` 每 AZ 常驻 100% 容量且**禁用抢占式实例**——长连接扩容会触发重连风暴，事后扩容无效，只能预留；`pool-app` 用 HPA + KEDA 按 Kafka lag 弹性，召测类消费者可用按量弹性节点组（峰值成本按小时计）；`pool-data` 固定容量、本地 NVMe、跨 AZ 反亲和。把这三类混在一个节点池里，任何一类的弹性策略都会伤害另外两类。

2. **四个网络分区中，数据区没有任何公网入口，且禁止北向发起连接。** DMZ 区只放 NLB/SLB/NAT；应用区放全部微服务与 Flink；数据区放 Kafka/IoTDB/RDS/Redis，仅安全组白名单可达。这直接对应等保三级的访问控制要求，也让"平台不提供通往 Ⅰ/Ⅱ 区的通道"在网络层可验证。

3. **自建开源组件用 K8s 工作负载图标表示，不用云产品图标。** 图中 EMQX / Kafka / IoTDB / Flink 都跑在 ACK 上，因此用 `sts`（StatefulSet，有状态）与 `deploy`（Deployment，无状态）区分，而 RDS / Redis / OSS / SLS 等托管服务用阿里云产品图标。**这个区分本身携带信息**：凡是 `sts`/`deploy` 的组件，其高可用、备份、升级都由我们负责；凡是云产品图标的，由阿里云 SLA 兜底。

4. **Kafka 双集群的容量形态是反直觉的。** 遥测集群 8~12 台 NVMe、允许 lag 涨到千万级（堆积能力=磁盘容量，这是唯一蓄水池）；告警集群只需 3~5 台小规格但零堆积容忍、`acks=all`。增量成本占整体个位数百分比，却换来两条不同 SLA 链路的故障域解耦——这是本项目性价比最高的一笔隔离投入。

5. **TSDB 节点数按稳态而非峰值建设（3~6 节点），前提是分流成立。** 若待拍板 #2 的答案是"整站报文含秒级子采样"，稳态写入将从 66,700 样本/s 变为约 4,000,000 样本/s（放大 60 倍），本图的 `pool-data` 容量与 OSS/TSDB 成本分工**都要重算**。这是当前架构图最大的单点不确定性。

---

## 3.3 本章受待拍板项影响的假设

第 3 章两张图基于 `02-decisions.md` 第 7 节的临时处理绘制。**以下 4 项若被推翻，需要重画：**

| 待拍板 # | 当前假设 | 若推翻的影响 |
|---|---|---|
| #1 | 峰值 50,000 msg/s 按"必须无损承载"设计，同时用令牌调度摊平可调度部分 | 若允许摊平，`pool-connect` 与遥测 Kafka 可显著缩容，图 3-2 的容量标注需改 |
| #2 | 11 MB/站/日 按"40 点位 × 5 分钟单值"读法 | **影响最大**：TSDB 节点数、OSS/TSDB 成本分工、`pool-data` 规格全部重算 |
| #3 | 告警 P99<10s 度量终点为"成功提交给三通道网关"；99.95% 排除云侧全断场景 | 若按"到达用户设备"计，短信通道无法承诺，图 3-1 的告警链路时延预算需重列 |
| #7 | 北向数据订阅由 `helios-openapi-gateway` 提供，**不单列服务** | 若确认需要独立北向服务，图 3-1 与 3-2 各增一个节点，命名表需加一行 |

其余 4 项（#4 客户侧隔离装置、#5 IoTDB vs Lindorm、#6 EMQX vs 托管 MQTT、#8 成本上限与报表范围）影响的是选型与交付条件，不改变图的结构。
