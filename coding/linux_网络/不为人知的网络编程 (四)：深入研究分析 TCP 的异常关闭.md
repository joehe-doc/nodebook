> 本文由 [简悦 SimpRead](http://ksria.com/simpread/) 转码， 原文地址 [www.52im.net](http://www.52im.net/thread-1014-1-1.html)

[![][img-0]

原作者：腾讯互娱谢代斌，由即时通讯网重新整理发布，感谢原作者的无私分享。

1、前言
----

研究测试 TCP 断开和异常的各种情况，以便于分析网络应用（比如 tconnd）断网的原因和场景，帮组分析和定位连接异常掉线的问题，并提供给 TCP 相关的开发测试人员作为参考。

各个游戏接入都存在一定的掉线问题，而且有的游戏项目的掉线比例还比较高，现在腾讯互娱自研游戏的网络接入基本上都用的是 tconnd 和 ProtocalHandler 组件（该组件请参考附件《TSF4G_ProtocalHandler 开发指导手册》），因此有幸参与了其掉线原因分析和研究。

在参与 A 项目的掉线问题研究分析过程中，tconnd 增加了玩家每个连接的流水日志和 ProtocalHandler 增加了每个连接的 Qos 上报日志，通过这些日志记录了每一次连接的断开原因和相关统计数据，其中包括了连接异常断开时 TCP 的底层错误码。

通过对 tconnd 的流水日志和 ProtocalHandler 的 Qos 日志进行统计分析，发现连接异常断开时 TCP 的错误码大部分是 “

104: Connection reset by peer”（Linux 下）或 “10054: An existing connection was forcibly closed by the remote host

”（Windows 下），单纯从错误码本来来说，大家都明白是 “网络被对端重置了”，但究竟什么情况下会导致这种情况呢？因此本文就对 TCP 的各种关闭情况做了进一步的测试研究。

2、系列文章
------

**本文是系列文章中的第 4 篇，本系列文章的大纲如下：**

*   《[不为人知的网络编程 (一)：浅析 TCP 协议中的疑难杂症 (上篇)](http://www.52im.net/thread-1003-1-1.html)》
*   《[不为人知的网络编程 (二)：浅析 TCP 协议中的疑难杂症 (下篇)](http://www.52im.net/thread-1004-1-1.html)》
*   《[不为人知的网络编程 (三)：关闭 TCP 连接时为什么会 TIME_WAIT、CLOSE_WAIT](http://www.52im.net/thread-1007-1-1.html)》
*   《[不为人知的网络编程 (四)：深入研究分析 TCP 的异常关闭](http://www.52im.net/thread-1014-1-1.html)》（本文）
*   《[不为人知的网络编程 (五)：UDP 的连接性和负载均衡](http://www.52im.net/thread-1018-1-1.html)》
*   《[不为人知的网络编程 (六)：深入地理解 UDP 协议并用好它](http://www.52im.net/thread-1024-1-1.html)》
*   《[不为人知的网络编程 (七)：如何让不可靠的 UDP 变的可靠？](http://www.52im.net/thread-1293-1-1.html)》
*   《[不为人知的网络编程 (八)：从数据传输层深度解密 HTTP](http://www.52im.net/thread-2456-1-1.html)》
*   《[不为人知的网络编程 (九)：理论联系实际，全方位深入理解 DNS](http://www.52im.net/thread-2740-1-1.html)》
*   《[不为人知的网络编程 (十)：深入操作系统，从内核理解网络包的接收过程 (Linux 篇)](http://www.52im.net/thread-3247-1-1.html)》
*   《[不为人知的网络编程 (十一)：从底层入手，深度分析 TCP 连接耗时的秘密](http://www.52im.net/thread-3265-1-1.html)》  
    

**如果您觉得本系列文章过于专业，您可先阅读《网络编程懒人入门》系列文章，该系列目录如下：**

*   《[网络编程懒人入门 (一)：快速理解网络通信协议（上篇）](http://www.52im.net/thread-1095-1-1.html)》
*   《[网络编程懒人入门 (二)：快速理解网络通信协议（下篇）](http://www.52im.net/thread-1103-1-1.html)》
*   《[网络编程懒人入门 (三)：快速理解 TCP 协议一篇就够](http://www.52im.net/thread-1107-1-1.html)》
*   《[网络编程懒人入门 (四)：快速理解 TCP 和 UDP 的差异](http://www.52im.net/thread-1160-1-1.html)》
*   《[网络编程懒人入门 (五)：快速理解为什么说 UDP 有时比 TCP 更有优势](http://www.52im.net/thread-1277-1-1.html)》  
    

**本站的《脑残式网络编程入门》也适合入门学习，本系列大纲如下：**

*   《[脑残式网络编程入门 (一)：跟着动画来学 TCP 三次握手和四次挥手](http://www.52im.net/thread-1729-1-1.html)》
*   《[脑残式网络编程入门 (二)：我们在读写 Socket 时，究竟在读写什么？](http://www.52im.net/thread-1732-1-1.html)》
*   《[脑残式网络编程入门 (三)：HTTP 协议必知必会的一些知识](http://www.52im.net/thread-1751-1-1.html)》
*   《[脑残式网络编程入门 (四)：快速理解 HTTP/2 的服务器推送 (Server Push)](http://www.52im.net/thread-1795-1-1.html)》  
    

**关于移动端网络特性及优化手段的总结性文章请见：**

*   《[现代移动端网络短连接的优化手段总结：请求速度、弱网适应、安全保障](http://www.52im.net/thread-1413-1-1.html)》
*   《[移动端 IM 开发者必读 (一)：通俗易懂，理解移动网络的“弱” 和“慢”](http://www.52im.net/thread-1587-1-1.html)》
*   《[移动端 IM 开发者必读 (二)：史上最全移动弱网络优化方法总结](http://www.52im.net/thread-1588-1-1.html)》  
    

3、参考资料
------

《

[TCP/IP 详解](http://www.52im.net/topic-tcpipvol1.html)

-

[第 11 章 ·UDP：用户数据报协议](http://docs.52im.net/extend/docs/book/tcpip/vol1/11/)

》

《

[TCP/IP 详解](http://www.52im.net/topic-tcpipvol1.html)

-

[第 17 章 ·TCP：传输控制协议](http://docs.52im.net/extend/docs/book/tcpip/vol1/17/)

》

《

[TCP/IP 详解](http://www.52im.net/topic-tcpipvol1.html)

-

[第 18 章 ·TCP 连接的建立与终止](http://docs.52im.net/extend/docs/book/tcpip/vol1/18/)

》

《

[TCP/IP 详解](http://www.52im.net/topic-tcpipvol1.html)

-

[第 21 章 ·TCP 的超时与重传](http://docs.52im.net/extend/docs/book/tcpip/vol1/21/)

》

《

[通俗易懂 - 深入理解 TCP 协议（上）：理论基础](http://www.52im.net/thread-513-1-1.html)

》

《

[通俗易懂 - 深入理解 TCP 协议（下）：RTT、滑动窗口、拥塞处理](http://www.52im.net/thread-515-1-1.html)

》

《

[理论经典：TCP 协议的 3 次握手与 4 次挥手过程详解](http://www.52im.net/thread-258-1-1.html)

》

《

[理论联系实际：Wireshark 抓包分析 TCP 3 次握手、4 次挥手过程](http://www.52im.net/thread-275-1-1.html)

》

4、TCP 异常关闭的研究测试
---------------

### 1 服务器端只 Recv 消息而不 Send 消息

**1.1 测试方法：**

服务器程序在接受客户端的 TCP 连接后 Sleep 几秒钟，客户端程序在 TCP 连接后立即发送很多消息给对端后做相应动作（退出或等待），服务器程序 Sleep 完后开始 Recv 消息。

**注意：**

服务器程序测试了 Linux 和 Windows 版本，但客户端只测试了 Windows 版本，如果是 Linux 客户端则有些 Case 的结果会不一样。

**1.2 测试 Case：**

*   **1）客户端程序正常运行的情况下，拔掉网线，杀掉客户端程序：**  
      目的：模拟客户端死机、系统突然重启、网线松动或网络不通等情况。  
      结论：这种情况下服务器程序没有检测到任何异常，并最后等待 “超时” 才断开 TCP 连接。
*   **2）客户端程序发送很多数据包后正常关闭 Socket 并 exit 进程 (或不退出进程)：**  
      目的：模拟客户端发送完消息后正常退出的情况。  
      结论：这种情况下服务器程序能够成功接收完所有消息，并最后收到 “对端关闭”（Recv 返回零）消息。
*   **3）客户端程序发送很多数据包后不关闭 Socket 直接 exit 进程：**  
      目的：模拟客户端程序退出而忘记关闭 Socket 的情况（比如通过 Windows 窗口的关闭图标退出进程，而没有捕获相应关闭事件做正常退出处理等）。  
      结论：这种情况下服务器程序能够收到部分 TCP 消息，然后收到 “104: Connection reset by peer”（Linux 下）或 “10054: An existing connection was forcibly closed by the remote host”（Windows 下）错误。
*   **4）客户端程序发送很多数据包的过程中直接 Kill 进程：**  
      目的：模拟客户端程序崩溃或非正常方式结束进程（比如 Linux 下 "kill -9" 或 Windows 的任务管理器杀死进程）的情况。  
      结论：这种情况下服务器程序很快收到 “104: Connection reset by peer”（Linux 下）或 “10054: An existing connection was forcibly closed by the remote host”（Windows 下）错误。  
    

### 2 服务器端 Recv 消息并 Send 应答消息

**2.1 测试方法：**

服务器程序在接受客户端的 TCP 连接后 Sleep 几秒钟，客户端程序在 TCP 连接后立即发送很多消息给对端后做相应动作（退出或等待），服务器程序 Sleep 完后开始 Recv 和 Send 消息。

**注意：**

服务器程序测试了 Linux 和 Windows 版本，但客户端只测试了 Windows 版本，如果是 Linux 客户端则有些 Case 的结果可能会不一样。

**2.2 测试结果：**

*   **1）客户端程序发送很多数据包后正常关闭 Socket 并 exit 进程（或不退出进程）：**  
      目的：模拟客户端正常关闭 Socket 后，服务器端在检查到 TCP 对端关闭前向客户端发送消息的情况。  
      结论：这种情况下服务器程序接收和发送部分 TCP 消息后，在 Send 消息时产生 “32: Broken pipe”（Linux 下）或 “10053: An established connection was aborted by the software in your host machine”（Windows 下）错误。
*   **2）客户端程序发送很多数据包后不关闭 Socket 直接 exit 或 Kill 进程：**  
      目的：模拟客户端程序退出而忘记关闭 Socket、或客户端程序崩溃或非正常方式结束进程的情况。  
      结论：这种情况下服务器程序在 Recv 或 Send 消息时产生 “104: Connection reset by peer”（Linux 下）或 “10054: An existing connection was forcibly closed by the remote host”（Windows 下）错误。  
    

### 3 效果和总结

**3.1 总结：**

TCP 发现网络异常（特别是 Linux 下的 104 错误或 Windows 下 10054 错误）的情况很多，比如网络本身的问题、中间路由器问题、网卡驱动器问题等不可抗拒因素，但下面是应用程序本身可能会导致的问题，也是我们需要进一步研究和解决的情况，特别是程序崩溃导致问题：

*   **1）当 TCP 连接的进程在忘记关闭 Socket 而退出、程序崩溃、或非正常方式结束进程的情况下：**  
    （Windows 客户端），会导致 TCP 连接的对端进程产生 “104: Connection reset by peer”（Linux 下）或 “10054: An existing connection was forcibly closed by the remote host”（Windows 下）错误。
*   **2）当 TCP 连接的进程机器发生死机、系统突然重启、网线松动或网络不通等情况下：**  
    （Windows 客户端），连接的对端进程可能检测不到任何异常，并最后等待 “超时” 才断开 TCP 连接。
*   **3）当 TCP 连接的进程正常关闭 Socket 时，对端进程在检查到 TCP 关闭事件之前仍然向 TCP 发送消息：**  
    （Windows 客户端），则在 Send 消息时会产生 “32: Broken pipe”（Linux 下）或 “10053: An established connection was aborted by the software in your host machine”（Windows 下）错误。  
    

**3.2 效果：**

针对 A 项目的掉线问题，通过问卷调查和联系个别玩家等方法，发现掉线的情况很大部分是客户端程序直接退出了，因此推动项目组实现了客户端的 Qos 上报功能，最后通过客户端的 Qos 上报的统计数据得出客户端程序的崩溃比例比较高，占了总掉线的很大比率，当然其它情况也存在，但比例相对比较小。

因此，A 项目首先应该解决客户端程序的崩溃问题，如果该问题解决了，也就解决大部分掉线问题。

5、TCP 异常关闭的进一步研究测试
------------------

### 1 问题背景

B 项目游戏在跨服跳转时的掉线比例比较高，经过分析 ProtocalHandler 和 tconnd 的日志，发现掉线出现的情况是：tconnd 发送了跨服跳转消息后立即关闭了 Socket，客户端进程在接收到跨服跳转消息之前发送消息后收到 Windows 10054 错误，然后做断线重连失败。

B 项目实现跨服跳转的流程是 GameSvr 给客户端程序下发的跨服跳转命令的同时携带了 Stop 请求，也就是说 tconnd 在向客户端转发跨服跳转消息后立即就会关闭当前的 Socket 连接，而且 B 项目的客户端程序会定期不断地向服务器上报消息。这又怎么会导致客户端程序收到 10054 错误而呢？鉴于此，对 TCP 的连接做进一步的场景测试分析。

### 2TCP 异常进一步测试研究

**2.1 测试方法：**

客户端和服务器端程序建立 TCP 连接，服务器程序在 TCP 缓冲区中有消息或没有消息的情况下关闭 Socket，客户端在对端 Socket 已经关闭的情况下继续 Send 和 Recv 消息。

**注意：**

服务器端只测试了 Linux 版本，但客户端测试了 Windows 和 Linux 两个版本。

**2.2 测试结果：**

*   **1）服务器端已经 close 了 Socket，客户端再发送数据：**  
      目的：测试在 TCP 对端进程已经关闭 Socket 时，本端进程还未检测到连接关闭的情况下继续向对端发送消息。  
      结论：第一包可以发送成功，但第二包发送失败，错误码为 “10053: An established connection was aborted by the software in your host machine”（Windows 下）或 “32: Broken pipe，同时收到 SIGPIPE 信号”（Linux 下）错误。
*   **2）服务器端发送数据到 TCP 后 close 了 Socket，客户端再发送一包数据，然后接收消息：**  
      目的：测试在 TCP 对端进程发送数据后关闭 Socket，本端进程还未检测到连接关闭的情况下发送一包消息，接着接收消息。  
      结论：客户端能够成功发送第一包数据（这会导致服务器端发送一个 RST 包 <已抓包验证>），客户端再去 Recv 时，对于 Windows 和 Linux 程序有如下不同的表现：  
            - 2.1）Windows 客户端程序：Recv 失败，错误码为 “10053: An established connection was aborted by the software in your host machine”；  
            - 2.2）Linux 客户端程序：能正常接收完所有消息包，最后收到正常的对端关闭消息（这一点与 Window 下不一样，RST 包没有被提前接收到）。
*   **3）服务器端在 TCP 的接收缓冲区中还有未接收数据的情况下 close 了 Socket，客户端再收包：**  
      目的：测试在 TCP 的接收缓冲区中还有未接收数据的情况下关闭 Socket 时，对端进程是否正常。  
      结论：这种情况服务器端就会向对端发送 RST 包，而不是正常的 FIN 包（已经抓包证明），这就会导致客户端提前（RST 包比正常数据包先被收到）收到 “10054: An existing connection was forcibly closed by the remote host”（Windows 下）或 “104: Connection reset by peer”（Linux 下）错误。  
    

### 3 效果和总结

**3.1 总结：**

TCP 应用程序某些看是正常的行为下也可能会导致对端接收到异常，比如当 TCP 接收缓冲区中还有未收数据的情况下关闭 Socket，则会导致对端接收到异常关闭而不是正常关闭；反过来说，当 TCP 检测到异常关闭时并不一定表示业务上出问题了，因为很可能就是业务正常结束了。

下面是本次测试的主要结论：

*   **1）**当 TCP 连接的对端进程已经关闭了 Socket 的情况下，本端进程再发送数据时，第一包可以发送成功（但会导致对端发送一个 RST 包过来）：之后如果再继续发送数据会失败，错误码为 “10053: An established connection was aborted by the software in your host machine”（Windows 下）或 “32: Broken pipe，同时收到 SIGPIPE 信号”（Linux 下）错误；之后如果接收数据，则 Windows 下会报 10053 的错误，而 Linux 下则收到正常关闭消息；
*   **2）**TCP 连接的本端接收缓冲区中还有未接收数据的情况下 close 了 Socket，则本端 TCP 会向对端发送 RST 包，而不是正常的 FIN 包，这就会导致对端进程提前（RST 包比正常数据包先被收到）收到 “10054: An existing connection was forcibly closed by the remote host”（Windows 下）或 “104: Connection reset by peer”（Linux 下）错误。  
    

**3.2 效果：**

B 项目跨服跳转的掉线问题有相当一部分的种情况是 tconnd 向客户端转发跨服跳转消息后立即关闭 Socket 连接，而此时刚好客户端向 tconnd 发送了数据包：

*   **第一种情况：**tconnd 在关闭 Socket 的时刻其 TCP 的接收缓冲区中有未收的消息，这就使得 tconnd 进程的 TCP 向客户端发送的是 RST 包而不是正常结束的 FIN 包，所以客户端程序就会提前收到 RST 包（RST 包会比正常数据提前收到），而不会先收完跨服跳转消息后再接收到正常结束消息，这就导致客户端收到网络异常断线而做重连，但之前的连接是 tconnd 主动关闭的，所以不可能重连成功，从而导致掉线；
*   **第二种情况：**tconnd 已经关闭了 Socket 后，客户端在接收到跳转消息和检测到 TCP 关闭之前向 tconnd 发送了消息，这就会导致客户端程序收到异常断线而做重连并失败。  
    

最后，与 B 项目项目组一起讨论，改进了大部分跨服跳转的业务流程后，掉线比例 j 减少了很多，当然还是存在一定比例的掉线，但这应该就是其它一些原因了（网络异常问题原因很多，国内当前的网络环境下，掉线问题是不可能完全避免的）。

6、结束语
-----

通常情况下，向 TCP 的 Socket 发送完数据后关闭 Socket，大家认为这样很正常的方式肯定没有问题，对端应该正确收完数据后收到 TCP 的关闭消息，但实际上在某些情况下并非如此：当 TCP 本端的接收缓冲区中有未收的数据时关闭 Socket，这会导致对端收到 RST 的异常关闭消息；当对端在本端已经关闭 Socket 的情况下再次发送消息时，也会导致对端收到异常关闭消息；还有为了避免 TIME_WAIT 而设置了 SO_LINGER 选项的话，也会导致连接提前夭折使对端收到 RST 异常关闭消息。

有些时候业务流程对是否引起掉线也很重要（特别是连接关闭流程），比如前面的 B 项目的跨服跳转掉线问题很大部分就是因为 GameSvr 请求关闭连接导致的。建议各个游戏项目的关闭流程（包括跨服跳转的原连接的关闭）最好都由客户端发起关闭，这样就一定程度上避免上述问题的发生（因为客服端发起关闭的时候，一般业务流程都走完了，服务器端也不会再向客户端发送消息了）。

程序收到网络异常的情况很多（最多的就是 Linux 下的 104 错误和 Windos 下的 10054/10053 错误）：有网络本身的问题、也有应用使用不当的问题；有运营商之间的跨网络问题、网络中间路由器问题、玩家机器硬件（比如网卡及其驱动）问题和操作系统、杀毒软件、防火墙等软件问题，还有玩家的上网设备和路由器等中间设备问题等，但客户端程序崩溃问题有可能会占掉线的很高比例，这也是值得我们注意和改进的地方。还有种情况值得我们注意，有些 TP-LINK 的路由器，当 UDP 包大小超过其 MTU 值时会导致用户机器的网络断开，从而引起掉线（这个问题在某些项目的个别玩家中已经出现过）。

网络异常关闭引起掉线是当前游戏中普遍存在的问题，区别只在于掉线的比例多少，特别是国内各运营商之间跨网络访问更是不太顺畅，要将其完全消除是不可能的，但我们的目标是将其控制在较小的可接受范围内。

（原文链接：[点此进入](https://www.qcloud.com/community/article/164816001481011820)）

7、更多资料
------

《

[TCP/IP 详解](http://www.52im.net/topic-tcpipvol1.html)

-

[第 11 章 ·UDP：用户数据报协议](http://docs.52im.net/extend/docs/book/tcpip/vol1/11/)

》

《

[TCP/IP 详解](http://www.52im.net/topic-tcpipvol1.html)

-

[第 17 章 ·TCP：传输控制协议](http://docs.52im.net/extend/docs/book/tcpip/vol1/17/)

》

《

[TCP/IP 详解](http://www.52im.net/topic-tcpipvol1.html)

-

[第 18 章 ·TCP 连接的建立与终止](http://docs.52im.net/extend/docs/book/tcpip/vol1/18/)

》

《

[TCP/IP 详解](http://www.52im.net/topic-tcpipvol1.html)

-

[第 21 章 ·TCP 的超时与重传](http://docs.52im.net/extend/docs/book/tcpip/vol1/21/)

》

《

[技术往事：改变世界的 TCP/IP 协议（珍贵多图、手机慎点）](http://www.52im.net/thread-520-1-1.html)

》

《

[通俗易懂 - 深入理解 TCP 协议（上）：理论基础](http://www.52im.net/thread-513-1-1.html)

》

《

[通俗易懂 - 深入理解 TCP 协议（下）：RTT、滑动窗口、拥塞处理](http://www.52im.net/thread-515-1-1.html)

》

《

[理论经典：TCP 协议的 3 次握手与 4 次挥手过程详解](http://www.52im.net/thread-258-1-1.html)

》

《

[理论联系实际：Wireshark 抓包分析 TCP 3 次握手、4 次挥手过程](http://www.52im.net/thread-275-1-1.html)

》

《

[计算机网络通讯协议关系图（中文珍藏版）](http://www.52im.net/thread-180-1-1.html)

》

《

[UDP 中一个包的大小最大能多大？](http://www.52im.net/thread-29-1-1.html)

》

《

[Java 新一代网络编程模型 AIO 原理及 Linux 系统 AIO 介绍](http://www.52im.net/thread-306-1-1.html)

》

《

[NIO 框架入门 (一)：服务端基于 Netty4 的 UDP 双向通信 Demo 演示](http://www.52im.net/thread-367-1-1.html)

》

《

[NIO 框架入门 (二)：服务端基于 MINA2 的 UDP 双向通信 Demo 演示](http://www.52im.net/thread-373-1-1.html)

》

《

[NIO 框架入门 (三)：iOS 与 MINA2、Netty4 的跨平台 UDP 双向通信实战](http://www.52im.net/thread-378-1-1.html)

》

《

[NIO 框架入门 (四)：Android 与 MINA2、Netty4 的跨平台 UDP 双向通信实战](http://www.52im.net/thread-388-1-1.html)

》

《

[P2P 技术详解 (一)：NAT 详解——详细原理、P2P 简介](http://www.52im.net/thread-50-1-1.html)

》

《

[P2P 技术详解 (二)：P2P 中的 NAT 穿越(打洞) 方案详解](http://www.52im.net/thread-542-1-1.html)

》

《

[P2P 技术详解 (三)：P2P 技术之 STUN、TURN、ICE 详解](http://www.52im.net/thread-557-1-1.html)

》

《

[高性能网络编程 (一)：单台服务器并发 TCP 连接数到底可以有多少](http://www.52im.net/thread-561-1-1.html)

》

《

[高性能网络编程 (二)：上一个 10 年，著名的 C10K 并发连接问题](http://www.52im.net/thread-566-1-1.html)

》

《

[高性能网络编程 (三)：下一个 10 年，是时候考虑 C10M 并发问题了](http://www.52im.net/thread-568-1-1.html)

》

《

[高性能网络编程 (四)：从 C10K 到 C10M 高性能网络应用的理论探索](http://www.52im.net/thread-578-1-1.html)

》

《

[不为人知的网络编程 (一)：浅析 TCP 协议中的疑难杂症 (上篇)](http://www.52im.net/thread-1003-1-1.html)

》

《

[不为人知的网络编程 (二)：浅析 TCP 协议中的疑难杂症 (下篇)](http://www.52im.net/thread-1004-1-1.html)

》

《

[不为人知的网络编程 (三)：关闭 TCP 连接时为什么会 TIME_WAIT、CLOSE_WAIT](http://www.52im.net/thread-1007-1-1.html)

》

>>

[更多同类文章 ……](http://www.52im.net/forum.php?mod=collection&action=view&ctid=9)

[img-0]:data:text/html;base64,DQo8IURPQ1RZUEUgaHRtbCBQVUJMSUMgIi0vL1czQy8vRFREIFhIVE1MIDEuMCBUcmFuc2l0aW9uYWwvL0VOIiAiaHR0cDovL3d3dy53My5vcmcvVFIveGh0bWwxL0RURC94aHRtbDEtdHJhbnNpdGlvbmFsLmR0ZCI+DQo8aHRtbCB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMTk5OS94aHRtbCI+DQo8aGVhZD4NCjxtZXRhIGh0dHAtZXF1aXY9IkNvbnRlbnQtVHlwZSIgY29udGVudD0idGV4dC9odG1sOyBjaGFyc2V0PWdiayIgLz4NCjxtZXRhIGh0dHAtZXF1aXY9IlgtVUEtQ29tcGF0aWJsZSIgY29udGVudD0iSUU9RW11bGF0ZUlFNyIgLz4gDQo8dGl0bGU+sKXRvaGtxPq3w87KtcTSs8Pmsru05tTaIC0gvLTKsc2o0bbN+Cg1MmltLm5ldCkgLSC8tMqxzajRtry8yvXJ58f4ITwvdGl0bGU+DQo8bWV0YSBuYW1lPSJrZXl3b3JkcyIgY29udGVudD0iNTJpbS5uZXQgLSC8tMqxzajRtry8yvXJ58f4ISIgLz4NCjxtZXRhIG5hbWU9ImRlc2NyaXB0aW9uIiBjb250ZW50PSI1MmltLm5ldCAtILy0yrHNqNG2vLzK9cnnx/ghICIgLz4NCjxtZXRhIG5hbWU9ImdlbmVyYXRvciIgY29udGVudD0iNTJpbS5uZXQgWDMuMiIgLz4NCjxtZXRhIG5hbWU9ImF1dGhvciIgY29udGVudD0izfi8ysqxtPogVGVhbSIgLz4NCjxtZXRhIG5hbWU9ImNvcHlyaWdodCIgY29udGVudD0iMjAxNC0yMDE2IDUySU0uTkVUIFRlYW0iIC8+DQo8bWV0YSBuYW1lPSJNU1NtYXJ0VGFnc1ByZXZlbnRQYXJzaW5nIiBjb250ZW50PSJUcnVlIiAvPg0KPG1ldGEgaHR0cC1lcXVpdj0iTVNUaGVtZUNvbXBhdGlibGUiIGNvbnRlbnQ9IlllcyIgLz4NCg0KPHN0eWxlPg0KKnttYXJnaW46MDtwYWRkaW5nOjB9DQpib2R5e2ZvbnQtZmFtaWx5OiLOosjt0cW62iI7YmFja2dyb3VuZDojREFEOUQ3fQ0KaW1ne2JvcmRlcjpub25lfQ0KYSAqe2N1cnNvcjpwb2ludGVyfQ0KdWwsbGl7bGlzdC1zdHlsZTpub25lfQ0KdGFibGV7dGFibGUtbGF5b3V0OmZpeGVkO30NCnRhYmxlIHRyIHRke3dvcmQtYnJlYWs6YnJlYWstYWxsOyB3b3JkLXdyYXA6YnJlYWstd29yZDt9DQoNCmF7dGV4dC1kZWNvcmF0aW9uOm5vbmU7b3V0bGluZTpub25lfQ0KYTpob3Zlcnt0ZXh0LWRlY29yYXRpb246dW5kZXJsaW5lfQ0KLmNmOmFmdGVye2NvbnRlbnQ6ICIuIjtkaXNwbGF5OiBibG9jaztoZWlnaHQ6IDA7Zm9udC1zaXplOiAwO2NsZWFyOmJvdGg7dmlzaWJpbGl0eTogaGlkZGVuO30NCi5jZnt6b29tOiAxO2NsZWFyOmJvdGh9DQoNCi5iZ3t3aWR0aDoxMDAlO2JhY2tncm91bmQ6dXJsKCJodHRwOi8vc3RhdGljLjUyaW0ubmV0L3N0YXRpYy9lcnJvcnBhZ2UvNDA0LzAxLmpwZyIpIG5vLXJlcGVhdCBjZW50ZXIgdG9wICNEQUQ5RDc7cG9zaXRpb246YWJzb2x1dGU7dG9wOjA7bGVmdDowO2hlaWdodDo2MDBweDtvdmVyZmxvdzpoaWRkZW59DQouY29udHttYXJnaW46MCBhdXRvO3dpZHRoOjUwMHB4O2xpbmUtaGVpZ2h0OjIwcHg7fQ0KLmMxe2hlaWdodDozNjBweDt0ZXh0LWFsaWduOmNlbnRlcn0NCi5jMSAuaW1nMXttYXJnaW4tdG9wOjE4MHB4fQ0KLmMxIC5pbWcye21hcmdpbi10b3A6MTY1cHh9DQouY29udCBoMnt0ZXh0LWFsaWduOmNlbnRlcjtjb2xvcjojNTU1O2ZvbnQtc2l6ZToxOHB4O2ZvbnQtd2VpZ2h0Om5vcm1hbDtoZWlnaHQ6MzVweH0NCi5jMntoZWlnaHQ6MzVweDt0ZXh0LWFsaWduOmNlbnRlcn0NCi5jMiBhe2Rpc3BsYXk6aW5saW5lLWJsb2NrO21hcmdpbjowIDRweDtmb250LXNpemU6MTRweDtoZWlnaHQ6MjNweDtjb2xvcjpyZ2IoMTM3LDE3Miw3OCk7cGFkZGluZy10b3A6MXB4O3RleHQtZGVjb3JhdGlvbjpub25lO3RleHQtYWxpZ246bGVmdH0NCi5jMiBhOmhvdmVye2NvbG9yOiM2MjYyNjI7dGV4dC1kZWNvcmF0aW9uOm5vbmU7fQ0KLmMyIGEuaG9tZXt3aWR0aDo2NnB4O2JhY2tncm91bmQ6dXJsKCJodHRwOi8vc3RhdGljLjUyaW0ubmV0L3N0YXRpYy9lcnJvcnBhZ2UvNDA0LzAyLnBuZyIpO3BhZGRpbmctbGVmdDozMHB4fQ0KLmMyIGEuaG9tZTpob3ZlcntiYWNrZ3JvdW5kOnVybCgiaHR0cDovL3N0YXRpYy41MmltLm5ldC9zdGF0aWMvZXJyb3JwYWdlLzQwNC8wMi5wbmciKSAwIC0yNHB4fQ0KLmMyIGEuaG9tZTphY3RpdmV7YmFja2dyb3VuZDp1cmwoImh0dHA6Ly9zdGF0aWMuNTJpbS5uZXQvc3RhdGljL2Vycm9ycGFnZS80MDQvMDIucG5nIikgMCAtNDhweH0NCi5jMiBhLnJle3dpZHRoOjY2cHg7YmFja2dyb3VuZDp1cmwoImh0dHA6Ly9zdGF0aWMuNTJpbS5uZXQvc3RhdGljL2Vycm9ycGFnZS80MDQvMDMucG5nIik7cGFkZGluZy1sZWZ0OjMwcHh9DQouYzIgYS5yZTpob3ZlcntiYWNrZ3JvdW5kOnVybCgiaHR0cDovL3N0YXRpYy41MmltLm5ldC9zdGF0aWMvZXJyb3JwYWdlLzQwNC8wMy5wbmciKSAwIC0yNHB4fQ0KLmMyIGEucmU6YWN0aXZle2JhY2tncm91bmQ6dXJsKCJodHRwOi8vc3RhdGljLjUyaW0ubmV0L3N0YXRpYy9lcnJvcnBhZ2UvNDA0LzAzLnBuZyIpIDAgLTQ4cHh9DQouYzIgYS5zcnt3aWR0aDoxNTNweDtiYWNrZ3JvdW5kOnVybCgiaHR0cDovL3N0YXRpYy41MmltLm5ldC9zdGF0aWMvZXJyb3JwYWdlLzQwNC8wNC5wbmciKTtwYWRkaW5nLWxlZnQ6MjhweH0NCi5jMiBhLnNyOmhvdmVye2JhY2tncm91bmQ6dXJsKCJodHRwOi8vc3RhdGljLjUyaW0ubmV0L3N0YXRpYy9lcnJvcnBhZ2UvNDA0LzA0LnBuZyIpIDAgLTI0cHh9DQouYzIgYS5zcjphY3RpdmV7YmFja2dyb3VuZDp1cmwoImh0dHA6Ly9zdGF0aWMuNTJpbS5uZXQvc3RhdGljL2Vycm9ycGFnZS80MDQvMDQucG5nIikgMCAtNDhweH0NCi5jM3toZWlnaHQ6MTgwcHg7dGV4dC1hbGlnbjpjZW50ZXI7Y29sb3I6Izk5OTtmb250LXNpemU6MTJweH0NCi5jMyBhIHtjb2xvcjpyZ2IoMTM3LDE3Miw3OCk7fQ0KI2Jme3Bvc2l0aW9uOmFic29sdXRlO3RvcDoyNjlweDtsZWZ0OjA7d2lkdGg6MTAwJX0NCi5iZjF7bWFyZ2luOjAgYXV0bzt3aWR0aDo5OXB4O3BhZGRpbmctbGVmdDozMnB4fQ0KLmJke2hlaWdodDo2MDBweDtvdmVyZmxvdzpoaWRkZW59DQojYm94e3Bvc2l0aW9uOmFic29sdXRlO3RvcDoxNjVweDtsZWZ0OjA7d2lkdGg6MTAwJTt0ZXh0LWFsaWduOmNlbnRlcn0NCi5iZjF7bWFyZ2luOjAgYXV0bzt3aWR0aDo5OXB4O3BhZGRpbmctbGVmdDozMnB4fQ0KDQpoMi5lcnJvcl9jb250ZW50IHtjb2xvcjogcmdiKDIzMSwwLDApO2ZvbnQtc2l6ZTogMjVweDt9DQo8L3N0eWxlPg0KDQo8c2NyaXB0Pg0KdmFyIF9obXQgPSBfaG10IHx8IFtdOw0KKGZ1bmN0aW9uKCkgew0KICB2YXIgaG0gPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJzY3JpcHQiKTsNCiAgaG0uc3JjID0gIi8vaG0uYmFpZHUuY29tL2htLmpzP2JkYTUwYjRkMDE3NDlhYmM0ZjJlMWEwMDI1MjRlY2QxIjsNCiAgdmFyIHMgPSBkb2N1bWVudC5nZXRFbGVtZW50c0J5VGFnTmFtZSgic2NyaXB0IilbMF07IA0KICBzLnBhcmVudE5vZGUuaW5zZXJ0QmVmb3JlKGhtLCBzKTsNCn0pKCk7DQo8L3NjcmlwdD4NCg0KPC9oZWFkPg0KPGJvZHk+DQo8ZGl2IGNsYXNzPSJiZyI+DQoJPGRpdiBjbGFzcz0iY29udCI+DQoJCTxkaXYgY2xhc3M9ImMxIj48aW1nIHNyYz0iaHR0cDovL3N0YXRpYy41MmltLm5ldC9zdGF0aWMvZXJyb3JwYWdlLzQwNC8wMS5wbmciIGNsYXNzPSJpbWcxIiAvPjwvZGl2Pg0KCQk8aDIgY2xhc3M9ImVycm9yX2NvbnRlbnQiPrCl0b2hrSDE+rfDzsq1xNKzw+ayu7Tm1NohPC9oMj4NCgkJPGRpdiBjbGFzcz0iYzIiPjxhIGhyZWY9Imh0dHA6Ly93d3cuNTJpbS5uZXQvZm9ydW0ucGhwIiBjbGFzcz0icmUiPre1u9jJ58f4PC9hPjxhIGhyZWY9Imh0dHA6Ly93d3cuNTJpbS5uZXQiIGNsYXNzPSJob21lIj7N+NW+ytfSszwvYT48YSBocmVmPSJodHRwOi8vd3d3LjUyaW0ubmV0L3NlYXJjaC5waHA/bW9kPWZvcnVtIiBjbGFzcz0ic3IiPsvRy/fSu8/C0rPD5s/gudjQxc+iPC9hPjwvZGl2Pg0KCQk8ZGl2IGNsYXNzPSJjMyI+PGEgaHJlZj0iaHR0cDovL3d3dy41MmltLm5ldCIgY2xhc3M9ImMzIj68tMqxzajRts34KDUyaW0ubmV0KTwvYT4mbmJzcDvM4dDRxPogLSDE+r/JxNzK5Mjrwcu07c7ztcTN+Na3o6y78tXfuMPN+NKz0tHJvrP9u/LSxravPC9kaXY+DQoJPC9kaXY+DQo8L2Rpdj4NCjwvYm9keT4NCjwvaHRtbD4=