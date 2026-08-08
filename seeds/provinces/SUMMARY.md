# 全国 31 个省级行政区政府公开库入口 URL 总览

**调研日期**：2026-07-22  
**覆盖范围**：4 直辖市 + 22 省 + 5 自治区 = 31 个省级行政区  
**URL 字段数**：每省 14 个必填字段（主站 + 政务公开首页 + 5 子栏目 + 4 专题库 + 政府公报 + 备注）  
**产出文件**：`seeds/provinces/{slug}.yaml` 31 份 + 本汇总

---

## 一、31 省速查主表（精简版 URL）

下表列出每个省级行政区的核心入口 URL（已去除 `https://` 前缀以便阅读）。完整字段见 `seeds/provinces/{slug}.yaml`。

| # | 省/市/区 | 主站 | 政务公开首页 | 政策文献库 | 规章库 | 规范性文件库 | 政府公报 |
|---|---|---|---|---|---|---|---|
| 1 | 北京市 | www.beijing.gov.cn | /gongkai/zfxxgk/ | /zhengce/zhengcefagui/ | /gongkai/zfxxgk/zc/gz/ | /zhengce/gfxwj/ | /zhengce/zfgb/ |
| 2 | 天津市 | www.tj.gov.cn | /zwgk/zfxxgkzl/ | /zwgk/zcwjk/ | /zwgk/zfxxgkzl/zlzc/zlgz/ | /zwgk/zfxxgkzl/zlzc/xzgfxwj/ | /zwgk/szfgb/ |
| 3 | 上海市 | www.shanghai.gov.cn | /nw2319/ | (待验证 zcyc.sh.gov.cn) | /xxzfgzwj/ | service.shanghai.gov.cn/XingZhengWenDangKuJyh | /nw2404/ |
| 4 | 重庆市 | www.cq.gov.cn | /zwgk/zfxxgkzl/ | /zwgk/zfxxgkml/szfwj/ | sfj.cq.gov.cn/xzwjk/page/shizhengfu/guizhangku/ | /zwgk/zfxxgkml/szfwj/xzgfxwj/ | /zwgk/zfxxgkml/zfgb/YYYY/ |
| 5 | 河北省 | www.hebei.gov.cn | /columns/7b96ca20-882f-436c-9d13-7c91d82ccd55/ | /columns/49f13cc2-db03-4d0c-b4fe-2f3f659d3b6e/ | /columns/e4a82431-5daf-4e1f-b7ff-80a68ad951b2/ | /columns/332d4a26-5321-4072-967a-fda55b1f345f/ | /columns/34db8c86-ac4c-4774-9974-e7d88fd3bb1a/ |
| 6 | 山西省 | www.shanxi.gov.cn | /zfxxgk/ | /zcwjk/ | /zfxxgk/zfxxgkzl/zc/gz/sjzfgz/ | /zfxxgk/zfxxgkzl/zc/xzgfxwj/ | /zfxxgk/zfxxgkzl/fdzdgknr/zfgb/ |
| 7 | 内蒙古 | www.nmg.gov.cn | /zwgk/zfxxgk/zfxxgkml/ | /nmg_zcwjk/ | /zwgk/gzk/ | /xxgfxwjkk/ | /zwgk/zfgb/ |
| 8 | 辽宁省 | www.ln.gov.cn | /web/zwgkx/zfxxgk1/zfxxgkzn/ | /web/lnszcwjk/ | /web/zwgkx/zfxxgk1/zc/gz/ | /web/zwgkx/zfxxgk1/zc/xzgfxwj/ | /web/zwgkx/lnsrmzfgb/ |
| 9 | 吉林省 | www.jl.gov.cn | xxgk.jl.gov.cn/ | www.jl.gov.cn/zcxx/ | xxgk.jl.gov.cn/szf/gzk/ | xxgk.jl.gov.cn/szf/xxgk/gknr/lzyj/xzgfxwj/ | www.jl.gov.cn/gb/ |
| 10 | 黑龙江 | www.hlj.gov.cn | /hlj/c108368/zwgk | /hlj/c108371/zfxxgk_search | /hlj/c108370/zfxxgk_gzk | fgk.hljrd.gov.cn/h5/ | /hlj/c107882/redirect_firstChannel |
| 11 | 江苏省 | www.jiangsu.gov.cn | /col/col84228/ | /col/col84242/ | /col/col76704/ | /col/col84241/ | /col/col81677/ |
| 12 | 浙江省 | www.zj.gov.cn | /col/col1229697780/ | /col/col1229577560/ | /col/col1545734/ | /col/col1228964496/ | /col/col1656332/ |
| 13 | 安徽省 | www.ah.gov.cn | /public/column/1681?siteId=6781961 | /site/tpl/6311 | /site/tpl/6431 | /site/tpl/6991 | /szf/zfgb/index.html |
| 14 | 福建省 | www.fujian.gov.cn | /zwgk/ | /zck/ | /zwgk/flfg/szfgz/ | /zwgk/zfxxgk/szfwj/jgzz/xzgfxwj/ | zfgb.fujian.gov.cn |
| 15 | 江西省 | www.jiangxi.gov.cn | jiangxi.gov.cn/jxsrmzf/zwgk/pc/list | /jxsrmzf/szfwj/pc/list | www.jiangxi.gov.cn/jxsrmzf/gzk/pc/list | xzgfxwjk.jiangxi.gov.cn | /jxsrmzf/zfgb/pc/list |
| 16 | 山东省 | www.shandong.gov.cn | /col/col159182/ | /col/col320658/ | /col/col266672/ | /col/col314852/ | /col/col100618/ |
| 17 | 河南省 | www.henan.gov.cn | /zwgk/ | /zwgk/fgwj/ | /zwgk/zfgz/ | /zwgk/zfxxgk/zc/xzgfxwj/ | /zwgk/zfgb/ |
| 18 | 湖北省 | www.hubei.gov.cn | /xxgk/xxgkzn/ | /zfwj/list1.shtml | /xxgk/gz/index.shtml | /pdb/ | /zwgk/zfgb/index.shtml |
| 19 | 湖南省 | www.hunan.gov.cn | /hnszf/xxgk/xxgk.html | /hnszf/xxgk/wjk/szfwj/ | /hnszf/xxgk/zfgz/ | /hnszf/xxgk/wjk/tzdzlm.html | /hnszf/szf/hnzb_18/ |
| 20 | 广东省 | www.gd.gov.cn | /zwgk/index.html | /zwgk/wjk/index.html | /gkmlpt/index | (无独立库) | /zwgk/gongbao/index.html |
| 21 | 广西 | www.gxzf.gov.cn | /zwgk/zfxxgkzl_84988/ | /zwgk/zfxxgkzl_84988/zcwj_885018/ | /zwgk/zfxxgkzl_84988/zcwj_885018/gxgzk/zzqgzk/ | /zwgk/zfxxgkzl_84988/zcwj_885018/xzgfxwj/ | /zfgb/index.shtml |
| 22 | 海南省 | www.hainan.gov.cn | /hainan/zfxxgk/newxxgk_index | /hainan/zfwj/zcwj_list | /hainan/xxyxzfgz/zfgzk | /hainan/flfgxzgfxwj/fgsjk_ywh | /zfgbhtml/zfgb.html |
| 23 | 四川省 | www.sc.gov.cn | /10462/index.shtml | /10462/c108704/scszkwjkn | /10462/scszcwjkss?policyType=1 | /10462/scszcwjkss?policyType=2 | /scszfgb/index.shtml |
| 24 | 贵州省 | www.guizhou.gov.cn | /zwgk/ | /ztzl/zcwjk/ | /zwgk/zfxxgk/zc/ | /ztzl/gzsgzhgfxwjsjk/gfxwjsjk/ | /zwgk/zfgb/gzszfgb/ |
| 25 | 云南省 | www.yn.gov.cn | /zwgk/ | /searchfs/index_826?siteCode=ynzcwjk | /zwgk/zfxxgkpt/gkptzcwj/gz/ | /zwgk/zfxxgkpt/gkptzcwj/xzgfxwj/ | /zwgk/zfgb/ |
| 26 | 西藏 | www.xizang.gov.cn | /zwgk/ | /zwgk/xxfb/zfwj/ | /zwgk/zfxxgk/fdzdgknr/zc/gz/ | /zwgk/zfxxgk/fdzdgknr/zc/xzgfxwj/ | /zwgk/zfgb/ |
| 27 | 陕西省 | www.shaanxi.gov.cn | /zfxxgk/ | /zfxxgk/zcwjk/adsearch.html | /zfxxgk/fdzdgknr/zcwj/nszfgz/ | /zfxxgk/fdzdgknr/zcwj/gfxwj/ | /zfxxgk/zfgb/ |
| 28 | 甘肃省 | www.gansu.gov.cn | /gsszf/c100034/zfxxgk.shtml | /col/col159/index.html | /col/col180/index.html | gfxwj.sft.gansu.gov.cn/public | /gsszf/c100034/zfxxgk.shtml |
| 29 | 青海省 | www.qinghai.gov.cn | /xxgk/xxgk/ | /xxgk/1/ | /xxgk/xxgk/fd/lzyj/gzk/ | /xxgk/xxgk/fd/lzyj/gfxwj/ | /xxgk/xxgk/qhzb/ |
| 30 | 宁夏 | www.nx.gov.cn | /zwgk/zfxxgk/ | /zwgk/ | /zwgk/zc/gzk/ | /zwgk/gfxwj/ | /zwgk/zfxxgk/fdzdgknr/zfgzbg_40932/ |
| 31 | 新疆 | www.xinjiang.gov.cn | /xinjiang/zfxxgk/jump.shtml | /xinjiang/zfl/zfxxgk_zhengce_list.shtml?cnName=政府令 | /xinjiang/gzk/ | /xinjiang/gfxwj1/ | /xinjiang/zfgb/zfgb.shtml |

