#!/usr/bin/env python3
"""Hash-guarded demo.4 -> demo.5 patch and pure logical-contract checks.
Default: read-only. --apply: explicit one-time patch. No LLM/runtime tests.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

OLD_VERSION = '4.0.0-demo.4'
VERSION = '4.0.0-demo.5'
BASE_BLOB = '93d389a35365b31ade0af7cb377fbba359839cef'
DEMO = Path('skills/complex-tavern-v4-demo')
LABELS = ('已完成', '未完成', '存在问题', '需要你确认')

GUARD = r'''#### 3.3.1 Turn Exit Contract / 回合出口与过早停顿防护（demo.5）

本节细化 3.2、3.3 与 6.1，不新增第二套执行流程。只在普通剧情输出准备结束时检查；系统查询、审计和用户要求暂停不因本节而自动续写。核心：**无选项不等于该停止；需要归还控制权也不只限于重大危机。**

**合法出口与优先次序：**
1. 用户明确暂停、仅查询、要求只写到指定位置，或混合输入按约定需要先答问题：分别使用 `user_pause / meta_hold / requested_endpoint`。不为凑选项推进剧情、计时或执行被 hold 的行动。
2. 真实能力/安全/关键证据/持久化阻塞使用 `blocker`；真实单次执行边界使用 `technical_checkpoint`。如实说明已完成范围、未完成动作与恢复点，不伪造已经出现新的世界事件。
3. 有尚未授权的真实决定（包括有实际偏好意义的 D1）使用 `decision_required`；将控制权交回玩家。已有明确授权且没有新关键信息的同一决定不得再次提问。
4. 当前已经授权的行动、普通反应、同日转场或队列仍可自然继续，且不越过更高优先级边界时，标记 `continue` 并在本次可执行输出内继续写；它不是合法的终止原因。不得仅因已生成一段正文、某个 NPC 暂时离开、某个任务刚收尾或没有 D2/D3 就结束。
5. 已到授权范围边缘且下一步需要玩家选择时间用途、场景方向或是否跨天，使用 `scope_boundary`。允许提供真正的方向选择：留在当前时段继续某事、转换另一活动、明确授权结束当天/推进到约定时间，以及自由行动；不制造事故、争吵或新任务来凑 Decision Gate。
6. 用户要求的完整故事/明确交付目标已经达成才使用 `story_complete`。一次邀约确定、一顿饭结束、一个项目阶段完成都不自动等于整局完结。

`decision_required / scope_boundary` 必须配套可用入口：通常 3–6 个真实不同的行动 + 自由行动，真实差异少时宁缺勿凑；若确实无法诚实列出具体行动，用一个明确的自由行动问题归还控制权，不留“你还有自己的时间”然后无人可操作的空结尾。D1 的“今晚用于项目收尾、休闲还是休息”可是真实偏好；“嗯/好/知道了”三个同义回答不是三个分支。`autonomous_novel` 对已授权类别交给 Autonomous Player，不机械改成每回合询问真人；未授权类别/手动门仍归还用户，显示遵守既有 Content Edition。

**授权时间边界：**
- 必须继续尊重 `No Proactive Day Skip`。**未来约定不等于跨天授权**；“明天中午一起吃饭”只锁定那顿饭，不替主角决定今晚的全部活动、睡觉、次日上午或提前消耗这段时间。
- 用户明确“睡觉到明早/快进到午饭”等才许可相应时间跳跃；用户选择的行动本身自然跨午夜仍据实更新时间。未知绝对日期不补日历。
- 不能因“要继续到选项”而越过时间边界、替玩家作主或重新制造已完成任务的问题；同日范围用尽时提供 `scope_boundary`，而非自动跳天，也不是没菜单就停止。

**循环与队列防护：**
- 延续必须带来新的可观察信息、执行已授权动作或到达真实边界；反复写同一氛围/状态、重复“还有空闲”不算推进。连续无新信息时归还场景方向控制，不循环生成以追求长度。
- 恢复时重用当前 `pending_decision`、授权范围与已提交行动 ID。已执行的 A 不因再次解释 Bug、修订 Skill 或单说“继续”而重复邀约/扣资源/消耗一天；只执行真正未完成的队列尾部。
- `scene_closed` 是转场检查，不是终止指令。NPC 暂时不可用时可转向主角的合法活动或询问方向；不能等待 NPC 重新出现才允许游戏继续。
- 当功能不可用、正文达到真实技术边界或用户请求结束，允许无选项停止并说清原因；本节不是“每回合必有选项”或“无限续写直到有事故”。

**正文、出口、收尾必须一致：**
- `decision_required / scope_boundary` 下，“需要你确认”写当前行动入口，不得写“无”；`continue` 状态不得提前输出任务结束型收尾。
- “已完成”只记真实执行/提交的动作；“未完成”只记已接受但未完成的任务、有效待执行选择或真实阻塞，不把“还没想好吃什么/今晚还剩时间”等普通开放可能性都记成欠办任务。
- “存在问题”反映已知真实问题/限制；已发现未处理的阻塞不得填“无”。请求仅审计/修订时，人物状态、故事日期和 pending action 都保持不变。
- 四字段按 2.3 最新展示合同分别换行，正文可以结束但不能靠收尾替代需要给玩家的行动入口。

建议可选运行记录：`turn_exit = {mode, reason, decision_ref, authorization_scope, resume_point}`。这是可选派生/恢复提示，不改变已有 schema 的必需字段；demo.5 保持 `schema_version: 4.0-demo.4`，版本升级不改故事事实。

'''

FOOTER_RULE = '''2. **Closing Status By Category**：普通剧情交付、暂停和审计交付的四类收尾分别占一行，顺序固定为“已完成、未完成、存在问题、需要你确认”。分类之间使用真实换行，不再用 `｜` 把四类挤成一行。每类内容保持简短；确需解释的 Major/Critical 问题可先在正文展开。格式为：

   已完成：……
   未完成：……
   存在问题：……
   需要你确认：……

   内容须与 3.3.1 的真实出口一致：待选时不能写“需要你确认：无”；普通尚未决定的活动不自动算未完成任务。'''


def blob(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def one(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise ValueError('Expected one patch anchor: ' + old[:90])
    return text.replace(old, new, 1)


def patch_skill(text: str) -> str:
    text = text.replace(OLD_VERSION, VERSION)
    text = one(text, '### 2.3 Player Interaction Profile / 玩家交互档案（demo.4 默认）', '### 2.3 Player Interaction Profile / 玩家交互档案（demo.5 默认）')
    old = '2. **Closing Status Compact**：No-Rush 启用时，普通剧情交付的四栏收尾压成一行并保持顺序：`已完成：…｜未完成：…｜存在问题：…｜需要你确认：…`；出现 Major/Critical 问题时可以展开。不得省略四个字段。'
    text = one(text, old, FOOTER_RULE)
    text = text.replace('普通收尾采用 2.3 的四字段压缩单行。', '普通收尾采用 2.3 的四字段分类换行；这次用户明确的分类换行要求覆盖此前压缩成一行的偏好。')
    text = text.replace('普通 No-Rush 收尾是否用四字段压缩单行', '普通收尾是否按四个类别分别换行并与真实出口一致')
    text = text.replace('276. 普通剧情收尾必须保留 已完成/未完成/存在问题/需要你确认 四字段，可在同一行。', '276. 普通剧情收尾必须保留 已完成/未完成/存在问题/需要你确认 四字段；demo.5 按用户最新要求每类独立一行。')
    text = one(text, '### 3.4 Autonomous Player Policy / 自动主角决策策略', GUARD + '### 3.4 Autonomous Player Policy / 自动主角决策策略')
    text = one(text, '没有真实 Decision Gate 时不出菜单。', '没有真实 Decision Gate 时不制造假菜单，但仍按 3.3.1 判断继续、真实偏好决策、授权边界或合法停止，不能把没有菜单直接当成回复结束。')
    text = one(text, '19. **Output / Continue**：仅在按', '19. **Output / Continue**：先执行 3.3.1 Turn Exit Contract：continue 返回已授权叙事，decision_required/scope_boundary 提供可用行动入口，其余合法出口说明原因；没有实际继续不声称已推进。再仅在按')
    text = one(text, '### 6.1 输出与选项规则', '### 6.1 输出与选项规则\n\n**Turn Exit Guard**：输出前按 3.3.1 检查正文、待执行选择、授权时间范围与四类收尾；没有 D2/D3 不等于没有 D1 方向决定，也不等于允许空停。到授权边界可给真实方向选择，禁止为了继续擅自跨天。')
    text = one(text, '3. **Decision Gate**：是否在 D0/D1 小事上无意义停顿；是否漏掉未授权 D3', '3. **Decision Gate / Turn Exit**：是否在已授权 D0/D1 上重复询问；是否漏掉未授权 D3、真实 D1 方向选择或 scope_boundary；是否把无菜单直接当结束；是否为了找选项越过 No Proactive Day Skip；菜单与四行收尾是否一致。')
    text = one(text, '### 3.3 Narrative Continuation Gate / 叙事连续推进闸门', '### 3.3 Narrative Continuation Gate / 叙事连续推进闸门\n\n“自然继续”仅指仍在玩家授权与时间边界内的推进；各类出口以 3.3.1 为准。不得将本节解释成“必须写到次日或必须制造新事件才能停”。')
    text = one(text, '### 2.2 Safe v4 Execution Pipeline', '### 2.2 Safe v4 Execution Pipeline\n\n本流程的 Release/Continuity Preflight 同时调用 3.3.1 Turn Exit Contract；它是同一流程的出口检查，不是第二套提交流程。')
    return text


# Pure reference decision table, not an installed game runtime.
def resolve_exit(**s: bool) -> str:
    if s.get('user_pause'):
        return 'user_pause'
    if s.get('meta_hold'):
        return 'meta_hold'
    if s.get('requested_endpoint'):
        return 'requested_endpoint'
    if s.get('blocker'):
        return 'blocker'
    if s.get('technical_limit'):
        return 'technical_checkpoint'
    if s.get('unresolved_choice'):
        return 'continue_auto' if s.get('auto_authorized') else 'decision_required'
    if s.get('time_transition_needed') and not s.get('time_authorized'):
        return 'scope_boundary'
    if s.get('authorized_progress') and not s.get('no_progress_loop'):
        return 'continue'
    if s.get('story_complete'):
        return 'story_complete'
    return 'scope_boundary'


CASES = [
    ('当前授权可继续，不因没有菜单空停', {'authorized_progress': True}, 'continue'),
    ('未来午饭不能授权今晚自动跳天', {'time_transition_needed': True, 'authorized_progress': True}, 'scope_boundary'),
    ('用户授权快进可继续', {'time_transition_needed': True, 'time_authorized': True, 'authorized_progress': True}, 'continue'),
    ('自然跨午夜的已选行动', {'time_transition_needed': True, 'time_authorized': True, 'authorized_progress': True}, 'continue'),
    ('空闲时间真实D1选择', {'unresolved_choice': True}, 'decision_required'),
    ('不强行生成事件，归还场景方向', {}, 'scope_boundary'),
    ('NPC离场不冻结主角', {'authorized_progress': True}, 'continue'),
    ('用户暂停高于可继续', {'user_pause': True, 'authorized_progress': True}, 'user_pause'),
    ('混合提问hold已选行动', {'meta_hold': True, 'authorized_progress': True}, 'meta_hold'),
    ('只写到指定处允许无菜单收束', {'requested_endpoint': True, 'authorized_progress': True}, 'requested_endpoint'),
    ('真实技术边界可停', {'technical_limit': True, 'authorized_progress': True}, 'technical_checkpoint'),
    ('关键证据缺失可停', {'blocker': True, 'authorized_progress': True}, 'blocker'),
    ('无新信息循环不能硬续写', {'authorized_progress': True, 'no_progress_loop': True}, 'scope_boundary'),
    ('完整故事结束可无选项', {'story_complete': True}, 'story_complete'),
    ('子任务结束不等于故事结束', {}, 'scope_boundary'),
    ('已授权队列继续不二次确认', {'authorized_progress': True}, 'continue'),
    ('出现新的未授权决定须停', {'authorized_progress': True, 'unresolved_choice': True}, 'decision_required'),
    ('授权自动小说不机械问真人', {'unresolved_choice': True, 'auto_authorized': True}, 'continue_auto'),
    ('自动小说手动门保留', {'unresolved_choice': True}, 'decision_required'),
    ('暂停不能被自动小说吞掉', {'user_pause': True, 'unresolved_choice': True, 'auto_authorized': True}, 'user_pause'),
    ('查询不因技术问题推进故事', {'meta_hold': True, 'technical_limit': True}, 'meta_hold'),
    ('同日已授权转场继续', {'authorized_progress': True}, 'continue'),
    ('同日但新目标未授权，不能代选', {'unresolved_choice': True}, 'decision_required'),
    ('日界授权边界高于继续到菜单', {'authorized_progress': True, 'time_transition_needed': True}, 'scope_boundary'),
    ('真实阻塞不伪装下个剧情选项', {'blocker': True, 'unresolved_choice': True}, 'blocker'),
    ('终点已到不无限追求下一场', {'requested_endpoint': True, 'unresolved_choice': True}, 'requested_endpoint'),
]


def footer(values: tuple[str, str, str, str]) -> str:
    return '\n'.join(f'{label}：{value}' for label, value in zip(LABELS, values))


def footer_valid(text: str, exit_mode: str) -> bool:
    lines = text.splitlines()
    if len(lines) != 4 or any(not x.startswith(k + '：') for x, k in zip(lines, LABELS)):
        return False
    if any('｜' in line for line in lines):
        return False
    if exit_mode in {'decision_required', 'scope_boundary'} and lines[3] == '需要你确认：无':
        return False
    if exit_mode in {'blocker', 'technical_checkpoint'} and lines[2] == '存在问题：无':
        return False
    return exit_mode != 'continue'


def run_logic() -> list[dict]:
    results = []
    for i, (name, context, expected) in enumerate(CASES, 1):
        before = dict(context)
        actual = resolve_exit(**context)
        results.append({'id': f'EXIT-{i:02}', 'name': name, 'expected': expected, 'actual': actual, 'pass': actual == expected and context == before})
    choices = footer(('邀约已确认', '无', '无', '选择今晚安排或自由行动'))
    paused = footer(('已暂停', 'A尚未执行', '无', '无'))
    blocked = footer(('已核对', '缺少关键原文', '关键证据不足', '补充或选择不依赖该证据的行动'))
    tests = [
        ('四字段分别换行', footer_valid(choices, 'scope_boundary'), True),
        ('真实待选不能写无需确认', footer_valid(footer(('已执行', '无', '无', '无')), 'decision_required'), False),
        ('拒绝旧横排收尾', footer_valid(choices.replace('\n', '｜'), 'scope_boundary'), False),
        ('用户暂停允许无需确认', footer_valid(paused, 'user_pause'), True),
        ('阻塞必须反映问题', footer_valid(blocked, 'blocker'), True),
        ('拒绝空白问题遮蔽阻塞', footer_valid(footer(('已核对', '待恢复', '无', '恢复')), 'blocker'), False),
        ('continue不是交付终点', footer_valid(paused, 'continue'), False),
        ('明确完结允许无选项', footer_valid(footer(('故事结束', '无', '无', '无')), 'story_complete'), True),
    ]
    for i, (name, actual, expected) in enumerate(tests, 1):
        results.append({'id': f'FOOTER-{i:02}', 'name': name, 'expected': expected, 'actual': actual, 'pass': actual == expected})
    return results


def check_document(text: str) -> list[dict]:
    exact = [
        ('release_version', f'version: {VERSION}' in text),
        ('unchanged_schema', 'Demo 使用独立 `schema_version: 4.0-demo.4`' in text),
        ('unique_exit_section', text.count('#### 3.3.1 Turn Exit Contract') == 1),
        ('latest_footer_policy', '**Closing Status By Category**' in text),
        ('no_old_compact_rule', '**Closing Status Compact**' not in text),
        ('no_old_single_line_phrase', '四字段压缩单行' not in text),
        ('no_old_pipe_template', '已完成：…｜未完成：…｜存在问题：…｜需要你确认：…' not in text),
        ('no_fake_unused_tasks', '普通开放可能性都记成欠办任务' in text),
        ('future_plan_not_authorization', '未来约定不等于跨天授权' in text),
        ('no_proactive_skip_preserved', '**No Proactive Day Skip**' in text),
        ('meta_hold_preserved', '**Mixed Action + Meta Query**' in text),
        ('preflight_wired', '**Decision Gate / Turn Exit**' in text),
        ('output_wired', '先执行 3.3.1 Turn Exit Contract' in text),
        ('pipeline_wired', '同一流程的出口检查' in text),
        ('footer_legacy_test_updated', '每类独立一行' in text),
        ('no_required_menu_every_turn', '本节不是“每回合必有选项”' in text),
        ('no_automatic_next_day', '也不是没菜单就停止' in text),
        ('anti_duplicate_action', '已执行的 A 不因再次解释 Bug' in text),
    ]
    return [{'id': 'DOC-' + name, 'pass': passed} for name, passed in exact]


def apply(root: Path) -> dict:
    skill = root / DEMO / 'SKILL.md'
    old = skill.read_bytes()
    if blob(old) != BASE_BLOB:
        raise ValueError('Base changed; refusing patch. Re-read/reconcile rather than overwrite.')
    protected_paths = [root/'skills/complex-tavern/SKILL.md', root/'skills/no-rush/SKILL.md']
    protected = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected_paths}
    updated = patch_skill(old.decode('utf-8'))
    logic = run_logic()
    docs = check_document(updated)
    if not all(r['pass'] for r in logic + docs):
        raise ValueError(json.dumps({'logic': logic, 'document': docs}, ensure_ascii=False))
    changes = {skill: updated}
    readme = root/DEMO/'README.md'
    rm = readme.read_text(encoding='utf-8').replace(OLD_VERSION, VERSION)
    rm += '\n## demo.5 — 回合出口与分类收尾\n\n' + '- 已授权范围内继续；真实D1/授权边界归还控制权，不再无菜单空停。\n' + '- 未来邀约不自动授权跨天；用户暂停、技术边界和完整完结仍可无选项停止。\n' + '- 收尾四类分别换行，未完成只列真实任务/待执行动作，内容与停点一致。\n' + '- 保留 schema 4.0-demo.4；稳定版与 No-Rush 全局文件不改。\n' + '- 新检查仅为纯决策表逻辑模型和定向文本静态检查，不是 LLM 玩法或 Runtime 实测。\n'
    changes[readme] = rm
    index = root/'skills/README.md'
    idx = index.read_text(encoding='utf-8')
    match = re.search(r'^## Complex Tavern Engine v4 Demo\n.*?(?=^## |\Z)', idx, re.M|re.S)
    if not match:
        raise ValueError('Missing unique v4 index section')
    section = match.group(0).replace(OLD_VERSION, VERSION)
    section = re.sub(r'^- Regression:.*$', '- Validation: demo.5 has 34 pure decision-table/formatter cases and 18 targeted text checks; no LLM gameplay or external Runtime test claimed. Earlier 80-case reports are historical and were not rerun as behavior tests.', section, flags=re.M)
    changes[index] = idx[:match.start()] + section + idx[match.end():]
    report = {'version': VERSION, 'base_blob': BASE_BLOB, 'new_blob': blob(updated.encode()), 'schema_version': '4.0-demo.4', 'logical_model_cases': logic, 'document_checks': docs, 'protected_sha256': protected, 'coverage': 'Pure reference decision table and targeted text lint only. No story generation, runtime behavior, persistence or historical 80-case behavioral suite executed.'}
    changes[root/DEMO/'evals/RESULTS-demo.5.json'] = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    audit = f'''# demo.5 定向逻辑审计

## 范围与结果
基线 `{BASE_BLOB}`；更新版本 `{VERSION}`，schema 保持 `4.0-demo.4`。
纯决策表/收尾格式逻辑模型：{len(logic)} 个用例通过。
定向文档静态检查：{len(docs)} 项通过。
这不是模型实际玩过相应回合，也不是分支/向量库/事务系统实测；不宣称旧80项行为回归已重跑或无Bug。

## 根因和同类风险
- 缺少结构化合法出口：无D2/D3被误读为可以结束。
- 真实D1时间用途/场景方向没有归还控制权。
- 子任务完成、NPC离场被误当整个交互结束。
- 过度修复可能擅自跳天：未来午饭承诺不是处理整晚与次日上午的授权。
- 为寻找选项可能无限续写、强造突发事件或重开已完成技术任务。
- 查询/审计可能误执行hold行动；已提交选择可能重试时重复结算。
- 四类收尾横排与最新要求冲突；菜单仍待选却填无需确认；开放可能性被虚列为欠办任务。

## 修复裁决
用户暂停/查询/指定终点与真实阻塞优先；有真实决定归还控制权；授权内仍有内容则继续；超出授权或需要新方向则scope_boundary，不擅自跨天。
只有完整交付目标达成才story_complete。菜单数量不是每回合配额；无合法具体项可明确询问自由行动，不留空停。
四类收尾分别换行，完成/待办/问题/确认内容与真实出口一致。

## 发布与回滚
保护 v3 stable 与 No-Rush 全局文件；不改任何故事/日程/关系/原文存档。更新后原剧情仍停在已确认明日午餐的当晚。
补丁要求完全匹配原始Git blob，基线变化会拒绝。检查失败不发布；不强推、不覆盖并发修改。回滚可撤销该补丁提交，不涉及玩家存档。
'''
    changes[root/DEMO/'evals/AUDIT-demo.5.md'] = audit
    for path, content in changes.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
    if {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected_paths} != protected:
        raise ValueError('Protected file changed')
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--logic-only', action='store_true')
    args = parser.parse_args()
    if args.apply:
        report = apply(args.root.resolve())
    else:
        logic = run_logic()
        text_path = args.root/DEMO/'SKILL.md'
        docs = [] if args.logic_only else check_document(text_path.read_text(encoding='utf-8'))
        report = {'logical_model_cases': logic, 'document_checks': docs}
        if not all(r['pass'] for r in logic + docs):
            raise SystemExit(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
