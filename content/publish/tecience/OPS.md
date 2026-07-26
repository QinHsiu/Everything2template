# Tecience 发布操作手册（今晚）

目标：把产品侧闭环变成**真实可点的公众号漏斗**。

## 15 分钟发表首发文

1. 打开 `launch_wechat.wechat.html`（由 `closed_loop_verify` 自动导出；也可 `e2t export`）。
2. 登录 [微信公众平台](https://mp.weixin.qq.com/) → 公众号 **Tecience**。
3. 新建图文 → 从浏览器打开 HTML → 全选复制 → 粘贴到编辑器（按需微调封面）。
4. 摘要用文内 blockquote；作者可写 Tecience。
5. **发表**（或定时今晚）。

## 10 分钟配置关键词

路径：自动回复 / 关键词回复。粘贴 `auto_reply.md` 三段：

- `E2T` `模板` `改写`
- `付款` `Pro` `99`
- `已付`
- `试用`

## 5 分钟收款

1. 准备微信收款码，上传素材库。
2. 在「付款」关键词回复里插图。
3. 本地记下 `secrets/tecience_pay_qr.png`（gitignore）。

## 验收

- [ ] 未关注用户能搜到 Tecience
- [ ] 回复 E2T 有价目
- [ ] 首发文文末 CTA 正确
- [ ] Pro zip 链接可下载（付款测试用小号）

完成以上 = **运营侧闭环点亮**。产品侧用：

```bash
python scripts/closed_loop_verify.py
```