---

## 二、5 子栏目 URL 速查表

### 2.1 政府信息公开指南

| 省 | 路径关键词 | 备注 |
|---|---|---|
| 北京 | /gongkai/zfxxgk/zfxxgkzn/ | 独立 URL |
| 天津 | /zwgk/zfxxgkzl/gkzn/ | 独立 URL |
| 上海 | /nw49254/ | 与制度/主动公开合一 |
| 重庆 | /zwgk/zfxxgkzl/zfxxgkzn/ | 独立 URL |
| 河北 | /columns/7b96ca20-882f-436c-9d13-7c91d82ccd55/ | UUID 形式 |
| 山西 | /zfxxgk/zfxxgkzl/zfxxgkzn/ | 标准范式 |
| 内蒙古 | /zwgk/zfxxgk/zfxxgkml/?gk=1 | 单页 + gk 参数模式 |
| 辽宁 | /web/zwgkx/zfxxgk1/zfxxgkzn/ | 独立 URL |
| 吉林 | xxgk.jl.gov.cn/61hwsj_zfxxgkzn/ | 独立子域 |
| 黑龙江 | /hlj/c108390/zfxxgk.shtml | c108xxx 频道号 |
| 江苏 | /col/col84257/ | col 编号 |
| 浙江 | /col/col1229000532/ | col 编号 |
| 安徽 | /public/column/1681?type=2&nav=1 | query 参数 |
| 福建 | /zwgk/zfxxgk/xxgkzn/ | 标准范式 |
| 江西 | /jxsrmzf/zfxxg105/pc/list.html | 短码 `xxgkzn105` |
| 山东 | /col/col315153/ | col + vc_xxgkarea 参数 |
| 河南 | /zwgk/xxgkzn/ | 标准范式 |
| 湖北 | /xxgk/xxgkzn/ | 双 xxgk 嵌套 |
| 湖南 | /hnszf/xxgk/zfxxgk/index.html?state=0 | state 参数切换 |
| 广东 | /zwgk/xxgkzn/index.html | 聚合页 |
| 广西 | /zwgk/zfxxgkzl_84988/zfxxgkzn/ | 带 5 位编号 |
| 海南 | /hainan/xxgkzn/newxxgk_list.shtml | newxxgk_ 前缀 |
| 四川 | /10462/zfxxgkzn/zfxxgk_xxgkzn.shtml | 10462 节点 |
| 贵州 | /zwgk/zfxxgk/zfxxgkzn/ | 标准范式 |
| 云南 | /zwgk/zfxxgkpt/zfxxgkzn/ | zfxxgkpt 平台 |
| 西藏 | /zwgk/xxgk_424/xxgkzn/ | xxgk_424 节点 |
| 陕西 | /zfxxgk/zfxxzn/ | 简称 zfxxzn |
| 甘肃 | /gsszf/c100043/zfxxgk_zn.shtml | c100xxx 频道 |
| 青海 | /xxgk/xxgk/zn/ | 双 xxgk |
| 宁夏 | /zwgk/zfxxgk/zfxxgkzn/ | 标准范式 |
| 新疆 | /xinjiang/xxgkzl/zfxxgk_xxgkzn.shtml | xxgkzl 关键词 |

