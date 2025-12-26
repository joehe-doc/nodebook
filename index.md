# 📚 Nodebook 文件浏览器

欢迎浏览 [joehe-doc/nodebook](https://github.com/joehe-doc/nodebook) 仓库的内容。点击目录或文件名进行浏览。

<style>
  #container {
    display: flex;
    gap: 2rem;
  }
  #toc {
    width: 200px;
    font-size: 0.9em;
    line-height: 1.4;
    border-right: 1px solid #ddd;
    padding-right: 1rem;
    position: sticky;
    top: 0;
    max-height: 90vh;
    overflow-y: auto;
  }
  #toc h3 {
    margin: 0.5em 0;
    font-size: 1em;
  }
  #toc a {
    display: block;
    color: #555;
    text-decoration: none;
    padding-left: 0.5em;
  }
  #toc a:hover {
    color: #0366d6;
  }
  #browser {
    flex: 1;
  }
  /* 定义大数字列表 */
  .custom-list {
    list-style: none;
    counter-reset: my-counter;
    padding-left: 0;
  }
  .custom-list li {
    counter-increment: my-counter;
    display: flex;
    align-items: center;
    padding: 15px;
    border-bottom: 1px solid #eee;
    transition: background 0.3s;
  }
  .custom-list li:hover {
    background: #f9f9f9;
  }
  /* 生成醒目数字 */
  .custom-list li::before {
    content: counter(my-counter, decimal-leading-zero);
    font-size: 24px;
    font-weight: bold;
    color: #159957; /* Cayman 主题的经典绿色 */
    margin-right: 20px;
    font-family: monospace;
  }
</style>

<div id="container">
  <div id="toc"></div>
  <div id="browser">📂 正在加载目录...</div>
</div>

<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>

<script>
  const owner = "joehe-doc";
  const repo = "nodebook";
  const apiBase = `https://api.github.com/repos/${owner}/${repo}/contents`;

  async function loadDirectory(path = "") {
    const res = await fetch(`${apiBase}/${path}`);
    const data = await res.json();

    const browser = document.getElementById("browser");
    const toc = document.getElementById("toc");
    toc.innerHTML = "";
    browser.innerHTML = "";

    // 返回上级目录
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

    // 排序
    data.sort((a, b) => {
      if (a.type !== b.type) return a.type === "dir" ? -1 : 1;
      return a.name.localeCompare(b.name);
    });

    // 文件项
    data.forEach(item => {
      const link = document.createElement("a");
      const isDir = item.type === "dir";
      const isMarkdown = item.name.endsWith(".md");
      const isHtml = item.name.endsWith(".html");

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
        link.onclick = async () => {
          const res = await fetch(item.download_url);
          if (!res.ok) {
            alert("无法加载 Markdown 文件内容");
            return;
          }
          const md = await res.text();
          const html = marked.parse(md);

          // 插入内容
          browser.innerHTML = `<a href="#" onclick="loadDirectory('${path}'); return false;">⬅️ 返回列表</a><hr>`;
          const mdContainer = document.createElement("div");
          mdContainer.innerHTML = html;
          browser.appendChild(mdContainer);

          // 自动为标题生成锚点
          const headings = mdContainer.querySelectorAll("h1, h2, h3");
          headings.forEach((h, i) => {
            const id = "heading-" + i;
            h.id = id;
          });

          // 构建目录导航
          toc.innerHTML = "<h3>🧭 目录</h3>";
          headings.forEach(h => {
            const link = document.createElement("a");
            link.href = `#${h.id}`;
            link.innerText = "  ".repeat(parseInt(h.tagName[1]) - 1) + h.innerText;
            toc.appendChild(link);
          });
        };
      } else {
        const fileUrl = `https://${owner}.github.io/${repo}/${path ? path + '/' : ''}${item.name}`;
        link.href = fileUrl;
        link.target = "_blank";
      }

      browser.appendChild(link);
    });
  }

  loadDirectory();
</script>
