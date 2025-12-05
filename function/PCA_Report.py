from __future__ import annotations
from typing import List, Dict
import numpy as np


RISK_PROFILES = {
    "안정형": "예금이나 적금 수준의 수익률을 기대하며, 투자원금에 손실이 발생하는 것을 원하지 않습니다. "
           "원금 손실의 우려가 없는 상품에 투자하는 데 바람직한 성향입니다.",
    "안정추구형": "투자원금의 손실 위험은 최소화하고, 이자·배당 등 안정적인 수익을 목표로 합니다. "
             "다만 수익을 위해 단기적인 손실을 수용할 수 있으며 일부를 변동성 높은 상품에도 투자할 수 있습니다.",
    "위험중립형": "투자에는 위험이 있다는 것을 인식하고 있으며, 예·적금보다 높은 수익을 기대한다면 일정 수준의 손실 위험을 감수할 수 있습니다.",
    "적극투자형": "원금 보전보다 높은 수준의 수익을 추구하는 편이며, 투자자금의 상당 부분을 주식, 주식형 펀드, 파생상품 등 위험자산에 투자할 의향이 있습니다.",
    "공격투자형": "시장평균수익률보다 크게 높은 수익을 목표로 하며, 큰 손실 위험도 적극 수용합니다. "
             "투자자금 대부분을 고위험 자산에 투자하는 성향입니다."
}

_RISK_LEVEL = {
    "안정형": 1,
    "안정추구형": 2,
    "위험중립형": 3,
    "적극투자형": 4,
    "공격투자형": 5,
}


def _factor_role_comment(factor_idx: int, factor_name: str, n_factors: int) -> str:
    base = f"{factor_name}는 PCA로 추출된 요인 중 {factor_idx}번째로 중요한 요인입니다. "

    if factor_idx == 1:
        base += "대부분의 종목이 함께 오르내리는, 시장 전체 방향과 비슷한 움직임을 담는 경우가 많습니다."
    elif factor_idx == 2:
        base += "성장주 vs 가치주, 혹은 공격적 스타일 vs 방어적 스타일처럼 스타일 차이를 반영하는 경우가 자주 있습니다."
    elif factor_idx == 3:
        base += "금융·필수소비재·헬스케어 같은 방어주, 혹은 특정 업종군에 조금 더 민감한 요인으로 해석되는 경우가 많습니다."
    else:
        base += "특정 섹터나 테마(예: 반도체, 전기차 등)에 더 특화된 움직임을 담는 경우가 많습니다."

    return base


def _factor_short_name(factor_idx: int) -> str:
    if factor_idx == 1:
        return "시장 전체 방향 요인"
    elif factor_idx == 2:
        return "성장/스타일 요인"
    elif factor_idx == 3:
        return "섹터/방어형 성격의 요인"
    else:
        return "특정 테마·업종 성격의 요인"


def _diff_comment(actual: float, target: float) -> str:
    diff = actual - target
    gap = abs(diff)

    if gap < 0.03:
        return "목표와 거의 비슷한 수준입니다."
    elif gap < 0.08:
        if diff > 0:
            return "목표보다 약간 더 많이 담고 있습니다."
        else:
            return "목표보다 약간 덜 담고 있습니다."
    elif gap < 0.15:
        if diff > 0:
            return "목표보다 다소 많이 들어가 있는 편입니다."
        else:
            return "목표보다 다소 부족한 편입니다."
    else:
        if diff > 0:
            return "목표보다 상당히 많이 들어가 있어 쏠림이 크게 나타납니다."
        else:
            return "목표보다 상당히 부족한 편이라 성향 대비 노출이 약한 편입니다."


def _momentum_comment(v: float) -> str:
    if np.isnan(v):
        return "데이터가 부족해 최근 성과를 평가하기 어렵습니다."
    if v > 0.50:
        return "최근 6개월 동안 매우 강한 상승 흐름을 보였습니다."
    elif v > 0.20:
        return "최근 6개월 동안 비교적 좋은 상승 흐름을 보였습니다."
    elif v > 0.05:
        return "최근 6개월 동안 완만한 상승을 보였습니다."
    elif v > -0.05:
        return "최근 6개월 동안 큰 방향성 없이 보합권에 머물렀습니다."
    elif v > -0.20:
        return "최근 6개월 동안 다소 부진한 흐름을 보였습니다."
    else:
        return "최근 6개월 동안 상당히 부진한 흐름을 보였습니다."