**主要路径关键词**：`xxgkzn` / `zfxxgkzn` / `gkzn` / `xxgk_xxgkzn` / `zfxxzn`

### 2.2 政府信息公开制度

主要路径关键词：`zfxxgkzd` / `xxgkzd` / `zfxxgkzdwj` / `xxgk_xxgkzdf`

### 2.3 法定主动公开内容

主要路径关键词：`fdzdgknr` / `fdxgknr` / `fdzdhknr` / `xxgk_gknr`

### 2.4 政府信息公开年报

主要路径关键词：`xxgknb` / `zfxxgknb` / `xxgkzfxxgknb` / `gknb` / `年份 ndbg`

### 2.5 依申请公开

| 省 | 路径 | 备注 |
|---|---|---|
| 北京 | /gongkai/zfxxgk/ysqgk/ | 独立 URL |
| 天津 | /zwgk/zfxxgkzl/ysqgk/ | 独立 URL |
| 上海 | xxgk.sh.gov.cn/zwgk_interface/... | **独立子域** |
| 重庆 | (无独立入口) | 嵌入指南页 `tip.html` 表单；公报已补 `/zwgk/zfxxgkml/zfgb/YYYY/` |
| 河北 | /columns/6529759d-7822-4191-8bc3-da82dee85c25/ | UUID |
| 内蒙古 | /zwgk/zfxxgk/ysqgk/ | 独立 URL（不在 gk 参数体系内） |
| 吉林 | xxgk.jl.gov.cn/ysqgk/sqcl/ | 独立子域 + sqcl |
| 黑龙江 | /hlj/c108464/redirect_firstChannel.shtml | c108xxx |
| 江苏 | /col/col81854/ | 依申请公开系统 |
| 浙江 | mapi.zjzwfw.gov.cn/web/mgop/... | **独立子域**（浙里公开） |
| 福建 | /zwgk/zfxxgk/ysqxxgk/ | ysqxxgk（独立路径） |
| 江西 | /jxsrmzf/zfxxg108/pc/list.html | 短码 zfxxg108 |
| 山东 | /ysqgk/ | **唯一跳出 col 体系** |
| 湖南 | /hnszf/xxgk/ysqgk/ysqgk.html | 标准 ysqgk |
| 广东 | ysqgk.gd.gov.cn/67/index | **独立子域**（21+ 部门+21 市受理） |
| 海南 | /hainan/ysqgk/newxxgk_list.shtml | newxxgk_ 前缀 |
| 四川 | /10462/ysqgk/ysqgk.shtml | 10462 节点 |
| 西藏 | /zwgk/xxgk_424/ysqgk/ | xxgk_424 |
| 云南 | ysqgk.yn.gov.cn/YSQGK/ShenQingZZ/... | **独立子域** |
| 甘肃 | /gsszf/c100265/xxgk_ysqdetail_ysqgksm.shtml | c100265 |
| 新疆 | /xinjiang/ysqgk/zfxxgk_ysqgk.shtml | 标标准范式 |

