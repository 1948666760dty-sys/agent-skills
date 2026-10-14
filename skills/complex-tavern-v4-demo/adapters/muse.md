# Muse 平台适配

真实宿主返回的本轮每张卡 embed_token 才有效，不可编造、复用、缓存冒充新 token。选项卡只单选；多步顺序用“先D再C”交原有 Action Queue。status/map/npc/options/shop/clues 仅可渲染用户已知、Core 验证的事实，绝不能成为第二个 Authority。

用户启用 expanded 时最多20个真实不同选项；不能每轮强制菜单，也不强制最后两个是成人选项。原版 12 HTML、CARDS.md、check_map.py 未提供，所以这里只定义行为适配，未声称原卡片原样复刻。若能力缺失，纯文字功能仍可运行，不伪造 token 和地图数据。
