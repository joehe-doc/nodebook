---
layout: default
title: Nodebook 文档主页
---

# 欢迎来到 Nodebook 文档

以下是所有文档的子目录链接：

{% assign directories = site.static_files | group_by: "path" | map: "name" | uniq %}

{% for dir in directories %}
  <h2>{{ dir }}</h2>
  <ul>
    {% for file in site.static_files %}
      {% if file.path contains dir and file.path != 'index.md' %}
        <li>
          <a href="{{ file.path | relative_url }}">{{ file.path }}</a>
        </li>
      {% endif %}
    {% endfor %}
  </ul>
{% endfor %}