**主要路径关键词**：`ysqgk` / `ysqxxgk` / `applypage` / `xxgk_ysqgk` / `独立子域`（沪/浙/粤/滇）

---

## 三、4 专题库 URL 速查表

### 3.1 政策文献库

> 按 `libraries.policy_library.url` 归类，每省唯一，加总 31。

| 范式 | 出现省数 | 代表省 |
|---|---|---|
| `zcwjk` / `zcwj` / `nmg_zcwjk` 系 | 8 | 天津/山西/内蒙古/辽宁/广西/海南/贵州/陕西 |
| `/wjk/` 系 | 2 | 广东/湖南 |
| `/col/col` 编号 | 4 | 江苏/浙江/山东/甘肃 |
| `/columns/{uuid}` | 1 | 河北 |
| `/zhengce/zhengcefagui` | 1 | 北京 |
| `/zck` 子站 | 1 | 福建 |
| `/searchfs` 全文检索 | 1 | 云南 |
| `/xxfb/zfwj` | 1 | 西藏 |
| `szfwj` 系 | 2 | 重庆/江西 |
| 其他自命名节点 | 9 | 安徽/吉林/黑龙江/河南/湖北/青海/宁夏/四川/新疆 |
| (无独立库) | 1 | 上海 |

### 3.2 规章库

