# Playbook 使用手册 —— 如何驱动 Phase 0~3

> 本手册解决**操作层面**的问题：在 Claude Code 会话里，每个阶段具体输入什么、实际会发生什么、怎么判断这一阶段可以结束了。
> 覆盖范围：Phase 0~3（定边界 → 能力分解 → 架构决策 → 骨架图）。Phase 4~6 的机制差异见第 8 节。

## 配套文档

| 文档 | 回答什么问题 | 什么时候看 |
|---|---|---|
| **本文**（`design-doc-playbook-usage.md`） | **怎么驱动** —— 逐阶段的输入话术、实际发生什么、退出标准、常见跑偏 | **实际开工时摊在旁边**，照着念 |
| **[`design-doc-playbook.md`](./design-doc-playbook.md)** | **做什么** —— 六阶段流程、skill 选型速查表、fence 格式硬规则、委派 prompt 模板、检查清单 | 规划阶段；委派时抄第 7 节模板 |
| [`ai-agent-development-guide.md`](./ai-agent-development-guide.md) | 被设计的对象本身是 AI Agent 时的领域知识 | 仅当设计文档主题是 Agent / LLM 应用 |

**本手册各节大量引用 playbook 的具体章节**，两边要对着看：

| 本手册 | 需要同时翻 playbook 的 |
|---|---|
| 2.1 skill 上下文成本 | 第 1.3 节（同一份数据，playbook 侧是完整版） |
| 2.2 stencils 必须 grep | **第 5.1 节**（61 类图标库分类表） |
| 3.1 Phase 0 输入话术 | **Phase 0 的约束清单模板**（第 6 节内） |
| 4.2 mindmap 格式规则 | **第 3 节**（fence 与格式硬规则全表） |
| 5.1 Phase 2 委派 | **第 7.2 节**（`Plan` 委派 prompt 模板） |
| 6.1 Phase 3 委派 | **第 2.1 节**（图类型 → skill 选型表） |
| 7 常见跑偏 | **第 3 节**（fence 对照表） |
| 8 Phase 4~6 机制 | **第 7.1 / 7.3 / 7.4 节**（委派模板）、**第 4 节**（agent 能力边界） |
| 9.2 产出文件对照 | **第 6 节**（六阶段流程图） |
| 交付前总验收 | **第 9 节**（交付前检查清单） |

> 实跑记录见 [`iot-design/`](./iot-design/) —— 用一份虚构但自洽的约束（分布式光伏储能监控平台）走完 Phase 0~3 的产出，可作为格式参照。

---

## 目录

