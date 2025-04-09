<h2>📁 Nodebook 目录浏览器</h2>
<div id="browser">加载中...</div>

<script>
  const owner = "joehe-doc";
  const repo = "nodebook";
  const apiBase = `https://api.github.com/repos/${owner}/${repo}/contents`;

  async function loadDirectory(path = "") {
    const res = await fetch(`${apiBase}/${path}`);
    const data = await res.json();

    const browser = document.getElementById("browser");
    browser.innerHTML = "";

    // 返回上级
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

    // 按类型和名称排序：目录在前，文件在后
    data.sort((a, b) => {
      if (a.type !== b.type) {
        return a.type === "dir" ? -1 : 1;
      }
      return a.name.localeCompare(b.name);
    });

    // 显示每个文件/目录
    data.forEach(item => {
      const link = document.createElement("a");
      const isDir = item.type === "dir";

      link.href = "#";
      link.innerText = (isDir ? "📁 " : "📄 ") + item.name;
      link.style.display = "block";
      link.style.margin = "4px 0";
      link.style.fontWeight = isDir ? "bold" : "normal";
      link.style.color = isDir ? "#0366d6" : "#333";

      if (isDir) {
        link.onclick = () => {
          loadDirectory(path ? `${path}/${item.name}` : item.name);
          return false;
        };
      } else {
        // 构造 GitHub Pages 链接
        const pageUrl = `https://${owner}.github.io/${repo}/${path ? path + '/' : ''}${item.name}`;
        link.href = pageUrl;
        link.target = "_blank";
      }

      browser.appendChild(link);
    });
  }

  loadDirectory();
</script>