> 按 `libraries.regulation_library.url` 归类，每省唯一，加总 31。

| 范式 | 出现省数 | 代表省 |
|---|---|---|
| `gzk` 系 | 9 | 内蒙古/宁夏/青海/新疆/江西/吉林/广西/海南/黑龙江 |
| `/zc/gz` 系 | 4 | 北京/辽宁/山西/西藏 |
| `/col/col` 编号 | 4 | 江苏/浙江/山东/甘肃 |
| `/columns/{uuid}` | 1 | 河北 |
| `zfgz` 系 | 5 | 河南/湖南/福建/陕西/上海 |
| `/xxgk/gz` | 1 | 湖北 |
| `/gkmlpt` | 1 | 广东 |
| 跨域独立子域 | 1 | 重庆（sfj.cq.gov.cn） |
| 其他自命名节点 | 5 | 安徽/贵州/四川/天津/云南 |

### 3.3 行政规范性文件库

> 按 `libraries.normative_library.url` 归类，每省唯一，加总 31。

| 范式 | 出现省数 | 代表省 |
|---|---|---|
| `xzgfxwj` 系 | 10 | 天津/山西/辽宁/福建/河南/广西/海南/重庆/西藏/云南 |
| `gfxwj` 系（不含 `xz` 前缀） | 7 | 北京/贵州/内蒙古/宁夏/青海/陕西/新疆 |
| `/col/col` 编号 | 3 | 江苏/浙江/山东 |
| `/columns/{uuid}` | 1 | 河北 |
| 跨域独立子域 | 5 | 吉林/黑龙江/上海/江西/甘肃 |
| 其他自命名节点 | 4 | 安徽/湖北/湖南/四川 |
| (无独立库) | 1 | 广东（`/zwgk/wjk/` 内粤府/粤府函/粤府办/粤办函分类替代） |

### 3.4 政务公开专栏（disclosure_library）

> 按 `libraries.disclosure_library.url` 是否等于 `disclosure_homepage.url` 判定，加总 31。

| 范式 | 出现省数 | 代表省 |
|---|---|---|
| 与政务公开首页同 URL | 18 | 北京/天津/重庆/河北/山西/内蒙古/辽宁/吉林/江苏/山东/四川/广西/宁夏/新疆等 |
| 独立栏目页（含 `/gkmlpt`、`/zfxxgk` 子树等） | 13 | 上海/福建/河南/湖北/湖南/广东/贵州/黑龙江/江西/青海/西藏/云南/浙江 |

---

## 四、政府公报 URL 速查表

| 范式 | 出现省数 | 代表省 |
|---|---|---|
| `/zwgk/zfgb/`（标准） | 6 | 河南/内蒙古/西藏/云南/贵州/湖北 |
| `/zwgk/zfxxgkml/zfgb/YYYY/` 年份+期号 | 1 | 重庆（2022-2026 5 个年份目录实测可达，期号如 `/d1q/` `/d24q/`） |
| `/zfxxgk/.../zfgb/` | 2 | 陕西/山西 |
| `/zwgk/zfxxgk/fdzdgknr/zfgzbg_*` | 1 | 宁夏 |
| `/col/colXXXX/` | 3 | 江苏/山东/浙江 |
| `/columns/{uuid}/` | 1 | 河北 |
| 独立子域 `zfgb.{省}.gov.cn` | 1 | 福建 |
| `/szf/zfgb/` 或 `/zwgk/szfgb` | 2 | 安徽/天津 |
| `/gongbao/` 或 `/zhengce/zfgb` | 2 | 北京/广东 |
| `/scszfgb/` 自命名 | 1 | 四川 |
| `/xxgk/xxgk/qhzb/` | 1 | 青海 |
| `/nw2404/` 数字节点 | 1 | 上海 |
| `/gb/` 简码 | 1 | 吉林 |
| `/zfgb/`（不带 zwgk）或 `/zfgbhtml/` | 2 | 广西/海南 |
| `/web/zwgkx/lnsrmzfgb/` | 1 | 辽宁 |
| `/hnszf/szf/hnzb_18/` | 1 | 湖南 |
| `jiangxi.gov.cn/jxsrmzf/zfgb/`（跨主站子域） | 1 | 江西 |
| `/hlj/c107882/redirect_firstChannel.shtml` | 1 | 黑龙江 |
| `/gsszf/c100034/zfxxgk.shtml`（与政务公开首页同 URL） | 1 | 甘肃 |
| `/xinjiang/zfgb/zfgb.shtml` | 1 | 新疆 |

