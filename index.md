# 📚 Nodebook 文件浏览器

欢迎浏览 [joehe-doc/nodebook](https://github.com/joehe-doc/nodebook) 仓库的内容。点击目录或文件名进行浏览。

<div id="browser">📂 正在加载目录...</div>

<!-- 引入 marked.js 用于渲染 Markdown -->
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>

<script>
  const owner = "joehe-doc";
  const repo = "nodebook";
  const apiBase = `https://api.github.com/repos/${owner}/${repo}/contents`;

  async function loadDirectory(path = "") {
    const res = await fetch(`${apiBase}/${path}`);
    const data = await res.json();

    const browser = document.getElementById("browser");
    browser.innerHTML = "";

    // 添加返回按钮
    if (path) {
      const back = document.createElement("a");
      back.href = "#";
      back.innerText = "⬅️ 返回上级目录";
      back.style.display = "block";
      back.style.marginBottom = "1em";
      back.onclick = () => {
        const parent = path.split("/").slice(0, -1).join("/");
        loadDirectory(parent);
        return false;
      };
      browser.appendChild(back);
    }

    // 排序：目录在前，文件在后，名称升序
    data.sort((a, b) => {
      if (a.type !== b.type) return a.type === "dir" ? -1 : 1;
      return a.name.localeCompare(b.name);
    });

    // 创建列表项
    data.forEach(item => {
      const link = document.createElement("a");
      const isDir = item.type === "dir";
      const isMarkdown = item.name.endsWith(".md");
      const isHtml = item.name.endsWith(".html");

      // 设置显示文本和样式
      link.href = "#";
      link.innerText = (isDir ? "📁 " : isMarkdown ? "📝 " : "📄 ") + item.name;
      link.style.display = "block";
      link.style.margin = "4px 0";
      link.style.fontWeight = isDir ? "bold" : "normal";
      link.style.color = isDir ? "#0366d6" : "#333";

      if (isDir) {
        link.onclick = () => {
          loadDirectory(path ? `${path}/${item.name}` : item.name);
          return false;
        };
      } else if (isMarkdown) {
        // 直接渲染 Markdown
        link.onclick = async () => {
          const res = await fetch(item.download_url);
          if (!res.ok) {
            alert("无法加载 Markdown 文件内容");
            return;
          }
          const md = await res.text();
          const html = marked.parse(md);

          browser.innerHTML = `<a href="#" onclick="loadDirectory('${path}'); return false;">⬅️ 返回列表</a><hr>`;
          const mdContainer = document.createElement("div");
          mdContainer.innerHTML = html;
          browser.appendChild(mdContainer);
        };
      } else {
        // 其他文件：跳转到 GitHub Pages 渲染路径
        const fileUrl = `https://${owner}.github.io/${repo}/${path ? path + '/' : ''}${item.name}`;
        link.href = fileUrl;
        link.target = "_blank";
      }

      browser.appendChild(link);
    });
  }

  loadDirectory();
</script>
