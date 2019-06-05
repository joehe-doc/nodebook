Linux开发环境搭建与使用——Linux必备软件之Samba - 秋叶原 && Mike || 麦克

版权声明：本博客文章，大多是本人整理编写，或在网络中收集，转载请注明出处！ https://blog.csdn.net/tennysonsky/article/details/44224671

假如我们是在ubuntu环境上做相应的开发，有的时候，我们需要把我们写的程序共享给别人，或者，自己拷贝出来备份一份。我们习惯用U盘拷贝，如果需要频繁拷贝的话，这样会不太方便。这里给大家介绍一种更好的方法：通过Samba服务器共享。  

Samba是在Linux和UNIX系统上实现SMB协议的一个免费软件，由服务器及客户端程序构成。

Samba服务器在两种不同操作系统间架起了一座桥梁，使Linux系统和Windows系统之间能够通信。通过Linux操作系统下的samba服务，可以实现Windows主机访问Linux下共享文件的功能，为广泛的Linux爱好者提供了极大方便。  

首先，我们需要在ubuntu环境里安装samba。  

安装命令，如下：

**sudo apt-get install samba smbfs smbclient system-config-samba**  

**如果是Ubuntu 14.04 版本，请以此命令安装：sudo apt-get install samba samba-common system-config-samba python-glade2 gksu  **

samba：samba核心组件。  
smbfs：支持SMB/CIFS协议的文件系统。  
smbclient：samba客户端，访问其它机器。  
system-config-samba：图形界面配置工具。  

![](../../_resources/f6f57d6c54a24cca870e6547abb5c904.jpg)  

**通过图形界面对Samba进行相应的配置：**  

1）添加用户

![](../../_resources/5be114fd575a42eeba4f146dc13e16c6.jpg)  

![](../../_resources/dd60611a65d243ca878addc54f2b1312.jpg)  

![](../../_resources/2df36d109c894f87a1669894055bfb44.jpg)  

![](../../_resources/8c7c88a31b524ca39ddffbb70de3f2cd.jpg)  

![](../../_resources/f6ed6cedb2d34b5ebe436f6a5ac25408.jpg)  

2）设置Linux共享目录及其权限  

![](../../_resources/91cfe9f24a504faea48d4ede0b9f11c0.jpg)  

![](../../_resources/265354bc2fcf40c3888a40fd7b7585ff.jpg)  

![](../../_resources/45fd565350844fe6ace66a7c0af6f812.jpg)  

![](../../_resources/ec1b5335e5ed4a199586ae2a32fb4142.jpg)  

![](../../_resources/4c32614122d8455e8a21a7b1a7b83ed9.jpg)  

![](../../_resources/96bd938e412643b1abd069f01d3519e1.jpg)  

![](../../_resources/8ce75e9e7d4c4b7ba188ec9b203a081b.jpg)  

![](../../_resources/4e312595b40945739a8788ccac43ed04.jpg)  

![](../../_resources/c4cf7d26c4084f74aab23f079ef63b88.jpg)  

**3、测试使用**  

1）如果是某个Windows主机要访问ubuntu的共享目录，这两系统的网络必须要能平通，否则，无法访问，下图为ubuntu去平Windows的ip：

![](../../_resources/fa3f269bcb8a45dbb6bdb990cbe2152c.jpg)  

2）获得ubuntu的ip，在终端下敲：ifconfig。  

![](../../_resources/6f0624cba401473d9817d0c5d02e11fb.jpg)  

3）访问samba共享目录，在Windows主机中操作：开始-->运行-->\\\10.220.x.x(ubuntu的ip)\\share(共享名)：  

![](../../_resources/8e380af862b447d68f552d2be09fb341.jpg)  

4）输入用户名、密码：  

![](../../_resources/d27228b94d8a48b3a56702c35cde3728.jpg)  

5）进入共享目录：

![](../../_resources/59a954bb8d2246169050c07830f77e1b.jpg)  

**映射网络驱动器**

以后访问ubuntu这个共享目录，都要在Windows主机中操作：开始-->运行-->\\\10.220.x.x(ubuntu的ip)\\share(共享名)，这个会很麻烦。下面给大家介绍一个好方法：映射网络驱动器。

![](../../_resources/a8299f74ffcc45f39a1d46159bb97bc4.jpg)  

![](../../_resources/dcb4f702c69044b9a4bcebe7b1e5b867.jpg)  

![](../../_resources/1762be9cfb0a4b88a04c37b8188b4f40.jpg)  

![](../../_resources/8f11941710ca4c6d81e81741ed6f9579.jpg)  

以后我们直接打开我的电脑，即可看到这个共享目录，直接打开即可（前提是ubuntu已经开启了）。如果我们不想使用了，也可断开个网络驱动器：

![](../../_resources/9ff448c7170e42929ff105bc4c9988e1.jpg)  

**如果samba服务出现问题，可以重启服务：**  

sudo service smbd restart