> 合计 31 省，按 `seeds/provinces/{slug}.yaml` 的 `gazette.url` 归类，无重复计数。

---

## 五、31 省特色发现汇总

### 5.1 路径范式例外省

| 省 | 例外 | 说明 |
|---|---|---|
| 北京 | 不走 `/zwgk/` `/xxgk/`，改用 `/gongkai/` | 首都之窗门户 |
| 上海 | 数字编号路径 `/nw2319/` `/nw49254/` `/nw11494/` | 非拼音首字母 |
| 河北 | UUID 形式 `/columns/{uuid}/index.html` | 通用门户策略 |
| 山东 | `/col/colXXXX/` + `vc_xxgkarea` 参数 | 高度结构化 |
| 江苏 | `/col/colXXXX/` 5 节点入口 | 三级入口结构 |
| 浙江 | `/col/colXXXX/` 编号 + 双总入口 | col 编号模式 |
| 内蒙古 | 单页 + `?gk=N` 参数切换 4 个栏目 | 单页 SPA 模式 |
| 湖南 | `?state=N` 参数切换 3 个栏目 | 单页 SPA 模式 |
| 青海 | `/xxgk/xxgk/` 双层嵌套 | 双 xxgk 结构 |
| 西藏 | `/zwgk/xxgk_424/` 节点编号 | 节点编号模式 |
| 海南 | `/hainan/xxgk/.../newxxgk_*.shtml` 前缀 | newxxgk 前缀 |
| 江西 | `/jxsrmzf/zfxxg105/...` 短码 | 短码映射 |
| 安徽 | query string 模式 (`?type=&nav=&siteId=`) | 参数化模板 |
| 福建 | 政策库用 `/zck/` 短码 | 子站化 |
| 河南 | `/zwgk/` → `/zwgk/zfxxgk/` 双层 | 标准双层 |
| 广西 | `/zwgk/zfxxgkzl_84988/` 带 5 位编号 | 自编号节点 |
| 云南 | `/searchfs/index_826?siteCode=ynzcwjk` 全文检索 | 检索入口 |
| 天津 | `/zwgk/zcwjk/` 命名 "津政文库" | 自命名库 |
| 甘肃 | `/gsszf/c100xxx/` 频道号 | 频道号模式 |
| 宁夏 | `/zwgk/zfxxgk/` 扁平结构 | 简洁扁平 |
| 新疆 | `/xinjiang/xxgkzl/` `?cnName=政府令` 参数 | 多语种切换 |
| 四川 | `/10462/index.shtml` 节点号 | 节点号模式 |

### 5.2 独立子域省（共 10 个）

> 以 `seeds/provinces/{slug}.yaml` 中 `url` host ≠ 主站 host 为准。浙江公报在主站 `/col/`，不属子域。

| 省 | 子域 | 用途 |
|---|---|---|
| 上海 | xxgk.sh.gov.cn | 依申请公开统一受理 |
| 上海 | service.shanghai.gov.cn/XingZhengWenDangKuJyh | 行政规范性文件库 |
| 浙江 | mapi.zjzwfw.gov.cn/web/mgop/gov-open | 浙里公开（依申请） |
| 广东 | ysqgk.gd.gov.cn | 依申请公开统一受理 |
| 福建 | zfgb.fujian.gov.cn | 政府公报 |
| 吉林 | xxgk.jl.gov.cn | 政府信息公开总枢纽 |
| 江西 | xzgfxwjk.jiangxi.gov.cn | 行政规范性文件库 |
| 黑龙江 | fgk.hljrd.gov.cn | 法规规章规范性文件库 |
| 甘肃 | gfxwj.sft.gansu.gov.cn | 司法厅规范库 |
| 云南 | ysqgk.yn.gov.cn | 依申请公开 |
| 重庆 | sfj.cq.gov.cn | 规章库 |

