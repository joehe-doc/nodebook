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

    data.forEach(item => {
      const link = document.createElement("a");
      link.href = "#";
      link.innerText = item.name;
      link.style.display = "block";
      link.style.margin = "5px 0";

      if (item.type === "dir") {
        link.onclick = () => {
          loadDirectory(path ? `${path}/${item.name}` : item.name);
          return false;
        };
      } else {
        // 使用 GitHub Pages 链接，而不是 GitHub 仓库链接
        const pageUrl = `https://${owner}.github.io/${repo}/${path ? path + '/' : ''}${item.name}`;
        link.href = pageUrl;
        link.target = "_blank";
      }

      browser.appendChild(link);
    });
  }

  loadDirectory();
</script>