- [1. 开工前准备](#1-开工前准备)
- [2. 三条通用机制（不懂就会每阶段跑偏）](#2-三条通用机制不懂就会每阶段跑偏)
- [3. Phase 0 · 定边界](#3-phase-0--定边界)
- [4. Phase 1 · 能力分解](#4-phase-1--能力分解)
- [5. Phase 2 · 架构决策](#5-phase-2--架构决策)
- [6. Phase 3 · 骨架图与命名表](#6-phase-3--骨架图与命名表)
- [7. 常见跑偏与纠正](#7-常见跑偏与纠正)
- [8. Phase 4~6 的机制差异](#8-phase-46-的机制差异)
- [9. 速查](#9-速查)

---

## 1. 开工前准备

### 1.1 目录结构

```
你的项目/
├── design-doc-playbook.md        # 流程与速查表（复制进项目，或用绝对路径引用）
├── design-doc-playbook-usage.md  # 本手册
├── CLAUDE.md                     # 放 playbook 指针（见 1.2）
├── docs/
│   └── design.md                 # 设计文档主体（最终交付物）
└── design/                       # ★ 阶段产出，每个阶段一个小文件
    ├── 00-constraints.md         # Phase 0：设计约束清单
    ├── 01-capability-map.md      # Phase 1：能力脑图
    ├── 01b-current-state.md      # （仅改造项目）Explore 扫描结论
    ├── 02-decisions.md           # Phase 2：架构决策
    └── 03-naming-table.md        # Phase 3：服务命名表
```

**为什么阶段产出要单独成文件，而不是都写进 `docs/design.md`**

因为 Phase 4 每次委派都要把「约束清单」和「命名表」交给 subagent（playbook 7.1 模板）。单独成小文件之后，委派只需给**路径**，不必复制粘贴大段文本。

这也和 2.3 节的委派机制直接相关：subagent 看不到你的对话，但能读磁盘上的文件。**先落盘、再给路径**是整个流程能跑顺的前提。

### 1.2 让 playbook 在每个会话里生效

**方式 A（推荐）** —— 在项目 `CLAUDE.md` 里加一行指针：

```markdown
## 设计文档

写设计文档时，先读 design-doc-playbook.md，按其中的六阶段流程执行。
驱动方式见 design-doc-playbook-usage.md。
```

这样每次新会话自动加载，你只要说"跑 Phase 2"。

**方式 B** —— 每次开工第一句显式引用：

```
先读 /绝对路径/design-doc-playbook.md 和 design-doc-playbook-usage.md，
然后按流程跑 Phase 0。项目是云原生 IoT 平台概要设计。
```

### 1.3 渲染环境

图表 skill 的产出是**带特定 fence 的 markdown 代码块**，由 **Markdown Viewer** 扩展（docu.md，Chrome / Edge / Firefox / VS Code）渲染。

| 需要 | 不需要 |
|---|---|
| 装 Markdown Viewer 扩展 | 本地 `plantuml` / `dot` / `java` |
| | 把图源另存为 `.puml` 文件（已内联在 md 里） |

只有要**导出 PNG/SVG 进 Word/PPT**、或走 **CI 自动出图**时，才需要本地工具链：

```bash
sudo apt install graphviz plantuml
```

---

## 2. 三条通用机制（不懂就会每阶段跑偏）

### 2.1 Skill 是"加载进上下文的写作规范"，不是可执行程序

调用 `Skill(skill="uml")` 做的事，是把 `~/.claude/skills/uml/SKILL.md` 的规范加载进模型上下文，然后**按规范往 markdown 里写一段带特定 fence 的代码块**。

没有"运行 skill 得到一张图片"这回事。产出永远是 markdown 文本。

**唤起 skill 很便宜**（只加载 SKILL.md，不加载 `stencils/` 和 `examples/`）：

- 最重的 `infocard` ≈ 7.8K token，`architecture` ≈ 4.5K
- 常用的图表 skill（`uml` `cloud` `iot` `mindmap` `graphviz` `data-analytics` `security`）每个都在 **0.7K~2.1K**
- 16 个全唤起也才 ~37K token；一份设计文档常用的 5~6 个加起来不到 10K，**不用省着用**

> 完整逐 skill 数据见 [`design-doc-playbook.md`](./design-doc-playbook.md) **第 1.3 节**——那是唯一数据源，本处只做摘要，避免两份表漂移。

### 2.2 真正贵的是图标索引 —— 必须 grep，不能整读

`stencils/` 下的文件是按需读取的，而且很大——最大的 `aws4.md` ≈ **19.5K token**，`electrical.md` ≈ 12.2K，`cisco_safe.md` ≈ 11.3K，云原生生常用的 `alibaba_cloud.md` ≈ 6.6K、`gcp2.md` ≈ 6.3K。

> **读整个 `aws4.md` 一次吃掉 ~19.5K token，比唤起全部 16 个 skill 的一半还多。**
> 完整清单见 [`design-doc-playbook.md`](./design-doc-playbook.md) 第 1.3 节；61 类图标的分类索引见其**第 5.1 节**。

正确做法：

```bash
grep -i "iot\|device\|gateway" ~/.claude/skills/uml/stencils/alibaba_cloud.md
```

好处不只是省 token —— 更避免了模型在几百个相似图标名里选错。**凭记忆写 `mxgraph.*` 图标名是"不报错但渲染成方框"的头号原因。**

相反，`examples/` 很便宜（最大的 `sequence-diagram.md` 只有 4.8K 字节），画不熟悉的图类型前**应该**读对应范例。

### 2.3 委派机制：subagent 能读文件，但看不到你的对话，也不能写文件

这是最容易搞错的一条，直接决定委派 prompt 怎么写。

| 能力 | `Plan` | `Explore` | `fork` | `general-purpose` |
|---|:---:|:---:|:---:|:---:|
| 看到你当前会话的对话历史 | ✗ | ✗ | **✓** | ✗ |
| 读磁盘上的文件（Read/Bash/Grep/Glob） | ✓ | ✓ | ✓ | ✓ |
| 写文件（Edit/Write） | ✗ | ✗ | ✓ | ✓ |

三条推论：

1. **委派靠给路径，不靠粘贴内容。** subagent 读不到对话，但读得到 `design/00-constraints.md`。所以"把上下文传给它"的正确做法是先落盘、再给路径。
2. **`Plan` / `Explore` 的产出必须由主线落盘。** 它们返回文本，然后由你（主线）写进文件。让 `Plan` "直接写到 02-decisions.md" 会失败。
3. **只有 `fork` 继承上下文。** 想让子任务少交代背景，用 `fork`；想要一个不带偏见的独立视角（比如 Phase 6 审查），用非 fork 的 fresh agent。

---

## 3. Phase 0 · 定边界

**产出**：`design/00-constraints.md`
**派 agent**：不派
**唤起 skill**：不唤起
**性质**：对话式采集 —— 这是全流程**唯一一步信息只在你脑子里**

### 3.1 你要输入什么

```
跑 Phase 0。项目：云原生 IoT 平台概要设计。

我先说我知道的，你按 playbook Phase 0 的模板整理成 design/00-constraints.md。
缺的字段逐条问我，不要替我猜、不要填默认值。

- 读者：架构评审委员会 + 研发团队
- 部署：阿里云 ACK，单 Region 双 AZ
- 规模：目标 500 万设备长连接，上行峰值 20 万 msg/s
- 公司标准：Java 17 + Spring Boot，消息队列必须用 Kafka
- 本期不做：视频流接入、边缘侧模型训练
```

**"缺的字段逐条问我，不要替我猜"这句不能省。** 约束清单有 9 个字段，通常你只会主动想到 5 个，剩下 4 个恰恰是后面最容易返工的。

### 3.2 实际会发生什么

不派 agent、不唤起 skill，纯对话。Claude 把你口述的内容归位到 playbook 的模板，然后反问缺失项。典型追问：

| 追问 | 为什么这项不能空 |
|---|---|
| "P99 端到端延迟目标是多少？" | 没有这个数字，接入层和消息队列的选型无法收敛 |
| "可用性目标是 99.9% 还是 99.95%？" | 差别在于是否需要跨 AZ 自动切换，直接影响架构 |
| "有等保 / 数据出境要求吗？" | 影响时序库和对象存储的部署位置 |
| "全新建设还是改造既有系统？" | 决定要不要在 Phase 2 前插一次 `Explore` 扫描 |
| "容量数字是当前值还是三年目标？" | 按当前值设计会导致一年内重构 |

### 3.3 产出格式

```markdown
# 设计约束清单 v1

文档类型：概要设计（不下钻到接口字段、不写表结构）
读者：架构评审委员会 + 研发团队
部署环境：阿里云 ACK（K8s）+ 自建边缘节点，单 Region 双 AZ
规模指标：500 万设备长连接；上行峰值 20 万 msg/s；P99 端到端 < 500ms
可用性：核心链路 99.95%；单 AZ 故障不中断接入
合规：等保三级；设备数据不出境
技术栈约束：Java 17 + Spring Boot；消息队列用 Kafka（公司标准）
明确不做：视频流接入；边缘侧模型训练；多活容灾（本期）
既有系统：设备管理平台 v2（待改造，仓库在 xxx）
```

### 3.4 退出标准

- [ ] 9 个字段全部填实，没有"待定" / "TBD"
- [ ] **规模指标是数字**，不是"大规模""高并发"
- [ ] **"明确不做"至少 2 条** —— 这栏空着，后面一定范围蔓延
- [ ] 已确认新建还是改造（决定要不要插 `Explore`）

> **没有这一页，后面所有图和文都会漂。** 它也是 Phase 4 每次委派 prompt 里最不能省的部分。

---

## 4. Phase 1 · 能力分解

**产出**：`design/01-capability-map.md`
**派 agent**：不派（主线直接做）
**唤起 skill**：`mindmap`

### 4.1 你要输入什么

```
跑 Phase 1。读 design/00-constraints.md，用 mindmap skill 把平台能力全量分解，
写入 design/01-capability-map.md。

要求：
- 分解到"能独立判断本期做不做"的粒度
- 不要出现"其他""misc"这类兜底分类
- 每个一级能力标注本期是否交付（对照约束清单的"明确不做"）
```

### 4.2 实际会发生什么

1. `Skill(skill="mindmap")` → 加载 SKILL.md（~2.1K token）
2. 读 `design/00-constraints.md`
3. 写一个 plantuml fence 块，内含 `@startmindmap ... @endmindmap`
4. 落盘

产出示意：

```
@startmindmap
* 云原生 IoT 平台
** 设备接入
*** 多协议适配（MQTT / CoAP / HTTP）
*** 连接管理与心跳
*** 设备认证（X.509 / 一机一密）
** 设备管理
*** 设备影子
*** 分组与标签
*** OTA 升级
** 数据链路
*** 规则引擎
*** 消息路由
*** 时序存储与冷热分层
** 运维与安全
*** 可观测性
*** 租户与权限
*** 审计
@endmindmap
```

> `mindmap` 的格式规则：层级用 `*` / `**` / `***` **或** `+` / `-`，**同一分支内不要混用两种风格**；`left side` 可把后续分支切到左侧。fence 必须是 plantuml，写 text 不渲染。

### 4.3 退出标准

- [ ] 约束清单里"明确不做"的项在脑图里被标注为不交付（而不是凭空消失）
- [ ] 没有兜底分类
- [ ] **你扫一眼能确认没漏掉关心的子系统**

最后一条是这一步的全部价值。此处漏掉的子系统，到 Phase 4 才发现，就要回头改架构图和命名表。

---

## 5. Phase 2 · 架构决策

**产出**：`design/02-decisions.md`
**派 agent**：`Plan`（改造项目再加一次 `Explore`）
**唤起 skill**：不唤起

> playbook 里那句"概要设计的价值 80% 在这一章"就是这个意思。图画得再漂亮，这一章空了就是一份 PPT。

### 5.1 你要输入什么

```
跑 Phase 2。派 Plan agent 做架构决策。

给它这些路径（它能自己读，不要粘贴内容）：
- design/00-constraints.md
- design/01-capability-map.md

要求它按 playbook 7.2 模板返回 6 项。
它返回文本后，由你写入 design/02-decisions.md（Plan 没有写权限）。
不要让它画图。
```

如果是**改造既有系统**，在这之前加一步：

```
先派 Explore 扫描 <仓库路径>，产出：现有服务清单、技术栈、
模块边界、已知的耦合点和技术债。写入 design/01b-current-state.md。
```

然后 Phase 2 的 prompt 里多给一个路径 `design/01b-current-state.md`。

### 5.2 实际会发生什么

1. `Agent(subagent_type="Plan", ...)` 派出去，prompt 含：文件路径 + playbook 7.2 的六项要求
2. `Plan` 自己 `Read` 那两个文件（它读得到磁盘，读不到你们的对话）
3. `Plan` 返回方案文本
4. **回到主线**，由主线落盘到 `design/02-decisions.md`

要求 `Plan` 返回的六项：

| # | 内容 |
|---|---|
| 1 | 服务拆分方案：哪些独立部署、哪些合并、边界划分依据 |
| 2 | 关键中间件选型（MQTT broker / MQ / 时序库 / 缓存 / 流处理），每项含**被否掉的备选及理由** |
| 3 | 满足规模指标的关键设计手段 |
| 4 | 满足可用性目标的**具体机制** |
| 5 | 风险清单（技术 + 实施）与缓解措施 |
| 6 | 分阶段实施建议与每阶段验收标准 |

### 5.3 退出标准

- [ ] **每个选型都写了"被否掉的备选 + 否掉的理由"** —— 只写结论的决策文档过不了评审
- [ ] 每个非功能指标都对应到具体机制，不是"多副本部署"这种口号
- [ ] 明确标出了"我不确定、需要人工拍板"的项
- [ ] **你已经就那些待拍板项做了决定，并回写进文件**

最后一条最容易被跳过。`Plan` 标出的不确定项如果不当场拍板，Phase 3 画图时会各画各的假设，Phase 6 审查才发现矛盾。

---

## 6. Phase 3 · 骨架图与命名表

**产出**：`docs/design.md` 第 3 章（两张图）+ `design/03-naming-table.md`
**派 agent**：不派（**必须串行，不能并行**）
**唤起 skill**：`iot` → `cloud`（或按部署环境换成 `architecture`）

### 6.1 你要输入什么

```
跑 Phase 3。读 design/00-constraints.md 和 design/02-decisions.md。

严格串行，两张图：
1. 用 iot skill 画 Device→Edge→Cloud 总体架构
2. 用 cloud skill 画阿里云部署架构（VPC / ACK / Kafka / 时序库 / OSS）

两张都写入 docs/design.md 第 3 章。
每张图前写 2~3 句引导文字，图后写 3~5 条要点说明（这张图想让人注意到什么）。

画完后从这两张图的源码里【抽取】所有服务与组件名，生成 design/03-naming-table.md。
命名表必须是图里实际出现的名字，不要另创。

图标名用 grep 从 stencils 里查准确的：
  grep -i "<关键词>" ~/.claude/skills/uml/stencils/alibaba_cloud.md
不要整个文件读进来，不要凭记忆写图标名。
```

### 6.2 实际会发生什么

1. `Skill(skill="iot")`（~1.8K token）→ 读约束和决策 → grep 查图标名 → 写 plantuml 块
2. `Skill(skill="cloud")`（~1.4K token）→ 同上，画部署架构
3. 从两张图源码里提取所有 `rectangle` / `component` / `node` 的名字 → 生成命名表

### 6.3 为什么命名表要"抽取"而不是"先写"

如果先写命名表再画图，两者会漂移（画图时顺手改了个更顺口的名字）。**从已画好的图里抽取，一致性是天然保证的。**

产出示意：

```markdown
# 服务命名表 v1

> 后续所有图（时序图、组件图、数据流图、安全图）必须逐字使用下列名称。
> 新增服务时先更新本表，再画图。

| 名称 | 职责 | 出现在 |
|---|---|---|
| iot-access-gateway | 设备接入网关，MQTT 协议终结 | 图 3-1、3-2 |
| device-auth-svc | X.509 双向认证、一机一密 | 图 3-1、3-2 |
| device-shadow-svc | 设备影子读写 | 图 3-1 |
| rule-engine-svc | 消息规则匹配与路由 | 图 3-1 |
| tsdb-writer | 时序数据落盘 | 图 3-1、3-2 |
| openapi-gw | 对外开放 API 网关 | 图 3-2 |
```

### 6.4 为什么必须串行、必须在 Phase 4 之前

命名表是 Phase 4 能**并行**的前提。

没有它，6~10 张细化图会各自发明名字（`access-gw` / `mqtt-proxy` / `device-gateway` 指同一个东西），读者会以为是三个系统。这个矛盾要到 Phase 6 审查才暴露，届时改图的成本远高于串行画两张骨架图。

### 6.5 退出标准

**先跑机械闸门**（脚本化，不靠自觉）：

```bash
python3 -I scripts/check-diagrams.py docs/design.md
# 退出码 0 = 通过；1 = 有错误，逐条修完再跑
```

`scripts/check-diagrams.py` 校验 8 项：fence 标识符合法性、`@start*/@end*` 配对、花括号配对、**边中引用的别名已定义**、**`mxgraph` 图标名在 stencils 中真实存在**、graphviz 的 `cluster_` 前缀、vega 的 `$schema`、单图节点数阈值（默认 25，超过则提示拆图或改用 `graphviz`）。

> 这个脚本是 `iot-design/` 实跑时补上的，因为**凭记忆写图标名的实测失败率是 4/4 = 100%**，而这类错误不报错、只渲染成空框。脚本已通过反向测试（故意写错的图能被全部抓出）。
> **但它不等于渲染验证**：布局是否可读、连线是否糊成一团，仍需目视检查。

**再核对人工项**：

- [ ] 命名表里每个名字**都在至少一张图里出现过**（无幽灵服务）
- [ ] 两张图里**没有同物异名**
- [ ] 命名表是用 `grep` 从图里**抽取**的，不是另行命名的（见 6.3）
- [ ] 在 Markdown Viewer 里实际渲染过，两张图都出图（不是方框）
- [ ] 每张图前后都有文字，没有裸图
- [ ] 图中出现的服务，都能在 `02-decisions.md` 里找到对应的决策依据
- [ ] **自建组件没有借用云厂商托管产品图标**（如用 `alibaba_cloud.kafka` 表示自建 Apache Kafka——名字有效但语义错误，会让读者误以为有云厂商 SLA 兜底）

**过了这一步，Phase 4 才可以并行。**

---

## 7. 常见跑偏与纠正

| 症状 | 原因 | 纠正 |
|---|---|---|
| Phase 0 直接开始猜规模数字 | 没说"缺的问我，不要猜" | 约束清单里任何数字都必须来自你 |
| Phase 0 产出只有 5 个字段 | 模板没被完整对照 | 明确要求对照 playbook Phase 0 的 9 字段模板 |
| 派出去的 `Plan` 返回很泛的建议 | prompt 里没给路径，它读不到约束 | 明确给 `design/00-constraints.md` 路径 |
| `Plan` 说"我无法写入文件" | 它本来就没有 Write 权限 | 正常行为。让它返回文本，主线落盘 |
| 想把对话里的背景直接讲给 subagent 听 | 非 fork 的 subagent 看不到对话 | 先落盘成文件，再给路径；或用 `fork` |
| Phase 3 两张图的服务名不一样 | 并行画了，或命名表不是从图里抽的 | Phase 3 必须串行；命名表在两张图**之后**抽取 |
| 图在编辑器里不渲染 | fence 写成了 text 或 graphviz | 查 playbook 第 3 节的 fence 对照表 |
| PlantUML 图标显示成方框 | 图标名凭记忆写的 | `grep -i` 查 `stencils/<类别>.md` |
| 上下文突然涨了很多 | 整个读了 `aws4.md` 之类的索引文件 | 改用 grep，见 2.2 节 |
| 每阶段产出都堆在 `docs/design.md` 里 | 没建 `design/` 目录 | 阶段产出单独成文件，否则 Phase 4 委派只能靠粘贴 |
| Phase 2 的不确定项没拍板就进 Phase 3 | 跳过了退出标准最后一条 | 回 5.3 节，当场决定并回写 |

---

## 8. Phase 4~6 的机制差异

Phase 0~3 是**串行**的，每一阶段的产出是下一阶段的输入。Phase 4 开始机制变了：

| 阶段 | 并行性 | 委派方式 | 关键差异 |
|---|---|---|---|
| Phase 4 细化图 | **可并行** | 一条消息里发多个 `Agent` 调用，或用 `fork` | 每个委派 prompt 必须含：约束清单路径 + 命名表路径 + 这张图要回答的**具体问题** + 用哪个 skill + 写进哪个文件哪一节 |
| Phase 5 组装 | **不要并行** | 主线自己做 | 需要全局一致性，委派出去会散 |
| Phase 6 审查 | 可按维度并行 | 派 **fresh agent（非 fork）** | **故意不给它你的结论**，否则它会回来确认你，审查就白做了 |

Phase 4 委派最容易写废的地方是"这张图要回答的具体问题"：

| 废指令 | 可用指令 |
|---|---|
| "画一个设备上线时序图" | "画时序图说明设备首次接入时如何完成 X.509 双向认证并建立设备影子，要体现 `iot-access-gateway`、`device-auth-svc`、`device-shadow-svc`、`tsdb-writer` 四方交互，以及认证失败时的重试与退避策略" |

四个可直接复制的委派 prompt 模板在 playbook 第 7 节：7.1 画一张图 / 7.2 要架构决策 / 7.3 一致性审查 / 7.4 技术调研。

---

## 9. 速查

### 9.1 四步一句话

**Phase 0** 对话采集（不许猜）→ **Phase 1** `mindmap` 分解 → **Phase 2** 派 `Plan` 给路径做决策 → **Phase 3** 串行画两张骨架图并从中抽命名表。

### 9.2 产出文件对照

| 阶段 | 产出文件 | 派 agent | 唤起 skill | 并行 |
|---|---|---|---|:---:|
| 0 | `design/00-constraints.md` | — | — | — |
| （改造） | `design/01b-current-state.md` | `Explore` | — | — |
| 1 | `design/01-capability-map.md` | — | `mindmap` | — |
| 2 | `design/02-decisions.md` | `Plan` | — | — |
| 3 | `docs/design.md` 第 3 章 + `design/03-naming-table.md` | — | `iot` → `cloud` | **禁止** |
| 4 | `docs/design.md` 第 4~8 章 | `fork` / `general-purpose` | `uml` `graphviz` `data-analytics` `security` … | **可以** |
| 5 | `docs/design.md` 全文 | — | `infographic` `vega` | **禁止** |
| 6 | 矛盾清单 → 修订 | fresh agent（非 fork） | — | 可按维度 |

### 9.3 每个阶段开口第一句

```
Phase 0：跑 Phase 0。项目：<名称>。我先说我知道的，你按模板整理成
         design/00-constraints.md，缺的字段逐条问我，不要替我猜。

Phase 1：跑 Phase 1。读 design/00-constraints.md，用 mindmap skill 分解能力，
         写入 design/01-capability-map.md。不要兜底分类。

Phase 2：跑 Phase 2。派 Plan agent，给它 design/00-constraints.md 和
         design/01-capability-map.md 的路径，按 playbook 7.2 返回六项，
         你负责落盘到 design/02-decisions.md。

Phase 3：跑 Phase 3。读 00 和 02，严格串行画总体架构图和部署架构图，
         写入 docs/design.md 第 3 章，然后从图里抽命名表到
         design/03-naming-table.md。图标名用 grep 查 stencils。
```

### 9.4 三条不能省的机制

1. **阶段产出各自成小文件** —— 否则 Phase 4 委派只能靠粘贴大段文本。
2. **委派靠给路径，不靠粘贴** —— subagent 能 Read，但看不到你的对话。
3. **Phase 3 的命名表从图里抽取** —— 这是 Phase 4 能并行的唯一前提。