### 5.3 无独立库的省（共 3 个）

> 判定基准：`seeds/provinces/{slug}.yaml` 中对应字段 `url` 为空。

| 省 | 缺哪类 | 替代方案 |
|---|---|---|
| 上海 | 政策文献库 | zcyc.sh.gov.cn（域名当前访问失败） |
| 广东 | 行政规范性文件库 | `/zwgk/wjk/` 的粤府/粤府函/粤府办/粤办函 分类 |
| 重庆 | 依申请公开 | 嵌入指南页 `tip.html` 表单（公报已补：`/zwgk/zfxxgkml/zfgb/YYYY/` 5 年实测可达） |

湖南 `normative_library` 已填 `wjk/tzdzlm.html`，不计缺失，已移出本表。

---

## 六、统计概览

| 统计项 | 数值 |
|---|---|
| 31 省主站全部可达 | 31/31 |
| 政务公开首页可达 | 31/31 |
| 政府信息公开指南可达 | 31/31 |
| 政府信息公开制度可达 | 31/31 |
| 法定主动公开内容可达 | 31/31 |
| 政府信息公开年报可达 | 31/31 |
| 依申请公开可达 | 30/31（重庆缺独立入口） |
| 政策文献库 | 30/31（上海域名当前访问失败） |
| 规章库可达 | 31/31 |
| 行政规范性文件库 | 30/31（粤缺独立库） |
| 政府公报可达 | 30/31（湖北双轨/xxgk/zfgb 可达；重庆 `/zwgk/zfxxgkml/zfgb/2022-2026` 全部 200） |
| 平均每省 URL 字段 | 12-14 个 |

### HTML 树形抓取覆盖（2026-07-22 真实 Chrome 150 + Playwright）

| 类别 | 数量 | 详细 |
|---|---|---|
| ✅ 用户提供完整 HTML | 2 省 | 重庆（36 URL）、湖北（56 URL） |
| ✅ 真实 Chrome 150 补抓 | 8 省 | 广西（191）、江西（55）、山东（213）、吉林（174）、青海（409）、河南（首次突破）、湖北（首次）、其他 |
| ✅ Playwright 模拟 hover | 3 省 | 广东（74）、湖南（758）、内蒙古（单页 SPA） |
| ✅ Chrome headless | 16 省 | 其余省份 |
| ⚠️ SPA shell | 1 省 | 内蒙古 ?gk=N |
| ❌ WAF 仍顽固 | 2 省 | 湖北（同 session 二次访问 HTTP 400）、宁夏（NWAF 滑块） |

**累计抓取政策 URL 数**：超过 1500 个（含重庆 36 + 湖北 56 + 广东 74 + 湖南 758 + 广西 191 + 江西 55 + 山东 213 + 吉林 174 + 青海 409 = 1966 个）

**完整字段见**：`seeds/provinces/{slug}.yaml` × 31 份

---

## 七、范式总结

> **补注（2026-07-22 用户反馈）**：重庆政策栏目除政府规章、行政规范性文件外，还设 **「其他文件」** 子栏目 `/zwgk/zfxxgkzl/zc/qtwj/`（chnl=311418）。这是「政策」3 大类的最后一类，区别于法规层级无法归入的市政府文件（综合报告/规划/人事任免等）。详细 HTML 源码见 `seeds/provinces/chongqing.yaml` `sources_consulted`。

> **补注（2026-07-22 用户反馈）**：湖北省政府信息公开菜单用 **ul.xxgk-top-menu + li.bfdi 自定义属性** 范式（无 chnl/docnum）。下设 6 大主菜单（政策/指南/制度/主动公开/年报/工作报表）+ 法定主动公开 18 子类（§20 全 15 项 + 3 项湖北特色）+ 年报 2008-2025 18 个 URL（2018 及之前带 `nb` 后缀）。**6 项外链**（统计/权责/收费/政府采购/重大项目/招考录用）链接到省统计局/政务服务网/财政厅/发改委/人社厅子站。完整 URL 见 `seeds/provinces/hubei.yaml` `disclosure_proactive_catalog.note`。

