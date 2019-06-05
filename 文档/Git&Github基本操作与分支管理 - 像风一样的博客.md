Git的原理涉及快照流、链表、指针等，这里不作过多叙述。

## 1.基本操作

### git init

创建一个 Git 仓库

### git clone [url]

拷贝一个 Git 仓库到本地

### git add [file_name]

git add 命令可将该文件添加到缓存

### git commit -m "备注信息"

使用 git add 命令将想要快照的内容写入缓存区， 而执行 git commit 将缓存区内容添加到仓库中。使用 -am 可以跳过 add 命令

### git reset HEAD

git reset HEAD 命令用于取消已缓存的内容

### git status

git status 以查看在你上次提交之后是否有修改

*   -s 参数可以获得简短的结果输出

### git rm

从 Git 中移除某个文件。

*   -f : 强制删除
*   --cached : 从暂存区域移除，但仍然希望保留在当前工作目录中
*   –r * : 递归删除整个目录内的子目录和文件

### git mv

git mv 命令用于移动或重命名一个文件、目录、软连接

## 2.设置签名

签名 = 用户名 \+ 邮箱

### 项目级别/ 仓库级别

**_git config userName demo@163.com_**

保存在 ./.git/config 文件

### 系统用户级别

**_git config --global userName demo@163.com_**\*\*\*

保存在 ~/.gitconfig 文件

项目级别优先于系统用户级别，不能没有签名。

## 3.查看历史记录

**_git log --pretty=oneline_**

**_git log [--oneline]_**

**_git reflog_**

多屏显示控制方式：

空格向下翻页

b 向上翻页

q 退出

## 4.版本回退

### 基于索引值的版本回退

查找历史版本，黄色字体（最左边开头部分）就是索引值。

**_git reflog_**

回退

**_git reset --hard [索引值]_**

### 使用^回退一步

**_git reset --hard HEAD^_**

**_git reset --hard HEAD^^_**

### 使用~回退n步

**_git reset --hard HEAD~n_**

### reset 命令的三个参数对比

--soft 参数

*   仅仅在本地库移动 HEAD 指针

--mixed 参数

*   在本地库移动 HEAD 指针
*   重置暂存区

--hard 参数

*   在本地库移动 HEAD 指针
*   重置暂存区
*   重置工作区

## 5.比较文件差异

**_git diff [文件名]_**

*   将工作区中的文件和暂存区进行比较

**_git diff [本地库中历史版本] [文件名]_**

*   将工作区中的文件和本地库历史记录比较
*   git diff HEAD apple.txt

**不带文件名比较多个文件**

## 6.分支操作

*   创建分支
    
    **_git branch [分支名]_**
    
*   查看分支
    
    **_git branch -v_**
    
*   切换分支
    
    **_git checkout [分支名]_**
    
*   合并分支
    
    将任何分支合并到当前分支
    
    **_git merge [分支名]_**
    
*   合并冲突
```    
    *   合并冲突时，会进入MERGING状态，查看冲突文件。
        
        <<<<<<< HEAD  
        123456  
        =======  
        456789  
        >>>>>>\> master
        
        HEAD：当前分支内容
        
        master：另一分支内容
        
        此时进入手动修改阶段.....
        
    *   冲突的解决
        
        *   编辑文件，删除特殊符号
            
        *   把文件修改到满意的程度，保存退出
            
        *   **_git add \[文件名\]_**
            
        *   **_git commit -m "日志信息"_**
            
            此时commit一定不能带文件名。
            
```

## 本地库关联Github远程库

**_git remote add [shortname][url]_**

**_例：git remote add origin git@github.com:tianqixin/runoob-git-test.git_**

## 推送到远程仓库

**_git push [alias][branch]_**

**_例：git push origin master_**

## 推送冲突

如果在你提交修改时已经有了其它人提交修改，那就会产生冲突。

这时候可以先合并冲突 **_pull_** 拉取到本地，然后按照 **合并冲突** 的解决方法做即可。

## 查看当前的远程库

**_git remote [-v]_**

## 1.从远程仓库下载新分支与数据到本地

**_git fetch [alias][branch]_**

## 2.从远端仓库提取数据并尝试合并到当前分支

**_git merge [alias][branch]_**

## 拉取（pull = fetch+merge）

**_git pull [alias][branch]_**

## 删除远程仓库

删除远程仓库你可以使用命令：

**_git remote rm [alias]_**