def _join_code_list(codes: List[str], max_len: int = 5) -> str:
    if not codes:
        return ""
    if len(codes) == 1:
        return codes[0]
    if len(codes) <= max_len:
        return ", ".join(codes[:-1]) + " 그리고 " + codes[-1]
    else:
        head = ", ".join(codes[:max_len])
        return f"{head} 등"


def _risk_profile_brief(name: str) -> str:
    level = _RISK_LEVEL.get(name, 3)
    if level <= 2:
        return "전반적으로 원금 손실을 크게 원치 않는, 비교적 안정 성향에 가깝습니다."
    elif level == 3:
        return "전반적으로 수익과 위험을 균형 있게 바라보는 성향입니다."
    else:
        return "전반적으로 수익을 위해 변동성을 감수할 수 있는 공격적인 성향입니다."


def generate_portfolio_report(
        analysis: "AnalysisResult",
        risk_profile_name: str,
        risk_profiles: Dict[str, str] | None = None
) -> str:
    if risk_profiles is None:
        risk_profiles = RISK_PROFILES

    exposures = analysis.exposures
    norm_exp = analysis.norm_exposures
    target = analysis.target_exposures
    factor_momentum = analysis.factor_momentum

    factors = list(norm_exp.index)
    n_factors = len(factors)
    diff = norm_exp - target

    over = analysis.over_factors or []
    under = analysis.under_factors or []

    dominant_factor = norm_exp.idxmax()
    dom_idx = factors.index(dominant_factor) + 1
    dom_diff = diff[dominant_factor]
    dom_role = _factor_short_name(dom_idx)

    lines: List[str] = []

    lines.append("----------------------------------------\n")

    lines.append("[1] 나의 투자 성향 한 번 더 정리하기\n")
    lines.append(f"· 투자 성향: {risk_profile_name}")
    profile_desc = risk_profiles.get(risk_profile_name, "")
    if profile_desc:
        lines.append(f"· 성향 설명: {profile_desc}")
    lines.append(f"· 한 줄 요약: {_risk_profile_brief(risk_profile_name)}\n")

    lines.append("[2] 지금 포트폴리오의 첫 인상 요약\n")

    if not over and not under and abs(dom_diff) < 0.05:
        lines.append(
            "전체적으로 투자 성향과 크게 어긋나지 않는, 비교적 균형 잡힌 구조로 보입니다.\n"
            f"다만 그중에서도 {dominant_factor}({dom_role}) 요인의 비중이 가장 크기 때문에, "
            "시장 환경이 이 요인에 유리한지 여부에 따라 계좌 등락폭이 함께 움직일 가능성이 큽니다.\n"
        )
    else:
        if dom_diff > 0:
            lines.append(
                f"당신은 {risk_profile_name} 성향이지만, 실제 포트폴리오는 "
                f"{dominant_factor}({dom_role}) 쪽에 비중이 가장 많이 실려 있습니다.\n"
            )
        else:
            lines.append(
                f"당신은 {risk_profile_name} 성향이지만, 현재 포트폴리오에서 "
                f"{dominant_factor}({dom_role}) 요인의 비중은 목표 대비 다소 낮은 편입니다.\n"
            )

        if over:
            over_names = ", ".join([f"Factor {i}" for i in over])
            lines.append(f"· 특히 {over_names} 쪽으로 노출이 다소 몰려 있는 모습입니다.")
        if under:
            under_names = ", ".join([f"Factor {i}" for i in under])
            lines.append(f"· 반대로 {under_names} 쪽은 성향 대비 상대적으로 노출이 부족한 편입니다.")

        lines.append("")

    lines.append("각 요인이 대략 어떤 성격을 갖는지, 아주 단순화해서 정리하면 다음과 같습니다.\n")
    for i, f in enumerate(factors, start=1):
        lines.append(f"· {_factor_role_comment(i, f, n_factors)}")
    lines.append("")

    lines.append("[3] 투자 성향에 비춘 요인별 비중 점검\n")
    lines.append("당신의 투자 성향을 기준으로 설정한 목표 요인 비중과 실제 비중을 비교하면 다음과 같습니다.\n")

    for i, f in enumerate(factors, start=1):
        a = norm_exp[f]
        t = target[f]
        comment = _diff_comment(a, t)
        lines.append(
            f"· {f}: 실제 {a*100:.1f}%, 목표 {t*100:.1f}% → {comment}"
        )

    lines.append("")

    if not over and not under:
        lines.append(
            "요약하면, 큰 쏠림 없이 전반적으로 투자 성향에 비교적 잘 맞는 배분 상태입니다.\n"
        )
    else:
        pieces = []
        if over:
            pieces.append("일부 요인에는 비중이 다소 많이 몰려 있고")
        if under:
            pieces.append("어떤 요인들은 성향에 비해 노출이 부족한 편입니다")
        lines.append(
            "요약하면, " + " · ".join(pieces) + ". "
                                            "장기적인 관점에서 리밸런싱을 한 번 고민해 볼 만한 구조입니다.\n"
        )

    lines.append("[4] 쏠림을 완화하거나 보완할 때 참고할 수 있는 아이디어\n")

    trim = analysis.trim_candidates or {}
    add = analysis.add_candidates or {}

    if trim:
        lines.append("① 과투자된(비중이 많은) 요인 쪽에서 비중을 줄일 때 참고할 수 있는 종목들입니다.\n")
        for f_idx, stocks in trim.items():
            if not stocks:
                continue
            fname = f"Factor {f_idx}"
            joined = _join_code_list(stocks)
            lines.append(f"· {fname} 관련 비중 축소 후보: {joined}")
        lines.append(
            "\n이 종목들은 해당 요인의 움직임에 상대적으로 민감한 편이라, "
            "비중을 조금만 줄여도 그 요인에 대한 전체 노출이 완화되는 효과가 있을 수 있습니다.\n"
        )
    else:
        lines.append(
            "현재 뚜렷하게 너무 많이 담았다고 판단되는 요인은 크지 않아서, "
            "즉시 비중 축소가 꼭 필요해 보이진 않습니다.\n"
        )

    if add:
        lines.append("② 부족한 요인을 보완하기 위해 추가로 담을 때 참고할 수 있는 종목들입니다.\n")
        for f_idx, stocks in add.items():
            if not stocks:
                continue
            fname = f"Factor {f_idx}"
            joined = _join_code_list(stocks)
            lines.append(f"· {fname} 노출을 늘릴 때 참고할 종목: {joined}")
        lines.append(
            "\n위 종목들은 해당 요인에 대한 노출이 상대적으로 높은 편이라, "
            "장기적으로 조금씩 편입하면 투자 성향에 맞는 목표 비중에 가까워지는 데 도움이 될 수 있습니다.\n"
        )
    else:
        lines.append(
            "부족한 요인을 보완하기 위해 당장 특정 종목을 늘려야 할 정도의 쏠림은 크지 않은 편입니다.\n"
        )

    lines.append("[5] 최근 6개월 동안 각 요인의 성과\n")
    lines.append("최근 6개월 누적 수익률 기준으로, 어떤 요인이 힘을 쓰고 있었는지 정리하면 다음과 같습니다.\n")

    sorted_mom = factor_momentum.sort_values(ascending=False)

    best_factor = None
    worst_factor = None
    if len(sorted_mom) > 0:
        best_factor = sorted_mom.index[0]
        worst_factor = sorted_mom.index[-1]

    for f, v in sorted_mom.items():
        lines.append(f"· {f}: {v*100:.2f}% → {_momentum_comment(v)}")

    lines.append("")

    if best_factor and worst_factor:
        lines.append(
            f"요약하면, 최근 6개월 동안에는 {best_factor} 요인이 상대적으로 가장 좋은 성과를, "
            f"{worst_factor} 요인은 가장 아쉬운 성과를 보여준 편입니다.\n"
        )

    lines.append("[6] 한 줄로 정리하면\n")

    if not over and not under:
        main_comment = (
            "투자 성향에 비해 크게 튀는 쏠림은 없고, "
            "다만 특정 요인의 환경에 따라 계좌 등락폭이 좌우될 수 있는 무난한 분산 포트폴리오에 가깝습니다."
        )
    else:
        parts = []
        if over:
            over_names = ", ".join([f"Factor {i}" for i in over])
            parts.append(f"{over_names} 쪽으로 비중이 다소 몰려 있고")
        if under:
            under_names = ", ".join([f"Factor {i}" for i in under])
            parts.append(f"{under_names} 쪽은 성향 대비 상대적으로 노출이 적은 편입니다")
        main_comment = " / ".join(parts) + "."

    lines.append(f"· 요약: {main_comment}\n")

    lines.append(
        "이 리포트는 과거 데이터와 통계적 기법(PCA)으로 포트폴리오의 구조와 성격을 설명해 주는 도구일 뿐, "
        "특정 종목의 매수·매도를 직접적으로 권유하는 것은 아닙니다. "
        "다만, 앞으로 리밸런싱을 고민할 때 어디에 쏠려 있고 무엇을 보완할지 한눈에 정리해 주는 참고용 나침반으로 활용해 주세요.\n"
    )

    return "\n".join(lines)
