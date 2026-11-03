# 设计文档 Playbook —— 用 Skill + Agent 产出带图的技术设计文档

> 用途：写概要设计 / 详细设计 / 技术方案 / 迁移方案时，照着这份流程走。
> 全文以「云原生 IoT 平台概要设计」为贯穿示例，但流程本身与领域无关。
> 环境事实核对时间：2026-11-02（`~/.claude/skills/` 下 16 个用户级 skill）。

## 配套文档

| 文档 | 回答什么问题 | 什么时候看 |
|---|---|---|
| **本文**（`design-doc-playbook.md`） | **做什么** —— 六阶段流程、skill 选型速查表、fence 格式硬规则、委派 prompt 模板、检查清单 | 规划阶段；委派 subagent 时抄第 7 节模板 |
| **[`design-doc-playbook-usage.md`](./design-doc-playbook-usage.md)** | **怎么驱动** —— 在 Claude Code 会话里每个阶段具体输入什么、实际发生什么、退出标准、常见跑偏 | **实际开工时摊在旁边**，逐阶段照着念 |
| [`ai-agent-development-guide.md`](./ai-agent-development-guide.md) | 被设计的对象本身是 AI Agent 时的领域知识 | 仅当你写的设计文档主题是 Agent / LLM 应用 |

**两份 playbook 的分工**：本文是**规范**（阶段划分、速查表、模板），使用手册是**操作说明**（逐阶段的输入话术、退出标准、排障）。第 6 节讲每个阶段"做什么"，使用手册第 3~6 节讲"怎么让 Claude 把它做出来"。

> 实跑记录见 [`iot-design/`](./iot-design/) —— 用一份虚构但自洽的约束（分布式光伏储能监控平台）走完 Phase 0~3 的产出，可作为格式参照。

---

## 目录

