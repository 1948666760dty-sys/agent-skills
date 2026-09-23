#!/usr/bin/env python3
"""demo.6 exact-base repair + pure final-output validation reference.
Default is read-only; --apply patches only the approved demo files.
This is NOT a hosted LLM runtime or a claim that ChatGPT invokes Python per turn.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path

VERSION = '4.0.0-demo.6'
OLD_VERSION = '4.0.0-demo.5'
BASE_BLOB = 'b877b9510d37985b5399d21b66530416da4062b6'
DEMO = Path('skills/complex-tavern-v4-demo')
LABELS = ('已完成', '未完成', '存在问题', '需要你确认')
HANDOFF = {'decision_required', 'scope_boundary'}
STOP_MODES = {'user_pause', 'meta_hold', 'requested_endpoint', 'blocker', 'technical_checkpoint', 'story_complete'}

# Actual final-tail excerpt supplied by the user conversation, not generated gameplay.
BAD_BODY = '“你困了吗？”她问。\n\n你现在确实已经把项目做完、澡也洗了，时间也不早，但要不要继续聊、准备休息，还是再做点自己的事，还是由你决定。'
BAD_FOOTER = '已完成：你明确表示明天中午本来就是和许知遥一起吃，并主动用了“许老师”这个旧称呼；她自然接了几句，没有重新陷入旧梗循环。\n未完成：今晚这通电话还没有决定什么时候结束。\n存在问题：无。\n需要你确认：你想继续聊、准备休息，还是做点别的都可以直接说。'
BAD_TAIL = BAD_BODY + '\n\n' + BAD_FOOTER
MENU = 'A. 继续语音聊一会儿，暂时不挂断。\nB. 告诉她自己有点困，互道晚安后结束通话；不跳到次日。\nC. 先结束电话，自己再做点别的。\nD. 自由行动或直接说你想怎样回答。'

GUARD = '''#### 3.3.2 Final Visible Handoff Gate / 最终正文与菜单可见性检查（demo.6）

**修复对象：** demo.5 的出口判定不等于最终交付完整。“需要你确认”填了自由回复提示，或旁白写“还是由你决定”，都不能证明玩家收到对应菜单。必须同时检查最终可见正文、实际选项和四行收尾，而非只检查状态字段或渲染前计划。

**默认普通互动的交付合同：**
- 当前 `interactive` 的出口为 `decision_required / scope_boundary` 时，最终回复必须有 **承接玩家行动的正文 → 对应当前未决问题的字母选项 → 四类换行收尾**。菜单在正文后、收尾前实际出现；通常3–6个真实差异行动加自由行动，真实选择少则少给，不造同义项。
- `自由行动` 是菜单之外的额外能力，**不是默认代替菜单的豁免**。仅用户明确选择“本局/本轮不要菜单，只让我自由回复”时可按已确认偏好省略字母菜单；不能由模型以“很自然/只是D1/能自由说”为由自行启用。
- “你可以继续聊、休息或做别的”“接下来由你决定”“你想怎么做都可以说”等正文/收尾提示，不算已渲染菜单。A/B/C若只存在于代码块、引用的示例、历史日志或注释里，也不算本轮行动入口。
- 默认手动决策至少有一个真实具体行动及自由行动入口。若确有更少行动，不为凑3个编剧情；如果关键状态缺失导致无法提出任何诚实具体行动，按实际证据阻塞处理，而不是假装已交付完整选择。
- 不能只给菜单或只给“已完成”。本轮执行了行动，就在正文呈现可观察的回应/后果；已写过的正文可原地保留，只补当前出口，不重跑电话、邀约、洗澡或旧选择。
- 菜单标签唯一且连续，收尾引用的字母必须确实存在。“需要你确认：无/无。/无需确认”等与待选出口冲突；仅写“自由回复”不豁免。输出后又删改正文/选项，必须重新检查，不能沿用旧PASS。

**不误伤其他出口：** 用户明确暂停、系统查询、指定写到某处、真实阻塞/技术边界、完整故事结束，可以没有菜单；其原因必须来自用户要求或可验证状态，不得由模型为了逃避菜单自称“已结束”。同一回合的系统修复/审计不推进故事、不消耗剧情TURN、不执行hold动作。
`autonomous_novel` 的已授权自动决策继续遵循Content Edition，不强制每次找真人选择；遇到仍归真人的manual gate，按同样的可见行动入口检查。

**修补与放行：** 最终文本装配（含注释、选项、四类收尾）完成后执行 `Final Visible Handoff Check`。若应当有菜单却没有，在原时间、原场景、原角色状态追加对应菜单，重新校验；不制造事故、不为找菜单自动跳天，不改已确认关系/安排。需要更完整正文时，只补未呈现的授权内后果。校验失败的稿件不提交为完成版，也不提前写“问题：无”。该检查与现有Preflight/Persistence同一流程，发生在最终Raw Story Log/状态提交之前，不另建第二套状态写入者。

可选派生记录 `delivery_check = {render_sha256, exit_mode, menu_labels, footer_labels, status, issues}` 用于绑定**被检查的那份最终文本**。它不是世界Canon，也不证明模型已自动执行了外部代码。宿主接入参考校验器才有程序级拦截；当前聊天依然需要模型实际遵循检查，不承诺零Bug。

`evals/repair_demo6.py` 是离线纯逻辑参考：它能检查可见结构、例外、标签与四行收尾，并复现demo.5只检收尾的误放行；不能自动证明选项语义独立、剧情精彩、人物没有漂移或模型每次都调用了它。版本升为demo.6，存档schema仍为`4.0-demo.4`；故事历史和待执行动作不改。

'''


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def once(s: str, old: str, new: str) -> str:
    if s.count(old) != 1:
        raise ValueError('Non-unique/missing anchor: ' + old[:100])
    return s.replace(old, new, 1)


def normalized_lines(text: str) -> list[str]:
    """Menu counting ignores examples in fences, blockquotes and HTML comments."""
    text = re.sub(r'<!--.*?-->', '', text, flags=re.S)
    result: list[str] = []
    fence: str | None = None
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith(('```', '~~~')):
            marker = line[:3]
            if fence is None:
                fence = marker
            elif fence == marker:
                fence = None
            continue
        if fence is not None or line.startswith('>') or line.startswith(':::'):
            continue
        line = line.replace('**', '').strip()
        if line:
            result.append(line)
    return result


def no_confirmation(value: str) -> bool:
    value = value.strip().rstrip('。.!！;； ')
    return value in {'无', '无需确认', '不需要确认', '暂无', '不用确认'}


def validate_output(text: str, *, exit_mode: str = 'decision_required',
                    narrative_required: bool = True, free_text_authorized: bool = False,
                    menu_policy: str = 'labeled', reason_verified: bool = False,
                    pending_user_decision: bool = True) -> dict:
    """Context flags must come from parsed user/state evidence, not model excuses.
    Targets normal interactive chat or an autonomous manual gate, not novel exports.
    Does not mutate any story state.
    """
    errors: list[str] = []
    lines = normalized_lines(text)
    footer_re = re.compile(r'^(已完成|未完成|存在问题|需要你确认)[：:](.*)$')
    footer_matches = [(i, footer_re.match(line)) for i, line in enumerate(lines) if footer_re.match(line)]
    values: dict[str, str] = {}
    if len(lines) < 4 or len(footer_matches) != 4:
        errors.append('FOUR_CATEGORY_LINES_REQUIRED')
        body_lines = lines[:footer_matches[0][0]] if footer_matches else lines
    else:
        tail = [footer_re.match(x) for x in lines[-4:]]
        if not all(tail) or tuple(m.group(1) for m in tail if m) != LABELS:
            errors.append('FOOTER_ORDER_OR_PLACEMENT')
            body_lines = lines[:footer_matches[0][0]]
        else:
            values = {m.group(1): m.group(2).strip() for m in tail if m}
            body_lines = lines[:-4]
            if any(not v for v in values.values()) or any('｜' in x for x in lines[-4:]):
                errors.append('FOOTER_EMPTY_OR_INLINE')
    choice_re = re.compile(r'^([A-G])[.．、:：)]\s*(\S.*)$')
    # Only the final contiguous menu, immediately before the footer, counts.
    split = len(body_lines)
    while split > 0 and choice_re.match(body_lines[split - 1]):
        split -= 1
    choices = [choice_re.match(x) for x in body_lines[split:]]
    labels = [m.group(1) for m in choices if m]
    texts = [m.group(2) for m in choices if m]
    prose = [x for x in body_lines[:split] if not x.startswith(('#', '不着急', '复杂酒馆')) and not choice_re.match(x)]
    if narrative_required and not prose:
        errors.append('NARRATIVE_MISSING')
    if exit_mode in {'continue', 'continue_auto'}:
        errors.append('CONTINUE_IS_NOT_A_FINAL_EXIT')
    elif exit_mode in STOP_MODES:
        if not reason_verified:
            errors.append('UNVERIFIED_STOP_REASON')
        if exit_mode == 'story_complete' and pending_user_decision:
            errors.append('PENDING_DECISION_NOT_COMPLETE')
        if exit_mode in {'blocker', 'technical_checkpoint'} and no_confirmation(values.get('存在问题', '')):
            errors.append('BLOCKER_HIDDEN_BY_FOOTER')
    elif exit_mode in HANDOFF:
        if menu_policy == 'free_text':
            if not free_text_authorized:
                errors.append('FREE_TEXT_MODE_NOT_AUTHORIZED')
        elif menu_policy != 'labeled':
            errors.append('UNKNOWN_MENU_POLICY')
        else:
            if not choices:
                errors.append('HANDOFF_MENU_MISSING')
            else:
                if labels != list('ABCDEFG'[:len(labels)]):
                    errors.append('DUPLICATE_OR_NONCONTIGUOUS_LABELS')
                free = [i for i, x in enumerate(texts) if '自由行动' in x or '自由回复' in x]
                if len(free) != 1 or free[0] != len(texts) - 1:
                    errors.append('FINAL_FREE_ACTION_REQUIRED')
                concrete = [x for i, x in enumerate(texts) if i not in free]
                if not concrete or len(concrete) > 6:
                    errors.append('CONCRETE_ACTION_COUNT')
                normalized = [re.sub(r'[\s。.!！?？]', '', x) for x in concrete]
                if len(set(normalized)) != len(normalized):
                    errors.append('DUPLICATE_ACTION_TEXT')
                if not prose:
                    errors.append('HANDOFF_NEEDS_NARRATIVE')
                for start, end in re.findall(r'([A-G])\s*[-–—~至]\s*([A-G])', values.get('需要你确认', '')):
                    if start not in labels or end not in labels or start > end:
                        errors.append('FOOTER_REFERENCES_NONEXISTENT_LABELS')
        if not values.get('需要你确认') or no_confirmation(values['需要你确认']):
            errors.append('PENDING_DECISION_WITHOUT_CONFIRMATION')
    else:
        errors.append('UNKNOWN_EXIT_MODE')
    return {'pass': not errors, 'errors': sorted(set(errors)), 'labels': labels,
            'render_sha256': hashlib.sha256(text.encode('utf-8')).hexdigest()}


def same_validated_output(check: dict, text: str) -> bool:
    return bool(check.get('pass')) and check.get('render_sha256') == hashlib.sha256(text.encode('utf-8')).hexdigest()


def footer(confirm: str = 'A–D，或直接自由回复。', issue: str = '无。') -> str:
    return f'已完成：通话仍在继续，明天午餐约定不变。\n未完成：无额外待办。\n存在问题：{issue}\n需要你确认：{confirm}'


def run_checks() -> list[dict]:
    out: list[dict] = []
    def case(name: str, actual: bool, expected: bool) -> None:
        out.append({'id': f'R{len(out)+1:02}', 'name': name, 'expected_accept': expected,
                    'actual_accept': actual, 'pass': actual == expected})
    good = BAD_BODY + '\n\n' + MENU + '\n\n' + footer()
    case('用户实际尾部：收尾有自由回复但无菜单，必须拒绝', validate_output(BAD_TAIL)['pass'], False)
    case('同一时点只补真实菜单和对齐收尾，可接受', validate_output(good)['pass'], True)
    case('scope_boundary也需要实际菜单', validate_output(BAD_TAIL, exit_mode='scope_boundary')['pass'], False)
    case('只填A-D收尾但正文没菜单', validate_output(BAD_BODY+'\n'+footer())['pass'], False)
    case('菜单只藏在代码块，不算可见行动入口', validate_output(BAD_BODY+'\n```text\n'+MENU+'\n```\n'+footer())['pass'], False)
    case('引用历史菜单不算本轮菜单', validate_output(BAD_BODY+'\n'+ '\n'.join('> '+x for x in MENU.splitlines())+'\n'+footer())['pass'], False)
    case('HTML注释菜单不算行动入口', validate_output(BAD_BODY+'\n<!--\n'+MENU+'\n-->\n'+footer())['pass'], False)
    case('只有菜单和收尾，没有承接正文', validate_output(MENU+'\n'+footer())['pass'], False)
    case('只有四行状态，没有正文和菜单', validate_output(footer())['pass'], False)
    case('旧横排四类收尾拒绝', validate_output(good.replace('\n未完成', '｜未完成').replace('\n存在问题', '｜存在问题').replace('\n需要你确认', '｜需要你确认'))['pass'], False)
    case('待选却写无句号也拒绝', validate_output(BAD_BODY+'\n'+MENU+'\n'+footer('无。'))['pass'], False)
    case('待选却写无需确认拒绝', validate_output(BAD_BODY+'\n'+MENU+'\n'+footer('无需确认'))['pass'], False)
    case('缺自由行动入口', validate_output(good.replace('D. 自由行动或直接说你想怎样回答。', ''))['pass'], False)
    case('只剩自由行动没有具体选择', validate_output(BAD_BODY+'\nA. 自由行动。\n'+footer('A。'))['pass'], False)
    case('只有两个真实行动也允许，不凑数', validate_output(BAD_BODY+'\nA. 继续通话。\nB. 结束通话。\nC. 自由行动。\n'+footer('A–C。'))['pass'], True)
    case('一个诚实具体行动加自由行动也不造假', validate_output(BAD_BODY+'\nA. 暂时等对方回答。\nB. 自由行动。\n'+footer('A–B。'))['pass'], True)
    case('重复标签拒绝', validate_output(good.replace('B. 告诉她', 'A. 告诉她'))['pass'], False)
    case('标签跳号拒绝', validate_output(good.replace('D. 自由行动', 'G. 自由行动'))['pass'], False)
    case('同义原句重复不算新选择', validate_output(BAD_BODY+'\nA. 继续通话。\nB. 继续通话。\nC. 自由行动。\n'+footer('A–C。'))['pass'], False)
    case('收尾引用不存在的F拒绝', validate_output(good.replace('A–D，或直接自由回复。', 'A–F，或自由行动。'))['pass'], False)
    case('菜单埋在正文前面不算当前出口', validate_output(MENU+'\n'+BAD_BODY+'\n'+footer())['pass'], False)
    case('正文后仅自由问题仍不豁免菜单', validate_output(BAD_BODY+'\n你想怎么做？\n'+footer('自由回复。'))['pass'], False)
    case('用户明确自由文本模式才可以无菜单', validate_output(BAD_TAIL, menu_policy='free_text', free_text_authorized=True)['pass'], True)
    case('模型不能自称自由文本模式', validate_output(BAD_TAIL, menu_policy='free_text')['pass'], False)
    for mode in ('user_pause', 'meta_hold', 'requested_endpoint'):
        text='已按你的要求停在当前通话，不推进时间。\n'+footer('无。')
        case(mode+'真实请求可无菜单', validate_output(text, exit_mode=mode, reason_verified=True, narrative_required=False)['pass'], True)
    case('不能伪称暂停来漏菜单', validate_output(BAD_TAIL, exit_mode='user_pause')['pass'], False)
    for mode in ('blocker', 'technical_checkpoint'):
        text='保留当前通话和待选动作。\n'+footer('无。', '实际条件阻塞，尚未继续。')
        case(mode+'真实限制可无菜单', validate_output(text, exit_mode=mode, reason_verified=True)['pass'], True)
    case('阻塞却问题填无拒绝', validate_output(BAD_BODY+'\n'+footer('无。'), exit_mode='blocker', reason_verified=True)['pass'], False)
    case('整局真实结束可无菜单', validate_output('故事在这里结束。\n'+footer('无。'), exit_mode='story_complete', reason_verified=True, pending_user_decision=False)['pass'], True)
    case('未决问题不能伪称整局完成', validate_output(BAD_TAIL, exit_mode='story_complete', reason_verified=True)['pass'], False)
    case('continue不能直接结束输出', validate_output(good, exit_mode='continue')['pass'], False)
    case('粗体字母菜单可识别', validate_output(good.replace('A. 继续', '**A.** 继续').replace('B. 告诉', '**B.** 告诉').replace('C. 先', '**C.** 先').replace('D. 自由', '**D.** 自由'))['pass'], True)
    case('中文句点菜单可识别', validate_output(re.sub(r'(?m)^([A-D])\.', r'\1．', good))['pass'], True)
    case('额外重复收尾拒绝', validate_output(good+'\n'+footer())['pass'], False)
    accepted = validate_output(good)
    case('校验绑定未改动的最终文本', same_validated_output(accepted, good), True)
    case('校验后删菜单不能沿用PASS', same_validated_output(accepted, BAD_TAIL), False)
    case('校验后改字也需要重新校验', same_validated_output(accepted, good+' '), False)
    return out


def patch_skill(s: str) -> str:
    s = s.replace(OLD_VERSION, VERSION)
    s = once(s, '（demo.5）', '（demo.6）')
    s = once(s, 'demo.5 保持 `schema_version: 4.0-demo.4`', 'demo.6 保持 `schema_version: 4.0-demo.4`')
    old = '若确实无法诚实列出具体行动，用一个明确的自由行动问题归还控制权，不留“你还有自己的时间”然后无人可操作的空结尾。'
    new = '默认不能以一个自由行动问题替代菜单；具体交付必须通过3.3.2的最终可见检查。仅用户明确要求无菜单自由回复模式时可省略菜单，不能因为D1很普通或收尾已有“可以直接说”而豁免。'
    s = once(s, old, new)
    s = once(s, '### 3.4 Autonomous Player Policy / 自动主角决策策略', GUARD+'### 3.4 Autonomous Player Policy / 自动主角决策策略')
    s = once(s, '19. **Output / Continue**：先执行 3.3.1 Turn Exit Contract：', '19. **Output / Continue**：先执行3.3.1出口判定，再按3.3.2检查最终装配文本中正文、菜单与四行收尾的实际存在性，失败先修补原出口且不提交草稿。出口判定：')
    s = once(s, '### 6.1 输出与选项规则', '### 6.1 输出与选项规则\n\n**Final Visible Handoff Check**：默认interactive在decision_required/scope_boundary交付时，必须实际呈现对应正文与字母菜单；自由行动附加而不代替菜单，收尾也不是菜单。最终装配文本通过3.3.2后才可提交；本轮查询、用户暂停和真实阻塞的例外保持。')
    anchor = '4. **Opening / Version / Novel Contract Gate**'
    extra = '3A. **Final Visible Handoff**：是否检验了最终玩家可见文本而非只看出口元数据/四行收尾；应显示的菜单是否真实出现在正文后且不藏于示例/代码；自由行动是否被滥用成省略菜单借口；末尾再次编辑是否使旧校验失效；不得为了修出口重跑已完成动作、越过跨天授权或制造新剧情。\n'
    s = once(s, anchor, extra+anchor)
    s = once(s, '本流程的 Release/Continuity Preflight 同时调用 3.3.1 Turn Exit Contract；', '本流程的 Release/Continuity Preflight 同时调用3.3.1出口判定和3.3.2最终可见正文/菜单检查；')
    s = once(s, '## 18. 持久化合同', '## 18. 持久化合同\n\n最终输出装配后执行3.3.2；缺少必须显示的正文/菜单/分类收尾时，先原地修补再走既有提交协议。检查与日志引用同一最终文本，不用渲染前的菜单计划代替。纯聊天宿主未接入代码时，不得声称参考Python校验器已自动执行。')
    s = re.sub(r'^description:.*$', 'description: 复杂酒馆4.0并行Demo。demo.6针对“有正文和自由回复收尾但仍漏字母选项”的重复缺陷，收紧无菜单豁免并加入最终可见正文/菜单/四行收尾检查、原时点最小修补和渲染摘要校验绑定。保留demo.5授权时间边界、四类换行、Single Authority、真实能力降级与既有叙事规则。参考校验代码不是已自动接入ChatGPT的Runtime。', s, count=1, flags=re.M)
    return s


def check_document(s: str) -> list[dict]:
    pairs = [
        ('version', f'version: {VERSION}' in s),
        ('schema_unchanged', 'Demo 使用独立 `schema_version: 4.0-demo.4`' in s),
        ('unique_final_gate', s.count('#### 3.3.2 Final Visible Handoff Gate') == 1),
        ('old_free_only_exception_removed', '用一个明确的自由行动问题归还控制权' not in s),
        ('explicit_free_mode_only', '仅用户明确选择' in s and '自由行动` 是菜单之外的额外能力' in s),
        ('actual_text_check', '不是默认代替菜单的豁免' in s and '实际存在性' in s),
        ('output_wired', '19. **Output / Continue**：先执行3.3.1' in s),
        ('preflight_wired', '3A. **Final Visible Handoff**' in s),
        ('persistence_wired', '最终输出装配后执行3.3.2' in s),
        ('four_lines_kept', '**Closing Status By Category**' in s),
        ('no_forced_day_skip', '未来约定不等于跨天授权' in s),
        ('meta_hold_kept', '**Mixed Action + Meta Query**' in s),
        ('no_fake_autoinstall_claim', '不能自动证明' in s and '宿主接入参考校验器才有程序级拦截' in s),
        ('no_replay', '已写过的正文可原地保留' in s),
    ]
    return [{'id': k, 'pass': v} for k, v in pairs]


def legacy_proof(root: Path) -> dict:
    path = root/DEMO/'evals/repair_demo5.py'
    spec = importlib.util.spec_from_file_location('legacy_demo5_check', path)
    if spec is None or spec.loader is None:
        raise ValueError('Cannot read legacy checker')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # main/apply are not called.
    old_accept = module.footer_valid(BAD_FOOTER, 'decision_required')
    new_check = validate_output(BAD_TAIL)
    return {'legacy_footer_checker_accepts_bad_tail_footer': old_accept,
            'new_final_output_check': new_check,
            'pass': old_accept is True and not new_check['pass'] and 'HANDOFF_MENU_MISSING' in new_check['errors']}


def all_checks(root: Path, candidate: str) -> dict:
    report = {'version': VERSION, 'schema': '4.0-demo.4',
              'output_logic_cases': run_checks(), 'document_checks': check_document(candidate),
              'legacy_false_acceptance_reproduction': legacy_proof(root),
              'scope': 'Offline reference checker on text fixtures plus targeted document checks. No gameplay generation, LLM integration, vector/branch/storage runtime or old 80-case behavioral test is claimed.'}
    if not all(x['pass'] for x in report['output_logic_cases']+report['document_checks']) or not report['legacy_false_acceptance_reproduction']['pass']:
        raise ValueError(json.dumps(report, ensure_ascii=False, indent=2))
    return report


def apply(root: Path) -> dict:
    skill = root/DEMO/'SKILL.md'
    b = skill.read_bytes()
    if git_blob(b) != BASE_BLOB:
        raise ValueError('Base changed: abort; reconcile before publishing.')
    protected = [root/'skills/complex-tavern/SKILL.md', root/'skills/no-rush/SKILL.md']
    hashes = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
    candidate = patch_skill(b.decode('utf-8'))
    report = all_checks(root, candidate)
    report.update({'base_blob': BASE_BLOB, 'new_blob': git_blob(candidate.encode()), 'protected_sha256': hashes})
    changes: dict[Path, str] = {skill: candidate}
    readme = root/DEMO/'README.md'
    changes[readme] = readme.read_text(encoding='utf-8').replace(OLD_VERSION, VERSION) + '\n## demo.6 — 最终可见菜单校验\n\n- 重现demo.5仅检查四行收尾会误放行漏菜单结尾的问题。\n- 默认interactive的decision/scope出口必须有正文、当前字母菜单、自由行动与四行收尾；仅用户显式无菜单模式例外。\n- 最终装配后检查文本，修出口不重跑动作、不跨天；校验后编辑文本需重检。\n- Python仅为离线参考校验器，未自动接入ChatGPT；详见evals/RESULTS-demo.6.json。\n- schema仍为4.0-demo.4；稳定版、全局No-Rush与故事存档不修改。\n'
    index = root/'skills/README.md'
    idx = index.read_text(encoding='utf-8')
    match = re.search(r'^## Complex Tavern Engine v4 Demo\n.*?(?=^## |\Z)', idx, re.M|re.S)
    if not match:
        raise ValueError('Missing demo index section')
    section = match.group(0).replace(OLD_VERSION, VERSION)
    statement = '- Validation: demo.6 reproduces the demo.5 footer-only false acceptance and checks complete visible-output fixtures plus targeted contract wiring. These are offline logical/reference checks, not live LLM gameplay or an automatically installed runtime guard.'
    section = re.sub(r'^- (?:Validation|Regression):.*$', statement, section, flags=re.M)
    changes[index] = idx[:match.start()]+section+idx[match.end():]
    changes[root/DEMO/'evals/RESULTS-demo.6.json'] = json.dumps(report, ensure_ascii=False, indent=2)+'\n'
    audit = f'''# demo.6 定向审计：漏菜单重复缺陷

## 已确认根因
1. demo.5明文保留“一个自由行动问题”可以替代菜单的兜底；末尾“由你决定”容易被当成交还控制权。
2. demo.5 `footer_valid`只检四行字段，根本没有正文/菜单输入。实际漏菜单尾部的收尾能通过旧检查；本次运行旧函数复现，而不是凭新增关键词宣布修好。
3. 旧版出口策略的逻辑用例不证明最终文本确实渲染了所需菜单。

## 修复
替换原兜底，不在默认互动中把自由行动当成省略菜单的授权。新增最终正文→当前菜单→四行收尾检查，在最终装配后、既有提交前执行。纯示例/代码里的菜单、仅收尾引用A-D、只有菜单无正文、重复/缺失标签、待选写“无。”均不算有效交付。用户暂停、查询、真实中断和明确无菜单模式保持。
失败在原通话原时点补菜单，明天午餐约定、玩家年级与项目完成状态不改，不重播旧行动。已接受文本的摘要绑定校验；后续编辑须重检。

## 本次执行范围
- 最终输出参考校验用例：{len(report['output_logic_cases'])}。
- 定向文档检查：{len(report['document_checks'])}。
- 旧收尾校验器误放行复现：1项。
均已执行并符合预期。没有运行LLM生成、长局试玩、外部Runtime/分支数据库/事务系统，也未重跑旧80项行为测试。

## 局限
Python代码只有宿主真实接入时才能程序级拦截。本聊天仍需实际遵循规则，不能保证永不漏选项。参考检查能判断可见结构，不自动证明选择语义独立或小说质量。

## 发布安全
仅更新Demo规则/说明/本轮测试材料及Demo索引。schema保持4.0-demo.4。精确基线Git blob不匹配立即终止；不强推；不修改stable、全局No-Rush或任何故事存档。
'''
    changes[root/DEMO/'evals/AUDIT-demo.6.md'] = audit
    for path, text in changes.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')
    assert hashes == {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
    return report


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path.cwd())
    p.add_argument('--apply', action='store_true')
    p.add_argument('--logic-only', action='store_true')
    args = p.parse_args()
    root = args.root.resolve()
    if args.apply:
        result = apply(root)
    elif args.logic_only:
        result = {'output_logic_cases': run_checks()}
        if not all(x['pass'] for x in result['output_logic_cases']):
            raise ValueError(json.dumps(result, ensure_ascii=False))
    else:
        result = all_checks(root, (root/DEMO/'SKILL.md').read_text(encoding='utf-8'))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
