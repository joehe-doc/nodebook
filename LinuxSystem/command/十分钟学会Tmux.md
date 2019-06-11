[![返回主页](https://www.cnblogs.com/Skins/custom/images/logo.gif)](https://www.cnblogs.com/kaiye/)

# [猫哥\_kaiye | 编程笔记](https://www.cnblogs.com/kaiye/)

*   [博客园](https://www.cnblogs.com/)
*   [首页](https://www.cnblogs.com/kaiye/)
*   [新随笔](https://i.cnblogs.com/EditPosts.aspx?opt=1)
*   [联系](https://msg.cnblogs.com/send/%E7%8C%AB%E5%93%A5_kaiye)
*   [订阅](https://www.cnblogs.com/kaiye/rss)
*   [管理](https://i.cnblogs.com/)

随笔 \- 78 文章 \- 0 评论 \- 144

# [十分钟学会 tmux](https://www.cnblogs.com/kaiye/p/6275207.html)

tmux 是一款终端复用命令行工具，一般用于 Terminal 的窗口管理。在 macOS 下，使用 iTerm2 能应付绝大多数窗口管理的需求。

![](https://images2015.cnblogs.com/blog/520689/201701/520689-20170111205923853-1701606139.png)

如上图所示，iTerm2 能新建多个标签页（快捷键 ⌘T），也能在同一个窗口中分割出多个窗格（快捷键 ⌘D 或 ⌘⇧D）。

tmux 相比 iTerm2 的优势在于：

*   iTerm2 的窗格切换快捷键（⌘⌥→）容易与其他软件全局快捷键冲突（例如 Spectacle 的窗口分割快捷键），tmux 由于存在前缀快捷键，所以不存在快捷键冲突问题；

*   tmux 可以在终端软件重启后通过命令行恢复上次的 session ，而终端软件则不行；

*   tmux 简洁优雅、订制性强，学会之后也能在 Linux 上使用，有助于逼格提升。

接下来我们花十分钟来掌握下 tmux 的基础用法：

## 安装运行

macOS 上使用 Homebrew 安装即可：

`brew install tmux`

安装完成后，运行 `tmux` 新建一个 tmux 的会话（session），此时窗口唯一的变化是在底部会出现一个 tmux 的状态栏。我们先按下 tmux 默认的前缀快捷键 `⌃b` 将其激活为快捷键接收模式，再按下 `%` ，即可将当前窗口切分为左右两个窗格。

![](https://images2015.cnblogs.com/blog/520689/201701/520689-20170111205933322-578444111.png)

## 快捷键

一般情况下 tmux 中所有的快捷键都需要和前缀快捷键 `⌃b` 来组合使用（注：⌃ 为 Mac 的 control 键），以下是常用的窗格（pane）快捷键列表，大家可以依次尝试下：

### 窗格操作

*   `%` 左右平分出两个窗格

*   `"` 上下平分出两个窗格

*   `x` 关闭当前窗格

*   `{` 当前窗格前移

*   `}` 当前窗格后移

*   `;` 选择上次使用的窗格

*   `o` 选择下一个窗格，也可以使用上下左右方向键来选择

*   `space` 切换窗格布局，tmux 内置了五种窗格布局，也可以通过 `⌥1` 至 `⌥5`来切换

*   `z` 最大化当前窗格，再次执行可恢复原来大小

*   `q` 显示所有窗格的序号，在序号出现期间按下对应的数字，即可跳转至对应的窗格

### 窗口操作

tmux 除了窗格以外，还有窗口（window） 的概念。依次使用以下快捷键来熟悉 tmux 的窗口操作：

*   `c` 新建窗口，此时当前窗口会切换至新窗口，不影响原有窗口的状态

*   `p` 切换至上一窗口

*   `n` 切换至下一窗口

*   `w` 窗口列表选择，注意 macOS 下使用 `⌃p` 和 `⌃n` 进行上下选择

*   `&` 关闭当前窗口

*   `,` 重命名窗口，可以使用中文，重命名后能在 tmux 状态栏更快速的识别窗口 id

*   `0` 切换至 0 号窗口，使用其他数字 id 切换至对应窗口

*   `f` 根据窗口名搜索选择窗口，可模糊匹配

![](https://images2015.cnblogs.com/blog/520689/201701/520689-20170111205944010-1132178011.png)

### 会话操作

如果运行了多次 `tmux` 命令则会开启多个 tmux 会话（session）。在 tmux 会话中，使用前缀快捷键 `⌃b` 配合以下快捷键可操作会话：

*   `$` 重命名当前会话

*   `s` 选择会话列表

*   `d` detach 当前会话，运行后将会退出 tmux 进程，返回至 shell 主进程

在 shell 主进程下运行以下命令可以操作 tmux 会话：

tmux new \-s foo # 新建名称为 foo 的会话
tmux ls # 列出所有 tmux 会话
tmux a # 恢复至上一次的会话
tmux a \-t foo # 恢复名称为 foo 的会话，会话默认名称为数字
tmux kill\-session \-t foo # 删除名称为 foo 的会话
tmux kill\-server # 删除所有的会话

除以上提到的快捷键以外，tmux 还有许多其他的快捷键和命令，使用前缀快捷键 `⌃b` 加 `?` 可以查看所有的快捷键列表，该列表视图为 **tmux copy 模式**，该模式下可使用以下快捷键（无需加 `⌃b` 前缀）：

*   `⌃v` 下一页

*   `Meta v` 上一页 （tmux 快捷键为 Emacs 风格，这里的 Meta 键可用 Esc 模拟）

*   `⌃s` 向前搜索

*   `q` 退出 copy 模式

## 常见配置与问题

### 1、鼠标滚屏

tmux 默认配置中最糟糕的体验就是滚屏查看和文本复制（大家可以先试试看）。你需要先使用 `⌃b` `[` 快捷键进入 copy 模式，然后使用翻页、字符定位来选择需要的字符，效率远没有鼠标选择来的快。

因此 tmux 提供了一些个性化配置项来优化这些配置，首先在 shell 中运行 `touch ~/.tmux.conf` 新建用户配置文件。在文件中增加以下内容：

[![复制代码](https://common.cnblogs.com/images/copycode.gif)](javascript:void(0); "复制代码")

\# 开启鼠标模式
set \-g mode\-mouse on
​
# 允许鼠标选择窗格
set \-g mouse\-select\-pane on
​
# 如果喜欢给窗口自定义命名，那么需要关闭窗口的自动命名
set\-option \-g allow\-rename off
​
# 如果对 vim 比较熟悉，可以将 copy mode 的快捷键换成 vi 模式
set\-window\-option \-g mode\-keys vi

[![复制代码](https://common.cnblogs.com/images/copycode.gif)](javascript:void(0); "复制代码")

配置文件修改完成后，可以 `tmux kill-server` 重启所有 tmux 进程，或者在 tmux 会话中使用 `⌃b` `:` 进入控制台模式，输入 `source-file ~/.tmux.conf` 命令重新加载配置。

### 2、鼠标复制

tmux 下开启鼠标滚屏后，复制文本有两种方式：

*   方法 1：使用 `⌃b` `z` 进入窗格全屏模式，鼠标选择文本的同时按住 option 键 `⌥`，然后使用 `⌘c` 进行复制；

*   方法 2：开启 iTerm2 「在选择时复制」选项，即可实现自动选择复制。如下图：

![](https://images2015.cnblogs.com/blog/520689/201701/520689-20170111210013541-836018258.png)

### 3、tips

*   [screen](http://hyperpolyglot.org/multiplexers) 是另外一款终端复用命令行，但他没有 tmux 好看好用；

*   [tmux 有个 bug](https://github.com/ChrisJohnsen/tmux-MacOSX-pasteboard#mac-os-x-pasteboard-access-under-tmux-and-screen) ，导致从它启动的 vscode 的复制粘贴快捷键会失效；

*   iTerm2 可以通过 「Preferences \-> Profiles \-> Keyboard Behavior \-> Left option key acts as +Esc」将键盘的左侧 option 键映射为 Meta 键

另外，最近看到两篇不错的 [awk](https://github.com/mylxsw/growing-up/blob/master/doc/%E4%B8%89%E5%8D%81%E5%88%86%E9%92%9F%E5%AD%A6%E4%BC%9AAWK.md)、[sed](https://github.com/mylxsw/growing-up/blob/master/doc/%E4%B8%89%E5%8D%81%E5%88%86%E9%92%9F%E5%AD%A6%E4%BC%9ASED.md) 命令入门，感兴趣的同学可以自己看一下。

