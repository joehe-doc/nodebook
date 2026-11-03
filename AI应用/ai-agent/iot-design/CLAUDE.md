# Helios —— 分布式光伏与储能电站物联监控平台

> ⚠️ 本目录是 **playbook 流程验证项目**，约束为虚构但自洽，不代表任何真实系统。
> 目的是检验 `design-doc-playbook.md` 的 Phase 0~3 能否顺畅跑通。

## 设计文档

写或改本目录下的设计文档时，先读这两份，按其中的六阶段流程执行：

- `../design-doc-playbook.md` —— 流程与速查表（**做什么**）
- `../design-doc-playbook-usage.md` —— 操作手册（**怎么驱动**，逐阶段输入话术与退出标准）

> 本项目直接引用上级目录的 playbook，不复制副本，避免两份漂移。
> 真实项目中建议把 playbook 复制进项目根目录并纳入版本控制。

## 目录约定

```
iot-design/
├── CLAUDE.md                     # 本文件
├── docs/
│   └── design.md                 # 设计文档主体（最终交付物）
└── design/                       # 阶段产出，每阶段一个小文件
    ├── 00-constraints.md         # Phase 0：设计约束清单（9 字段）
    ├── 01-capability-map.md      # Phase 1：能力全景脑图
    ├── 02-decisions.md           # Phase 2：架构决策（Plan agent 产出）
    └── 03-naming-table.md        # Phase 3：服务命名表（从骨架图抽取）
```

**阶段产出单独成文件的原因**：Phase 4 每次委派 subagent 都要交出约束清单与命名表。subagent 看不到对话历史但能读文件，所以**先落盘、再给路径**——见 usage 手册 2.3 节。

## 当前进度

| Phase | 状态 | 产出 | 备注 |
|---|---|---|---|
| 0 定边界 | ✅ | `design/00-constraints.md` | 9 字段全填实，指标全数字化 |
| 1 能力分解 | ✅ | `design/01-capability-map.md` v1.1 | `mindmap` skill；v1.1 修正了 Phase 2 报出的矛盾 #7 |
| 2 架构决策 | ⚠️ 完成但**闸门未过** | `design/02-decisions.md` | `Plan` agent 产出；**8 项待拍板未确认**，按 usage 手册 5.3 本不应进入 Phase 3 |
| 3 骨架图 + 命名表 | ✅ | `docs/design.md` 第 3 章（图 3-1/3-2）、`design/03-naming-table.md` | `iot` + `cloud` skill；60 种图标经 grep 全部验证存在；命名表 23 项由脚本从图中抽取 |
| 4~6 | ⏳ 本次验证不含 | — | Phase 4 待画图清单见 `03-naming-table.md` 第 7 节 |

**流程验证报告**见 `RUN-REPORT.md`（记录了跑通情况、发现的问题、对 playbook 的修订建议）。

## 约束速记（详见 `design/00-constraints.md`）

- 50 万座电站，2000 万点位；稳态 1,700 msg/s，**峰值召测 50,000 msg/s**
- 接入+告警链路 99.95%，单 AZ 故障不中断；告警 P99 < 10s
- **边缘自治是硬约束**：云侧中断时本地缓存 ≥72h 并补传，本地告警继续运行
- 阿里云 ACK 单 Region 双 AZ；Java 17 + Spring Boot；**Kafka 为公司标准不可替换**
- MQTT Broker / 时序库 / 流处理引擎**可自选**，需在 Phase 2 给出选型理由
- 等保三级；电力监控安全防护规定 Ⅲ 区，**只监视不控制**；数据不出境
- 本期不做：视频图像、边缘 AI 训练、多活容灾、电力交易结算、电网侧控制、原生 App