- [1. 核心认知：这些 skill 是怎么工作的](#1-核心认知这些-skill-是怎么工作的)
- [2. 速查表 A：图类型 → skill](#2-速查表-a图类型--skill)
- [3. 速查表 B：skill → fence 与格式硬规则](#3-速查表-bskill--fence-与格式硬规则)
- [4. 速查表 C：agent → 用途与能力边界](#4-速查表-cagent--用途与能力边界)
- [5. 资源位置：图标库、范例、模板](#5-资源位置图标库范例模板)
- [6. 六阶段流程](#6-六阶段流程)
- [7. 委派 prompt 模板（可直接复制）](#7-委派-prompt-模板可直接复制)
- [8. 按文档类型裁剪流程](#8-按文档类型裁剪流程)
- [9. 交付前检查清单](#9-交付前检查清单)

---

## 1. 核心认知：这些 skill 是怎么工作的

### 1.1 Skill 不是可执行程序，是"加载进上下文的写作规范"

调用 `Skill(skill="uml")` 做的事，是把 `~/.claude/skills/uml/SKILL.md` 的规范加载进模型上下文，然后**按规范往 markdown 里写一段带特定 fence 的代码块**。

没有"运行 skill 得到一张图片"这回事。产出永远是 **markdown 文本**。

### 1.2 渲染靠 Markdown Viewer 扩展，不靠本地工具链

所有图表 skill 的 metadata 都标注 *"powered by Markdown Viewer"*（docu.md，Chrome / Edge / Firefox / VS Code 扩展）。

| 你以为需要 | 实际需要 |
|---|---|
| `apt install plantuml graphviz`、本地 Java | **不需要**。渲染在扩展里完成 |
| 把 `.puml` / `.dot` 单独存一份源码 | **不需要**。图源就内联在 markdown 的 fence 里，天然可 diff、可版本控制 |
| — | **需要**：装 Markdown Viewer 扩展（VS Code 或浏览器） |

**只有这两种情况才需要本地工具链**：
1. 要导出 PNG/SVG 塞进 Word / PPT / Confluence；
2. 要在 CI 里自动出图。

那时才 `sudo apt install graphviz plantuml`（本机 Java 是 1.8.0_504，偏老，可能要一起升）。

### 1.3 上下文成本：唤起 skill 很便宜，读图标索引才贵

唤起一个 skill 只加载它的 `SKILL.md`，**不会**加载 `stencils/` 和 `examples/`（那些是按需读取的）。所以目录大小不等于上下文成本。

**SKILL.md 实际大小（= 唤起时的真实成本）：**

| Skill | 字节 | ≈ token |
|---|---:|---:|
| `infocard` | 23.3K | ~7.8K |
| `architecture` | 13.4K | ~4.5K |
| `infographic` | 10.5K | ~3.5K |
| `archimate` | 7.7K | ~2.6K |
| `bpmn` | 7.3K | ~2.4K |
| `mindmap` | 6.2K | ~2.1K |
| `security` | 5.7K | ~1.9K |
| `data-analytics` | 5.3K | ~1.8K |
| `iot` | 5.3K | ~1.8K |
| **`uml`** | **4.7K** | **~1.6K** |
| `network` | 4.4K | ~1.5K |
| `cloud` | 4.2K | ~1.4K |
| `canvas` | 2.6K | ~0.9K |
| `graphviz` | 2.3K | ~0.8K |
| `vega` | 2.2K | ~0.7K |

16 个全部唤起也才 ~37K token。**画一份设计文档常用的 5~6 个 skill 加起来不到 10K token，不用省着用。**

**真正的成本大头是按需读取的图标索引文件：**

| 文件 | 字节 | ≈ token |
|---|---:|---:|
| `stencils/aws4.md` | 58.6K | **~19.5K** |
| `stencils/electrical.md` | 36.6K | ~12.2K |
| `stencils/cisco_safe.md` | 34.0K | ~11.3K |
| `stencils/rack.md` | 33.7K | ~11.2K |
| `stencils/office.md` | 28.1K | ~9.4K |
| `stencils/alibaba_cloud.md` | 19.8K | ~6.6K |
| `stencils/gcp2.md` | 18.8K | ~6.3K |
| `stencils/cisco.md` | 21.0K | ~7.0K |

> **结论：读整个 `aws4.md` 一次就吃掉 ~19.5K token，比唤起全部 16 个 skill 的一半还多。**
> 所以第 5.1 节那条"用 `grep -i` 查图标名，别整个文件读进来"不是锦上添花，是必须遵守的规则。

`examples/` 相反，很便宜（最大的 `sequence-diagram.md` 只有 4.8K 字节），画不熟悉的图类型前**应该**读对应范例。

### 1.4 三种触发方式

| 方式 | 例子 |
|---|---|
| 直接描述需求（模型自动选 skill） | "画一个设备首次接入的时序图" |
| 显式点名 | "用 `cloud` skill 画阿里云部署架构" / `/uml` |
| 需求里指定产出位置和格式 | "…写进 `docs/design.md` 第 4.2 节，用 ` ```plantuml ` fence" |

**推荐第三种**：指定落盘位置，避免图散落在对话里。

---

## 2. 速查表 A：图类型 → skill

### 2.1 按"你要表达什么"选

| 你要表达 | Skill | 备注 |
|---|---|---|
| 分层技术栈 / 平台由哪几层组成 | `architecture` | HTML/CSS 色块，**给非技术读者看最合适** |
| 设备—边缘—云 端到端拓扑 | `iot` | 默认 `left to right direction`，正好是 Device→Edge→Cloud |
| 云上部署（VPC / Region / 云服务） | `cloud` | AWS / Azure / GCP / **阿里云** / IBM Cloud 官方图标 |
| K8s 集群内部结构 | `cloud` | 有 `kubernetes` / `kubernetes2` 图标类 |
| 机房 / 现场网络 / 专线 | `network` | Cisco / Citrix 设备图标 |
| 服务依赖、调用关系、故障传播 | `graphviz` | 自动布局 + cluster 分组，服务多时比 PlantUML 组件图清爽 |
| **时序 / 交互（谁先调谁）** | `uml` | 唯一正解 |
| **状态机（生命周期、状态迁移）** | `uml` | 唯一正解 |
| 类图 / 领域模型 | `uml` | |
| 用例图 | `uml` | |
| 部署图（节点—构件） | `uml` | |
| 技术流程（含分支、并行） | `uml` activity | |
| 跨角色/跨系统的业务流程 | `uml` swimlane-activity 或 `bpmn` | 涉及人和系统混合、审批链 → `bpmn` |
| 企业集成模式（消息路由、 Saga） | `bpmn` | 有 `eip` 图标类 |
| 价值流图（精益） | `bpmn` | 有 `lean_mapping` 图标类 |
| 数据管道 / ETL / 流处理 / 数仓 / BI | `data-analytics` | |
| 数据流图（DFD） | `graphviz` 或 `uml` | 有 `dfd` 图标类 |
| 安全边界 / IAM / 零信任 / 加密链路 | `security` | 信任边界用 `rectangle "Trust Boundary" { }` |
| 能力分解 / 需求拆解 / 决策树 | `mindmap` | **前期梳理用，避免后面漏子系统** |
| 概念地图 / 知识图谱 / 规划板 | `canvas` | 需要精确 x/y 坐标；Obsidian Canvas 兼容 |
| 路线图 / 里程碑 / 时间线 | `infographic` | 模板名必须精确 |
| 泳道式步骤 / 漏斗 / SWOT / 2×2 矩阵 / 组织树 / 饼图 | `infographic` | 同上 |
| A vs B 方案对比 | `infographic` | `compare-binary-*` 系列模板 |
| 统计图表（柱/线/散点/热力/面积/雷达） | `vega` | **写图表前先读 `dataviz`** |
| KPI 卡片 / 数据高亮 / 单主题知识卡 | `infocard` | |
| 企业架构 / TOGAF 三层（业务-应用-技术） | `archimate` | **给架构委员会看的视角** |
| 动机分析 / 迁移规划（EA） | `archimate` | |
| SysML / BDD | `uml` | 有 `sysml-bdd` 范例和 `sysml` 图标类 |

### 2.2 IoT 平台概要设计的主力组合

六张核心图，覆盖评审必需的 80%：

| # | 图 | Skill |
|---|---|---|
| 1 | 能力全景脑图 | `mindmap` |
| 2 | 设备—边缘—云 总体架构 | `iot` |
| 3 | 阿里云 / AWS 部署架构 | `cloud` |
| 4 | 设备接入 + 认证 + 上报时序 | `uml` sequence |
| 5 | 设备生命周期状态机 | `uml` state-machine |
| 6 | 数据链路（采集→MQ→流处理→时序库→BI） | `data-analytics` |

按需再加：`graphviz`（微服务依赖）、`security`（设备身份/零信任）、`network`（现场网络）、`infographic`（演进路线）、`archimate`（EA 视角）。

---

## 3. 速查表 B：skill → fence 与格式硬规则

> **写错了不报错，只是不渲染。** 这张表值得贴在旁边。

| Skill | Fence | 硬性规则 |
|---|---|---|
| `uml` `cloud` `iot` `network` `security` `bpmn` `data-analytics` | ` ```plantuml ` 或 ` ```puml ` | `@startuml` / `@enduml`；**绝不能写 ` ```text `** |
| `mindmap` | ` ```plantuml ` | `@startmindmap` / `@endmindmap`；层级用 `*`/`**`/`***` 或 `+`/`-`；**同一分支内不要混用两种标记风格**；`left side` 切到左侧；可用 `top to bottom direction` 等 |
| `archimate` | ` ```plantuml ` | 必须先 `!include <archimate/Archimate>`；元素 `Layer_Type(alias, "Label")`；关系 `Rel_Type(from, to, "label")`；方向后缀 `_Up`/`_Down`/`_Left`/`_Right` |
| `graphviz` | **` ```dot `** | **不是 ` ```graphviz `**；子图必须 `subgraph cluster_xxx`（少了 `cluster_` 前缀不画框）；节点 ID 含空格要加引号；默认 `rankdir=TB`；用分号结尾 |
| `vega` | ` ```vega-lite ` 或 ` ```vega ` | **必须含 `$schema`**；必须是合法 JSON（双引号、无尾逗号）；字段名大小写敏感；**90% 场景用 Vega-Lite**，只有雷达图/词云/力导向才用 Vega |
| `canvas` | ` ```canvas ` | JSON；节点要有 `id`/`type`/`x`/`y`/`width`/`height`；原点在**左上**，X 右 Y 下；按 100px 网格布局；边用 `fromNode`/`toNode`；颜色 1-6 |
| `infographic` | 专用 fence | **空格分隔的 key-value，不是 YAML**；**模板名必须从 SKILL.md 的列表里精确选，写错直接渲染失败** |
| **`architecture`** | **无 fence —— 直接嵌 HTML** | **规则与其他 skill 完全相反**：绝不能用 ` ```html `；**HTML 结构内不能有空行**（会解析错误）；建议分三步增量写：① 外框+全部 CSS ② 层容器+标题 ③ 逐层填组件 |
| `infocard` | 直接嵌 HTML | 同上，编辑排版风格的单主题卡片 |

### 3.1 PlantUML 系（cloud / iot / network / security / bpmn / data-analytics）的共同约定

```
left to right direction          # 数据流类图的标准方向（云、IoT、数据管道、安全访问流）
rectangle "VPC / Zone / Pool" { } # 分组容器
package "Region / Site / Layer" { }
cloud "Internet" { }              # 云/互联网边界形状
-->                               # 有向流
..>                               # 虚线：异步 / 事件驱动 / 消息流 / 审计流
--                                # 无箭头：双向物理链路（network 专用）
..  或 ..>                        # 虚线：VPN / 无线 / 逻辑链路（network 专用）
mxgraph.aws4.xxx                  # 图标声明语法
skinparam ...                     # 全局样式
```

**默认配色是自动应用的 —— 不要手动指定 `fillColor` / `strokeColor`。**

图标名**不要凭记忆写**，去查 `~/.claude/skills/uml/stencils/<类别>.md`（见第 5 节）。

---

## 4. 速查表 C：agent → 用途与能力边界

| Agent | 上下文 | 能写文件？ | 用在哪 |
|---|---|---|---|
| **`Plan`** | 全新，只有你给的 prompt | ✗（无 Edit/Write） | 出设计骨架：服务拆分、选型、**每个决策的权衡与被否掉的备选**、风险清单 |
| **`Explore`** | 全新 | ✗（只读） | 改造既有系统时，扫描现有代码/文档，让图和**现实**一致而不是和愿望一致 |
| **`general-purpose`** | 全新 | ✓ | 调研型子任务，搜索路径不确定时（"对比 EMQX / VerneMQ / HiveMQ 在千万级长连接下的表现"） |
| **`fork`** | **继承你的完整对话上下文** | ✓ | 把彼此独立的图并行分出去；不需要重复交代背景 |
| **`claude`** | 全新 | ✓ | 兜底，不匹配其他类型时 |
| **`claude-code-guide`** | 全新 | ✗ | 只在文档涉及 Claude Code / Agent SDK / Claude API 时用 |

### 4.1 委派的两条铁律

**① 非 fork 的 subagent 看不到你的对话历史。**

你脑子里的设计约束、前面几轮定下的服务命名表，**必须在委派 prompt 里显式写全**。这是委派质量的第一决定因素。`fork` 是唯一例外（它继承上下文）。

**② 审查用的 agent 要故意不给结论。**

一致性审查阶段派一个 fresh agent，只给它文档路径和"找矛盾"的任务。给了它你的判断，它就会回来确认你 —— 那这次审查就白做了。

### 4.2 并行的时机

| 阶段 | 能否并行 | 原因 |
|---|---|---|
| Phase 1~3（能力分解、架构决策、骨架图） | **必须串行** | 后者依赖前者的产出；骨架图还负责定义命名表 |
| Phase 4（细化图） | **可以并行** | 图之间彼此独立，命名表已固定 |
| Phase 5（组装） | **不要并行** | 需要全局一致性，委派出去会散 |
| Phase 6（审查） | 可并行分维度 | 命名一致性 / 接口闭环 / 数字自洽 各派一个 |

---

## 5. 资源位置：图标库、范例、模板

### 5.1 图标库（61 类，9500+ 图标）

路径：`~/.claude/skills/uml/stencils/`

`cloud` / `iot` / `security` / `data-analytics` / `network` / `bpmn` 全都指向这里的 `README.md`。

| 类别 | 文件 |
|---|---|
| **云厂商** | `aws` `aws2` `aws3` `aws3d` `aws4` `azure` `gcp` `gcp2` `alibaba_cloud` `ibm` `ibm_cloud` `mscae` `openstack` |
| **云原生** | `kubernetes` `kubernetes2` |
| **网络/机房** | `cisco` `cisco19` `cisco_safe` `citrix` `citrix2` `networks` `networks2` `rack` `rackGeneral` `cabinets` `floorplan` `veeam` `veeam2` |
| **流程/集成** | `bpmn` `eip` `flowchart` `lean_mapping` `dfd` `sitemap` |
| **建模** | `uml25` `sysml` `archimate` `archimate3` `arrows` `basic` |
| **工业/电气** | `electrical` `pid` `pid2inst` `pid2misc` `pid2valves` `fluid_power` |
| **UI/前端** | `mockup` `webicons` `weblogos` `bootstrap` `gmdl` `ios7` `android` `office` `signs` |
| **SaaS** | `salesforce` `sap` `atlassian` `ibm` `vvd` |
| **信息图** | `infographic` |

> **用法**：需要阿里云 IoT 图标时，先 `grep -i iot ~/.claude/skills/uml/stencils/alibaba_cloud.md`，拿到准确的 `mxgraph.*` 名字再用。凭记忆写图标名是最常见的渲染失败原因。

### 5.2 UML 范例（15 种图）

路径：`~/.claude/skills/uml/examples/`

```
activity-diagram          class-diagram              communication-diagram
component-diagram         composite-structure-diagram deployment-diagram
interaction-overview-diagram  object-diagram          package-diagram
profile-diagram           sequence-diagram           state-machine-diagram
swimlane-activity-diagram sysml-bdd                  use-case-diagram
```

画不熟悉的图类型前，先看对应范例文件，比读 SKILL.md 的语法表更快。

### 5.3 其他 skill 的子目录

| Skill | 子目录 | 内容 |
|---|---|---|
| `architecture` | `layouts/` `styles/` | HTML 布局与配色模板 |
| `infocard` | `layouts/` `styles/` | 卡片排版模板 |
| `infographic` | `references/` | **模板名清单**（选错会渲染失败，必查） |
| `canvas` | `references/` | JSON 结构参考 |
| `vega` | `references/` | 图表示例 |
| `graphviz` | `references/` | DOT 语法与布局参考 |
| `mindmap` | `examples/` | 脑图范例 |

---

## 6. 六阶段流程

> **本节讲"每阶段做什么"。要在 Claude Code 会话里实际驱动它们——每阶段该输入什么话、实际会发生什么、退出标准怎么核对、跑偏了怎么纠——见 [`design-doc-playbook-usage.md`](./design-doc-playbook-usage.md) 第 3~7 节。**

```
Phase 0  定边界        你 + 主线，不派 agent     → 设计约束清单（1 页）
Phase 1  能力分解      mindmap                  → 能力全景，防漏子系统
Phase 2  架构决策      Plan agent               → 服务拆分 / 选型 / 权衡 / 风险
Phase 3  骨架图        iot + cloud（串行）       → 总体架构图 + ★服务命名表★
Phase 4  细化图        并行委派 fork/agent       → 时序图 / 状态机 / 依赖图 / 数据链路 / 安全
Phase 5  组装          主线，不委派              → 完整文档 + 术语表 + 非功能需求 + 路线图
Phase 6  一致性审查    fresh agent（不给结论）    → 矛盾清单 → 修订
```

### Phase 0 · 定边界

**这一步不能委派** —— 信息在你脑子里。产出一页约束清单，之后每次委派都原样附上：

```
【设计约束清单 v1】
文档类型：概要设计（不下钻到接口字段、不写表结构）
读者：架构评审委员会 + 研发团队
部署环境：阿里云 ACK（K8s）+ 自建边缘节点，单 Region 双 AZ
规模指标：500 万设备长连接；上行峰值 20 万 msg/s；P99 端到端 < 500ms
可用性：核心链路 99.95%；单 AZ 故障不中断接入
合规：等保三级；设备数据不出境
技术栈约束：Java 17 + Spring Boot；消息队列用 Kafka（公司标准）
明确不做：视频流接入；边缘侧模型训练；多活容灾（本期）
已知既有系统：设备管理平台 v2（待改造，仓库在 xxx）
```

**没有这一页，后面所有图和文都会漂。** 这也是委派 prompt 里最不能省的部分。

### Phase 1 · 能力分解（`mindmap`）

把平台能力全量拆开，目的是**先有全景**：

```
设备接入 / 设备影子 / 设备管理 / 规则引擎 / 消息路由 /
时序存储 / 冷热分层 / 告警 / OTA / 开放 API / 租户与权限 /
运维可观测 / 安全（身份、传输、审计）/ 边缘运行时
```

产出物落盘到 `docs/design.md` 第 2 章。这一步能避免画到第 8 张图时发现有子系统没地方放。

### Phase 2 · 架构决策（派 `Plan`）

给 `Plan` 的东西：Phase 0 约束清单 + Phase 1 能力清单 + 你的具体问题。

要求它返回：
- 服务拆分方案（哪些独立部署、哪些合并、边界怎么划）
- 关键中间件选型（MQTT broker / 消息队列 / 时序库 / 缓存 / 流处理）
- **每个决策的权衡，以及被否掉的备选和否掉的理由**
- 风险清单与缓解措施
- 分阶段实施建议

> **概要设计的价值 80% 在这一章。** 图画得再漂亮，如果"为什么选 EMQX 不选 Mosquitto 集群""为什么用 TDengine 不用 InfluxDB"没写清楚，评审过不了。
> `Plan` 不能写文件，它返回文本，由主线落盘。

如果是要**改造既有系统**，Phase 2 之前先派 `Explore` 扫现有仓库，把结果一起喂给 `Plan`。

### Phase 3 · 骨架图（`iot` + `cloud`，必须串行且先做）

画 1~2 张主图：
- `iot`：Device → Edge → Cloud 总体架构
- `cloud`：阿里云上的部署（VPC、ACK、MQ、时序库、对象存储）

**这一步的真正产出是一张主图 + 一份副产品：服务命名表。**

```
【服务命名表 v1】（后续所有图必须逐字一致）
iot-access-gateway     设备接入网关（MQTT broker 前置）
device-shadow-svc      设备影子服务
rule-engine-svc        规则引擎
tsdb-writer            时序写入服务
alert-svc              告警服务
ota-svc                OTA 升级服务
openapi-gw             开放 API 网关
```

**为什么必须先做**：命名一旦在骨架图里定下，后面 6~10 张细化图都要沿用。如果并行画，每张图会各自发明名字（`access-gw` / `mqtt-proxy` / `device-gateway`），读者会以为是三个系统。

### Phase 4 · 细化图（并行委派）

到这里图之间彼此独立了，一条消息里发多个 Agent 调用，或用 `fork` 并行。

IoT 平台的典型细化图清单：

| 图 | Skill | 委派时要说清的问题 |
|---|---|---|
| 设备首次接入时序 | `uml` sequence | X.509 双向认证怎么完成、影子怎么建立、涉及哪四方、认证失败的重试与退避 |
| OTA 分批升级时序 | `uml` sequence | 灰度分批策略、失败回滚、断点续传 |
| 告警下发与确认时序 | `uml` sequence | 规则命中→去重→分级→通知→确认闭环 |
| 设备生命周期状态机 | `uml` state-machine | 未激活/在线/离线/OTA中/故障/已注销 的全部迁移与触发条件 |
| 微服务依赖图 | `graphviz` | 含故障传播路径，用 cluster 按域分组 |
| 数据链路 | `data-analytics` | 采集→Kafka→Flink→时序库→冷存→BI，标出吞吐和延迟 |
| 安全架构 | `security` | 设备身份、证书轮换、信任边界、审计流 |
| 现场网络拓扑 | `network` | 现场总线→边缘网关→专线→VPC（按需） |

### Phase 5 · 组装（回主线，不委派）

- 章节编排、图与正文的呼应（每张图前后都要有文字解释，不能只丢一张图）
- 术语表（缩写、服务名、状态名）
- 非功能需求：可用性设计、扩展性设计、**容量测算**、成本估算
- 演进路线：`infographic` 的 `sequence-roadmap-vertical-simple` 模板
- 容量/成本数据图表：先读 `dataviz`，再用 `vega`

**组装需要全局一致性，委派出去反而会散。**

### Phase 6 · 一致性审查（派 fresh agent，不给结论）

审查维度，可以各派一个 agent 并行：

| 维度 | 查什么 |
|---|---|
| 命名一致性 | 所有图里的服务名是否和 Phase 3 的命名表逐字一致 |
| 接口闭环 | 时序图里调用的每个接口，在组件图/依赖图里是否存在对应的边 |
| 数字自洽 | 各处容量、吞吐、延迟、可用性数字是否互相矛盾 |
| 需求覆盖 | Phase 1 的能力清单，是否每项都在架构里有落点 |
| 指标可支撑 | 非功能指标（99.95%、P99<500ms）是否有对应的架构手段，还是只是口号 |
| 渲染合规 | 所有 fence 名字对不对（第 3 节的表）；`architecture` 的 HTML 有没有空行 |

**关键：不给它你的判断。** 只给文档路径 + 约束清单 + 命名表 + "找矛盾"。

---

## 7. 委派 prompt 模板（可直接复制）

> 委派前必读 [`design-doc-playbook-usage.md`](./design-doc-playbook-usage.md) **第 2.3 节**：subagent 能 Read 文件但看不到你的对话、且 `Plan`/`Explore` 不能写文件。下面四个模板都建立在"先落盘、再给路径"这个前提上。

### 7.1 委派一张图

```
任务：为「云原生 IoT 平台概要设计」画一张 <图类型> 图，用 <skill 名> skill。

【设计约束清单】
<把 Phase 0 那一页原样粘进来>

【服务命名表】（图中所有服务名必须逐字使用下面的名字，不要另创）
<把 Phase 3 的命名表粘进来>

【这张图要回答的具体问题】
<一段话说清。例：设备首次接入时如何完成 X.509 双向认证并建立设备影子，
要体现 iot-access-gateway、认证服务、device-shadow-svc、tsdb-writer 四方交互，
以及认证失败时的重试与退避策略>

【产出要求】
- 写入 docs/design.md 的第 <N.M> 节，标题为「<节标题>」
- fence 标识符：PlantUML 系用 plantuml，graphviz 用 dot（见 playbook 第 3 节）
- 图前写 2~3 句引导文字，图后写 3~5 条要点说明（这张图想让人注意到什么）
- 图标名从 ~/.claude/skills/uml/stencils/<类别>.md 里查准确的，不要凭记忆写
- 不要修改文档的其他章节

【不要做】
- 不要重新设计架构（架构决策已定，见约束清单）
- 不要发明命名表里没有的服务
```

### 7.2 委派架构决策（给 `Plan`）

```
任务：为「云原生 IoT 平台」做概要设计层面的架构决策，返回方案文本（你不需要写文件）。

【设计约束清单】
<原样粘入>

【能力清单】
<Phase 1 的产出>

【既有系统情况】
<如果有，粘 Explore 的扫描结论；没有就写"全新建设">

【请返回】
1. 服务拆分方案：哪些独立部署、哪些合并、边界划分依据
2. 关键中间件选型：MQTT broker / 消息队列 / 时序库 / 缓存 / 流处理引擎，
   每项给出选择、理由、被否掉的备选及否掉的理由
3. 满足规模指标（500 万长连接、20 万 msg/s、P99<500ms）的关键设计手段
4. 满足 99.95% 可用性的具体机制（不是"多副本"这种口号）
5. 风险清单（技术风险 + 实施风险）与缓解措施
6. 分阶段实施建议与每阶段的验收标准

【要求】
- 决策要可辩驳：写出权衡，不要只写结论
- 不要给代码，不要画图（图在后续阶段单独做）
- 明确标出哪些决策你不确定、需要人工拍板
```

### 7.3 委派一致性审查（fresh agent）

```
任务：审查 docs/design.md 这份概要设计文档的内部一致性，只找矛盾，不改文件。

【参考基准】
设计约束清单：<粘入>
服务命名表：<粘入>

【逐条检查并报告】
1. 命名一致性：文中所有图（plantuml / dot / html 块）里出现的服务名，
   是否与命名表逐字一致。列出所有不一致处，给出所在节号。
2. 接口闭环：时序图里出现的每一次调用，在组件图/依赖图里是否有对应的边。
   列出孤立的调用。
3. 数字自洽：容量、吞吐、延迟、可用性、成本等数字，在文档不同位置是否矛盾。
   列出每一对矛盾及其位置。
4. 需求覆盖：能力清单里的每一项，是否能在架构中找到落点。列出无落点的项。
5. 指标支撑：非功能指标是否有具体的架构手段支撑。列出只有口号没有机制的指标。
6. 渲染合规：所有代码块的 fence 标识符是否正确
   （plantuml/puml、dot、vega-lite、canvas）；
   architecture 类的内嵌 HTML 里是否存在空行。

【输出格式】
按上面 6 项分节，每节列出：问题描述 + 所在节号/行号 + 建议修法。
没问题的项写"通过"。不要总结文档内容，不要评价设计好坏，只报矛盾。
```

### 7.4 委派调研（给 `general-purpose`）

```
任务：调研 <具体技术问题>，返回结论 + 依据，不要写文件。

【背景约束】
<粘入约束清单里相关的部分：规模、技术栈限制、合规要求>

【需要回答】
1. <候选方案 A/B/C> 在 <你的具体场景> 下的表现对比
2. 各自的运维复杂度、社区活跃度、生产案例
3. 明确的推荐 + 推荐理由 + 什么情况下推荐会翻转

【要求】
- 给出信息来源（链接或文档名），区分"实测数据"和"厂商宣称"
- 不确定的地方明确说不确定，不要用一般性描述填充
- 控制在 <N> 字以内
```

---

## 8. 按文档类型裁剪流程

不是每种文档都要走满六个阶段。

| 文档类型 | 保留阶段 | 主力 skill | 说明 |
|---|---|---|---|
| **概要设计**（本文示例） | 0-6 全套 | `mindmap` `iot`/`cloud` `uml` `graphviz` `data-analytics` | 重点在 Phase 2 的决策权衡 |
| **详细设计** | 0、3、4、6 | `uml`（class/sequence/state）、`graphviz` | Phase 2 已在概设里做完，直接细化；时序图和类图为主 |
| **技术方案 / 选型报告** | 0、2、5、6 | `infographic`（compare/swot/quadrant）、`vega`、`architecture` | 几乎不画图，重点是方案对比矩阵和数据图表 |
| **迁移 / 改造方案** | 0（+`Explore`）、2、3、4、6 | `cloud`（现状 vs 目标）、`bpmn`（迁移步骤）、`uml` deployment | **必须先用 `Explore` 扫现状**；画"现状架构"和"目标架构"两张对比图 |
| **企业架构 / 规划** | 0、1、2、5 | `archimate`、`mindmap`、`infographic`（roadmap） | 业务-应用-技术三层视角，读者是管理层 |
| **故障复盘 / RCA** | 0、4、5 | `uml` sequence、`graphviz`（故障传播）、`bpmn` | 时序图还原事件链是核心 |
| **对外技术白皮书** | 0、3、5 | `architecture`、`infocard`、`infographic` | 图要给非技术读者看懂，`architecture` 的分层色块最合适 |

### 裁剪原则

- **Phase 0 永远不能省。** 任何文档类型都要先有约束清单。
- **Phase 3 永远在 Phase 4 之前。** 命名表是所有多图一致性的前提。
- **超过 3 张图就该做 Phase 6。** 图越多，不一致的概率越高。
- **只有 1~2 张图时不用委派**，主线直接画，委派的开销大于收益。

---

## 9. 交付前检查清单

> 本清单是**交付前**的总核对。**每个阶段各自的退出标准**（判断"这一阶段可以结束了吗"）在 [`design-doc-playbook-usage.md`](./design-doc-playbook-usage.md) 第 3.4 / 4.3 / 5.3 / 6.5 节 —— 那些是阶段闸门，本清单是终点验收，两者不要混用。

### 流程
- [ ] Phase 0 的设计约束清单已成文，且每次委派都附上了
- [ ] Phase 3 的服务命名表已固定，细化图全部沿用
- [ ] 超过 3 张图时做过 Phase 6 一致性审查
- [ ] 审查用的 agent 没有拿到我的结论

### 图
- [ ] **`python3 -I scripts/check-diagrams.py docs/*.md` 退出码为 0**（机械闸门，覆盖 fence、括号、别名、图标名存在性、`cluster_` 前缀、`$schema`、节点数阈值）
- [ ] 每张图的 fence 标识符正确（`plantuml`/`puml`、`dot`、`vega-lite`、`canvas`）
- [ ] 自建组件没有借用云厂商托管产品图标（图标要反映**部署责任归属**，不只是"长得像什么"）
- [ ] 单图节点数 ≤ 25，超过则拆图或改用 `graphviz`
- [ ] `graphviz` 的子图都带 `cluster_` 前缀
- [ ] `vega` 图表都带 `$schema`，是合法 JSON
- [ ] `architecture` 的 HTML 是直接嵌入的（没有 fence），且内部无空行
- [ ] `infographic` 的模板名从 `references/` 清单里精确选取
- [ ] PlantUML 图标名是从 `stencils/` 查出来的，不是凭记忆写的
- [ ] `archimate` 图有 `!include <archimate/Archimate>`
- [ ] **每张图前后都有文字**：图前引导，图后要点说明。没有裸图
- [ ] 在 Markdown Viewer 里实际渲染过一遍，全部出图

### 内容
- [ ] 关键选型都写了权衡和被否掉的备选，不只写结论
- [ ] 每个非功能指标都有对应的架构手段，不是口号
- [ ] 文档各处的容量/吞吐/延迟/可用性数字自洽
- [ ] 能力清单里每一项都能在架构中找到落点
- [ ] 有术语表（缩写、服务名、状态名）
- [ ] 不确定的、需要人工拍板的决策已明确标出

### 落盘
- [ ] 图和正文在同一个 markdown 文件里（图源内联，可 diff）
- [ ] 文档进了版本控制
- [ ] 约束清单和命名表作为文档附录保留（下一版迭代要复用）

---

## 附：一句话流程

**约束清单 → 能力脑图 → Plan 出决策 → 骨架图定命名 → 并行画细化图 → 主线组装 → fresh agent 审矛盾。**

其中不能省的三件事：**Phase 0 的约束清单**、**Phase 3 的命名表**、**Phase 6 的不带结论审查**。
