# Tecience 收款与交付

## SKU（与 sales 一致）

| SKU | 价格 | 交付物 |
|-----|------|--------|
| Hobby | 免费 | GitHub / Hobby zip |
| **Pro** | **¥99** 一次买断 | `releases/everything2template-pro-*.zip` + 声线/模板 + 12 个月模板更新说明 |
| Team | ¥499 | 5 席 + 异步 onboarding |

## 付款方式（运营填写）

在 Tecience 自动回复中三选一写清楚（今晚先选一种）：

1. **微信收款码**：把二维码放到素材库，自动回复发图 + 文案「备注 E2T-Pro」  
2. **赞赏码**：文章底部赞赏，金额选 99，备注昵称  
3. **商家转账**：对公/个人微信转账账号（仅私聊确认后发送）

占位（发布前替换）：

```text
【付款】扫码支付 ¥99，备注：E2T-Pro + 微信号
【交付】付款后回复「已付」，24h 内发送 Pro 包下载链接
【售后】安装失败附 e2t version 与报错，7 日内书面退款
```

收款码本地路径（可选，勿提交仓库）：`secrets/tecience_pay_qr.png`

## 交付 checklist

- [ ] 最新 Pro zip 已生成（`python scripts/build_release.py`）
- [ ] 网盘/私链有效期 ≥ 30 天
- [ ] 自动回复含「已付」分支
- [ ] SUPPORT 联系方式与 Tecience 一致
