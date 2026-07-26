const DEMO = `# 把任何材料变成可发布内容：我用 Everything2template 做了一稿三发

创作者最耗时间的不是「写」，而是「同一件事用三种平台语言再说一遍」。

公众号要有钩子和小节；小红书要关键词前置和步骤感；知乎要结论先行和边界条件。手动改三遍，质量还容易塌成「换皮粘贴」。

## 问题
- 源材料形态太多：网页、PDF、文档、代码、整个项目
- 平台语风差异大，模板套用不等于平台原生
- 导出经常卡在「只能复制文本」

## 方法
1. 先把材料摄入成 CIR
2. 再按平台模板重写结构
3. 用质量门禁检查套话、长度、CTA
4. 导出 Markdown / PDF / 公众号 HTML

## 结果
你得到的是三到五份可继续精修的平台草稿 + 可交付文件。
`;

let state = { platforms: [], current: 0 };

async function init() {
  const meta = await fetch("/api/meta").then((r) => r.json());
  document.getElementById("version").textContent = `v${meta.version} 试用台`;
  const hint = document.getElementById("llmHint");
  if (hint) {
    if (meta.llm_enabled) {
      const L = meta.llm || {};
      hint.textContent = `LLM 已启用：${L.provider || "deepseek"} / ${L.model || ""}`;
    } else {
      hint.textContent = "未配置密钥：复制 .env.example 为 .env，填入 DEEPSEEK_API_KEY 后重启";
    }
  }
  const box = document.getElementById("platforms");
  meta.platforms.forEach((p, i) => {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "chip on";
    b.dataset.id = p.id;
    b.textContent = p.label;
    b.onclick = () => b.classList.toggle("on");
    box.appendChild(b);
    if (i < 5) state.selected = true;
  });
  const voice = document.getElementById("voice");
  (meta.voices || []).forEach((v) => {
    const o = document.createElement("option");
    o.value = v.id;
    o.textContent = v.display_name || v.id;
    voice.appendChild(o);
  });
}

function selectedPlatforms() {
  return [...document.querySelectorAll(".chip.on")].map((el) => el.dataset.id);
}

document.getElementById("demo").onclick = () => {
  document.getElementById("source_text").value = DEMO;
  document.getElementById("source_url").value = "";
};

document.getElementById("run").onclick = async () => {
  const btn = document.getElementById("run");
  const status = document.getElementById("status");
  btn.disabled = true;
  status.textContent = "转换中…";
  const fd = new FormData();
  fd.append("source_text", document.getElementById("source_text").value);
  fd.append("source_url", document.getElementById("source_url").value);
  fd.append("platforms", selectedPlatforms().join(","));
  fd.append("voice", document.getElementById("voice").value);
  fd.append("humanize", document.getElementById("humanize").checked ? "1" : "0");
  fd.append("use_llm", document.getElementById("use_llm").checked ? "1" : "0");
  const file = document.getElementById("upload").files[0];
  if (file) fd.append("upload", file);

  try {
    const res = await fetch("/api/convert", { method: "POST", body: fd });
    const data = await res.json();
    if (!data.ok) throw new Error(data.error || "转换失败");
    render(data);
    status.textContent = `完成 · 输出目录 ${data.out_dir}`;
  } catch (e) {
    status.textContent = e.message || String(e);
  } finally {
    btn.disabled = false;
  }
};

function render(data) {
  state.platforms = data.platforms || [];
  state.current = 0;
  const scoreBox = document.getElementById("scoreBox");
  const results = document.getElementById("results");
  scoreBox.classList.remove("hidden");
  results.classList.remove("hidden");
  const eff = data.effect;
  document.getElementById("scoreNum").textContent = eff.score;
  document.getElementById("scoreVerdict").textContent = eff.verdict;
  document.getElementById("scoreSub").textContent =
    `${eff.pass_count}/${eff.total} 平台通过 · 模式 ${eff.mode || "-"} · CIR「${data.cir.title || "未命名"}」`;
  document.getElementById("scoreNum").style.color = eff.commercializable_hint
    ? "var(--ok)"
    : "var(--danger)";

  const tabs = document.getElementById("tabs");
  tabs.innerHTML = "";
  state.platforms.forEach((p, i) => {
    const t = document.createElement("button");
    t.type = "button";
    t.className = "tab" + (i === 0 ? " on" : "");
    t.textContent = `${p.label}${p.ok ? " ✓" : " !"}`;
    t.onclick = () => {
      state.current = i;
      [...tabs.children].forEach((c, j) => c.classList.toggle("on", j === i));
      showPlatform(i);
    };
    tabs.appendChild(t);
  });
  document.getElementById("brief").textContent = data.cir.brief || "";
  showPlatform(0);
}

function showPlatform(i) {
  const p = state.platforms[i];
  if (!p) return;
  document.getElementById("pTitle").textContent = p.label;
  const badges = document.getElementById("badges");
  badges.innerHTML = "";
  const add = (text, ok) => {
    const s = document.createElement("span");
    s.className = "badge " + (ok ? "ok" : "bad");
    s.textContent = text;
    badges.appendChild(s);
  };
  add(`校验 ${p.validate.score}`, p.validate.ok);
  add(p.compliance.ok ? "合规通过" : `合规命中: ${(p.compliance.hits || []).join(",") || "否"}`, p.compliance.ok);
  if ((p.validate.warnings || []).length) {
    add(`警告 ${p.validate.warnings.length}`, false);
  }
  const ul = document.getElementById("titles");
  ul.innerHTML = "";
  (p.titles || []).forEach((t) => {
    const li = document.createElement("li");
    li.textContent = t;
    ul.appendChild(li);
  });
  document.getElementById("draft").textContent = p.draft || "";
  document.getElementById("images").textContent = p.image_plan || "";
}

init().catch((e) => {
  document.getElementById("status").textContent = "元数据加载失败: " + e;
});