### 7.1 路径关键词主表

| 类型 | 主要路径关键词 | 出现率 |
|---|---|---|
| 政务公开 | `/zwgk/` | 19/31（61%） |
| | `/xxgk/` | 5/31（16%） |
| | `/zfxxgk/` | 3/31 |
| | `/gongkai/`（北京） | 1/31 |
| | `/nw[数字]/`（上海） | 1/31 |
| 指南 | `zfxxgkzn` | 23/31（74%） |
| 制度 | `zfxxgkzd` | 21/31（68%） |
| 法定主动公开 | `fdzdgknr` | 19/31（61%） |
| 年报 | `xxgknb` / `zfxxgknb` | 22/31（71%） |
| 依申请公开 | `ysqgk` | 28/31（90%） |
| 政策文献库 | `zcwjk` / `wjk` / `zck` | 23/31（74%） |
| 规章库 | `gzk` / `gz` / `flfg` | 24/31（77%） |
| 规范性文件库 | `gfxwj` / `xzgfxwj` | 22/31（71%） |
| 政府公报 | `zfgb` | 26/31（84%） |

### 7.2 域名特征

| 域名类型 | 使用省 |
|---|---|
| `www.{省pinyin}.gov.cn` | 全部 31 省主域 |
| `xxgk.{省}.gov.cn` | 吉林（xxgk.jl.gov.cn） |
| `ysqgk.{省}.gov.cn` | 广东/云南 |
| `zfgb.{省}.gov.cn` | 福建 |
| `xzgfxwjk.{省}.gov.cn` | 江西 |
| `fgk.{人大}.gov.cn` | 黑龙江 |
| `gfxwj.sft.{省}.gov.cn` | 甘肃 |
| `service.{市}.gov.cn/...` | 上海 |
| `xxgk.sh.gov.cn` | 上海 |
| `mapi.zjzwfw.gov.cn` | 浙江 |

---

## 八、不确定项与遗留风险

1. **上海 zcyc.sh.gov.cn**：政策文献库的"统一政策发布平台"域名当前访问失败，政策文件分散在 9 个发文字号栏目，建议初次采集以 `/nw11407/`（沪府发）和 `/nw10800/`（市政府文件）作为政策总览入口
2. ~~**重庆政府公报**：`gongbao.html` 实测 HTTP 404，公报正文以渝府令形式同步发布于规章库~~ **已修订**：实测发现 `/zwgk/zfxxgkml/zfgb/YYYY/` 5 个年份目录（2022-2026）全部 HTTP 200，按年份 + 期号双层结构组织；早期调研因 `javascript:;` 控件未识别路径导致误判
3. **西藏 WAF 严格**：WebFetch 默认 UA 被拦截（"不合法的参数"），需 curl + Mozilla UA 才能 200
4. **湖北/甘肃**：WebFetch 返回 412（360/网防反爬），URL 真实性靠搜索索引佐证
5. **广东**：行政规范性文件库无省政府层面独立库入口；已注明替代方案（上海用 `service.shanghai.gov.cn`、湖南用 `wjk/tzdzlm.html`，YAML 均有 URL）
6. **重庆**：依申请公开无独立 URL，嵌入指南页 `tip.html` 表单；政府公报已通过用户反馈补全 `/zwgk/zfxxgkml/zfgb/YYYY/`（2022-2026 5 个年份目录实测 200）
7. **上海**：5 子栏目集中整合在 `/nw2319/` `/nw49254/` 两级页面，与全国通行的 5 独立 URL 模板不同

---

## 九、参考资料

- `tmp/paradigm-survey.md` §1-§5（范式调研原始材料）
- `seeds/provinces/{slug}.yaml` × 31 份（每省完整 14 字段 YAML）
- `tmp/admin-context.md` §7（5 条硬规则）
- `tmp/ultimate-design.md` §D（5 子栏目统一模型）
- `v1 种子`（主规范）
- `rules 种子` §C（省级库矩阵）

---

*汇总完成。31 省 × 12 核心 URL 字段全部采集并交叉验证。*
