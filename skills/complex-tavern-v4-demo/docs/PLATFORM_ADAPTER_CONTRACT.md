# 平台中立的运行与交付合同

适配器只负责能力发现、界面呈现、获取玩家当前输入；状态唯一写入者仍为 Core 的 Authority。任何平台组件都不能直接改时间、关系、Canon 或资源。当前 gate 的 option_id 才是实际身份；字母是临时标签。

合成示例（非实际故事）：

    {"scope":{"story_id":"synthetic","branch_id":"main"},
     "gate_id":"demo-gate-01","exit_mode":"decision_required",
     "options":[{"option_id":"o1","label":"A","intent":"询问安排"},
                {"option_id":"o2","label":"B","intent":"暂时观察"}],
     "allow_free_action":true}

A/B 必须基于当前 gate 映射；“先B再A”是 Core 顺序队列；旧卡选择/重复提交不得二次结算。“0次/1次/2次”是额外自检 meta 命令，不进入剧情。

有真实 decision_required/scope_boundary 时输出正文、当前选项及四行收尾；纯查询/暂停/真实阻塞可无菜单。Muse 缺 token、GPT-6 缺控件、地图缺 POS 时以文字降级。未知状态值不能杜撰；所有隐私故事数据不得进入公共例子。
