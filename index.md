# Nodebook 浏览器

> 点击文件名即可浏览 Markdown、HTML 或其他文件内容。

<div id="browser">正在加载...</div>


<!-- markdown 渲染库 -->
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

    // 返回上级目录
    if (path) {
      const back = document.createElement("a");
      back.href = "#";
      back.innerText = "⬅️ 返回上级目录";
      back.onclick = () => {
        const parent = path.split("/").slice(0, -1).join("/");
        loadDirectory(parent);
        return false;
      };
      browser.appendChild(back);
    }

    // 排序：目录在前，文件在后
    data.sort((a, b) => {
      if (a.type !== b.type) return a.type === "dir" ? -1 : 1;
      return a.name.localeCompare(b.name);
    });

    // 显示内容
    data.forEach(item => {
      const link = document.createElement("a");
      const isDir = item.type === "dir";
      const isMarkdown = item.name.endsWith(".md");

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
          const filePath = path ? `${path}/${item.name}` : item.name;
          const rawUrl = `https://raw.githubusercontent.com/${owner}/${repo}/main/${filePath}`;
          const res = await fetch(rawUrl);
          const md = await res.text();

          const mdContainer = document.createElement("div");
          mdContainer.innerHTML = marked.parse(md);
          browser.innerHTML = `<a href="#" onclick="loadDirectory('${path}'); return false;">⬅️ 返回列表</a><hr>`;
          browser.appendChild(mdContainer);
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


