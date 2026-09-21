# No-Rush Host Integration

## 目的
让 No-Rush 真正做到“用户不提 Skill 名也运行”。这是宿主加载问题，不是关键词匹配问题。

## 必须满足的宿主合同
1. 在会话首条用户消息进入普通路由前，预加载 canonical `skills/no-rush/SKILL.md`。
2. 后续每个用户回合继续把 No-Rush 作为 preflight/default controller；不要等待用户出现“不着急”关键词。
3. 用户明确关闭时只改变 No-Rush 的启用状态，不卸载其他任务 Skill。
4. GitHub 可访问时优先读取 canonical；缓存可以存在，但不得让旧缓存覆盖更新后的版本。
5. 任务专用 Skill 的顺序应是：No-Rush preflight → task-specific Skill → No-Rush Final Check / closing report。

## 参考路由
```text
on_user_turn(message):
  ensure_loaded(no_rush_canonical)
  state = no_rush.preflight(message, conversation_state)
  if state.needs_clarification:
      return clarification
  result = route_task_specific_skills(message, state.task_brief)
  return no_rush.final_check_and_close(result)
```

## 禁止的集成方式
- `if message contains "不着急" then load no-rush`
- 仅在复杂任务时加载 No-Rush
- 仅在某个模型或 thinking effort 下加载
- 把 GitHub 上传本身当成“已经安装/已经 always-on”

## 运行时边界
`SKILL.md` 是规则文件，没有能力在宿主完全没有读取它之前主动执行自己。因此：
- **仓库内已能修复**：零关键词合同、Question Scan、状态/收尾规范、测试与审计。
- **宿主必须配合**：默认 preload / preflight。若客户端不支持默认加载，本仓库不能单独强制它。

## 验收
至少覆盖：
- 用户完全不提 No-Rush 的简单问答仍进入 No-Rush；
- 用户完全不提 No-Rush 的复杂项目仍先做 Question Scan；
- 明确关闭/恢复生效；
- “直接做”跳过提问但不关闭 Final Check；
- 事实可检索时不反问；用户拥有的重要偏好不能被“合理默认值”静默代决。