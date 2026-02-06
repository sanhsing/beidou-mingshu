# 北斗命數 API v1.0

**古法是根，場論是枝，用戶是花**

## 📚 功能模組

| 模組 | 描述 | 經典依據 |
|:-----|:-----|:---------|
| 八字命理 | 年月日時四柱分析 | 《三命通會》《滴天髓》 |
| 紫微斗數 | 十二宮排盤 | 《紫微斗數全書》 |
| 姓名學 | 五格剖象分析 | 《康熙字典》+ 熊崎氏 |
| 梅花易數 | 數字起卦 | 《梅花易數》 |
| 奇門遁甲 | 時家奇門排盤 | 《奇門遁甲秘笈》 |

## 🚀 部署

```bash
# 本地運行
pip install -r requirements.txt
uvicorn main:app --reload

# Docker
docker build -t beidou-mingshu .
docker run -p 8000:8000 beidou-mingshu
```

## 📐 API 端點

- `GET /` - 首頁
- `GET /docs` - API 文檔
- `GET /api/v1/lunar/{year}/{month}/{day}` - 農曆轉換
- `POST /api/v1/bazi` - 八字分析
- `POST /api/v1/ziwei` - 紫微排盤
- `POST /api/v1/name` - 姓名分析
- `POST /api/v1/meihua` - 梅花起卦
- `POST /api/v1/qimen` - 奇門排盤
- `POST /api/v1/report` - 統合報告

## ⚖️ 認識論聲明

> 術數是個人化決策框架生成器，與天氣預報同構
> — 提供機率性參考，不做命定式裁決
>
> 趨吉避凶——趨和避都是動詞，主語是人

## 📜 原則

- 零廣告
- 不綁約
- 不裁決
- 不命定

---

北斗七星文創數位 | XTF8 Methodology
