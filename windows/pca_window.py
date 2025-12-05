import sys
import traceback
from dataclasses import dataclass
from typing import List, Dict, Optional

import numpy as np
import pandas as pd
import yfinance as yf

from sklearn.decomposition import PCA
from sklearn.preprocessing import scale

from PyQt6.QtCore import QDate, Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QComboBox,
    QDateEdit, QTabWidget, QPlainTextEdit,
    QTableWidget, QTableWidgetItem, QMessageBox,
    QSizePolicy, QFrame
)



from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# ★ Fin GPT 스타일 공통 함수
from styles import apply_global_style


# =========================
# 데이터/분석용 데이터클래스
# =========================

@dataclass
class PortfolioInput:
    tickers: List[str]
    weights: np.ndarray  # shape (n_assets,)
    start: str           # 'YYYY-MM-DD'
    end: str             # 'YYYY-MM-DD'
    risk_profile: str    # 'Conservative', 'Balanced', 'Aggressive'


@dataclass
class PCAResult:
    # 원본(클리닝된) 일간 수익률
    returns: pd.DataFrame
    # 정규화된 수익률 기반 공분산 행렬
    cov: pd.DataFrame
    pca: PCA
    eigen_portfolios: pd.DataFrame   # shape (n_factors, n_assets)
    explained_variance: pd.Series    # shape (n_factors,)
    factor_returns: pd.DataFrame     # columns = Factor 1..k
    market_returns: pd.Series        # equal-weighted "market"


@dataclass
class AnalysisResult:
    exposures: pd.Series            # raw exposures (Factor 1..k)
    norm_exposures: pd.Series       # normalized abs exposures (sum=1)
    target_exposures: pd.Series     # per risk profile
    over_factors: List[int]         # 1-based factor 번호
    under_factors: List[int]
    trim_candidates: Dict[int, List[str]]
    add_candidates: Dict[int, List[str]]
    factor_momentum: pd.Series      # 최근 6개월 누적 수익률
    summary_text: str


# =========================
# 데이터 로딩 & 전처리
# =========================

def fetch_price_data(tickers: List[str], start: str, end: str) -> pd.DataFrame:
    if not tickers:
        raise ValueError("티커가 비어 있습니다.")

    data = yf.download(
        tickers,
        start=start,
        end=end,
        auto_adjust=False,      # Adj Close 사용
        progress=False
    )

    # yfinance 결과 형식 맞추기
    if isinstance(data.columns, pd.MultiIndex):
        # MultiIndex → 'Adj Close' 레벨만 선택
        if ('Adj Close' in data.columns.get_level_values(0)
                or 'Adj Close' in data.columns.get_level_values(-1)):
            if 'Adj Close' in data.columns.get_level_values(0):
                price = data['Adj Close']
            else:
                price = data.xs('Adj Close', axis=1, level=-1)
        else:
            price = data.iloc[:, 0].unstack()
    else:
        if isinstance(data, pd.Series):
            price = data.to_frame(name=tickers[0])
        else:
            price = data

    price.columns = [str(c) for c in price.columns]
    price = price.dropna(axis=1, how='all')

    if price.shape[1] < 2:
        raise ValueError("유효한 데이터가 있는 종목이 2개 미만입니다. 기간을 늘리거나 다른 종목을 사용해보세요.")

    return price


def prepare_returns(price: pd.DataFrame) -> pd.DataFrame:
    """
    교과서와 동일한 흐름을 따르기 위한 '기본' 수익률만 만든다.
    나머지 winsorize/정규화는 run_pca 안에서 수행.
    """
    returns = price.pct_change().dropna(how='all')

    # 너무 결측치가 많은 열/행 제거 (95% 이상 유효한 값이 있는 것만)
    col_thresh = int(returns.shape[0] * 0.95)
    row_thresh = int(returns.shape[1] * 0.95)
    returns = returns.dropna(axis=1, thresh=col_thresh)
    returns = returns.dropna(axis=0, thresh=row_thresh)

    if returns.shape[1] < 2:
        raise ValueError("수익률 계산 후 유효한 종목이 2개 미만입니다.")

    return returns


# =========================
# PCA & Eigen Portfolios
# =========================

def run_pca(returns: pd.DataFrame, n_factors: int = 4) -> PCAResult:
    """
    교과서의 'PCA for Algorithmic Trading: Eigen Portfolios' 로직 그대로 구현
    """

    # 1) winsorize: 각 종목(column) 기준으로 2.5%~97.5% 범위로 자름
    lower = returns.quantile(q=0.025)
    upper = returns.quantile(q=0.975)
    winsorized = returns.clip(lower=lower, upper=upper, axis=1)

    # 2) 각 종목별 정규화 (z-score): (r - mean) / std
    standardized = winsorized.apply(lambda x: x.sub(x.mean()).div(x.std()), axis=0)

    # 3) sklearn scale로 추가 표준화
    normed_arr = scale(standardized)  # shape: (n_samples, n_assets)
    normed_returns = pd.DataFrame(normed_arr,
                                  index=standardized.index,
                                  columns=standardized.columns)

    # 4) 정규화된 수익률의 공분산 행렬
    cov = normed_returns.cov()

    # 5) PCA 수행
    pca = PCA()
    pca.fit(cov)

    n_assets = cov.shape[0]
    max_factors = min(n_factors, n_assets)
    components = pca.components_[:max_factors]

    # components → DataFrame → 각 행의 합이 1이 되도록 정규화
    eigen_portfolios = pd.DataFrame(components, columns=cov.columns)
    eigen_portfolios = eigen_portfolios.div(eigen_portfolios.sum(axis=1), axis=0)
    eigen_portfolios.index = [f'Factor {i+1}' for i in range(eigen_portfolios.shape[0])]

    explained = pd.Series(
        pca.explained_variance_ratio_[:max_factors],
        index=eigen_portfolios.index
    )

    # Market(평균 수익률) & Factor 수익률 계산
    market_ret = returns.mean(axis=1)

    factor_rets = {}
    for fname in eigen_portfolios.index:
        w = eigen_portfolios.loc[fname]          # 각 factor의 종목별 weight
        r = returns.mul(w, axis=1).sum(axis=1)   # 일간 factor 수익률
        factor_rets[fname] = r

    factor_returns = pd.DataFrame(factor_rets, index=returns.index)

    return PCAResult(
        returns=returns,
        cov=cov,
        pca=pca,
        eigen_portfolios=eigen_portfolios,
        explained_variance=explained,
        factor_returns=factor_returns,
        market_returns=market_ret
    )
def get_risk_profile_targets(profile: str, n_factors: int) -> pd.Series:

    base_map = {
        "안정형":     np.array([0.40, 0.10, 0.40, 0.10]),
        "안정추구형": np.array([0.40, 0.20, 0.30, 0.10]),
        "위험중립형": np.array([0.35, 0.30, 0.25, 0.10]),
        "적극투자형": np.array([0.30, 0.40, 0.20, 0.10]),
        "공격투자형": np.array([0.25, 0.50, 0.15, 0.10]),
    }
    base = base_map.get(profile, base_map["위험중립형"])
    if n_factors < len(base):
        base = base[:n_factors]
    elif n_factors > len(base):
        extra = np.full(n_factors - len(base), 0.05)
        base = np.concatenate([base, extra])

    base = np.abs(base)
    base = base / base.sum()

    idx = [f"Factor {i+1}" for i in range(n_factors)]
    return pd.Series(base, index=idx)
def analyze_portfolio(
        pca_res: PCAResult,
        portfolio_weights: pd.Series,
        risk_profile: str
) -> AnalysisResult:
    eigen = pca_res.eigen_portfolios

    # weights index를 eigen.columns에 맞추기
    w = portfolio_weights.reindex(eigen.columns).fillna(0.0)
    if abs(w.sum()) > 1e-8:
        w = w / w.sum()  # 비중 정규화

    # 요인 노출도
    exposures = eigen.dot(w)  # index = Factor 1..k

    # 절댓값 기준 정규화 (노출 비중)
    norm_exposures = exposures.abs()
    if norm_exposures.sum() > 0:
        norm_exposures = norm_exposures / norm_exposures.sum()

    target_exposures = get_risk_profile_targets(risk_profile, len(exposures))

    # 과다/과소 요인 판별 (단순 threshold: 0.1)
    diff = norm_exposures - target_exposures
    over_idx = [i for i, v in enumerate(diff.values) if v > 0.10]   # 0-based
    under_idx = [i for i, v in enumerate(diff.values) if v < -0.10]

    trim_candidates: Dict[int, List[str]] = {}
    add_candidates: Dict[int, List[str]] = {}

    # 과투자 요인 → 줄이기 후보
    for i in over_idx:
        fname = exposures.index[i]
        factor_weights = eigen.loc[fname]
        df = pd.DataFrame({
            'factor_weight': factor_weights,
            'port_weight': w
        })
        df = df[df['port_weight'] > 0]
        df = df.reindex(factor_weights.index).dropna()
        df = df.sort_values('factor_weight', ascending=False)
        trim_candidates[i + 1] = df.head(5).index.tolist()

    # 과소투자 요인 → 늘리기 후보
    for i in under_idx:
        fname = exposures.index[i]
        factor_weights = eigen.loc[fname]
        df = pd.DataFrame({
            'factor_weight': factor_weights,
            'port_weight': w
        })
        df = df.sort_values('factor_weight', ascending=False)
        add_candidates[i + 1] = df.head(5).index.tolist()

    # 최근 6개월 factor 모멘텀 (누적 수익률)
    factor_returns = pca_res.factor_returns
    if len(factor_returns) > 120:
        recent = factor_returns.iloc[-120:]
    else:
        recent = factor_returns
    factor_momentum = (1 + recent).prod() - 1.0

    # 요약 텍스트 생성
    lines = []
    lines.append("📊 PCA 기반 포트폴리오 요인 분석 결과\n")

    lines.append("1️⃣ 요인별 현재 노출 비중:")
    for fname, val in norm_exposures.items():
        lines.append(f"   - {fname}: {val*100:.1f}%")

    lines.append("\n2️⃣ 투자 성향에 따른 목표 요인 비중:")
    for fname, val in target_exposures.items():
        lines.append(f"   - {fname}: {val*100:.1f}%")

    if over_idx or under_idx:
        lines.append("\n3️⃣ 요인 쏠림 진단:")
        if over_idx:
            over_desc = ", ".join([f"Factor {i+1}" for i in over_idx])
            lines.append(f"   - 과투자 요인: {over_desc}")
        if under_idx:
            under_desc = ", ".join([f"Factor {i+1}" for i in under_idx])
            lines.append(f"   - 과소투자 요인: {under_desc}")
    else:
        lines.append("\n3️⃣ 요인 쏠림 진단: 투자 성향 대비 큰 쏠림은 없습니다.")

    if trim_candidates:
        lines.append("\n4️⃣ 과투자 요인 관련, 비중 조정 후보 종목:")
        for f_idx, tickers in trim_candidates.items():
            lines.append(f"   - Factor {f_idx}: {', '.join(tickers)}")
    if add_candidates:
        lines.append("\n5️⃣ 과소투자 요인 관련, 비중 보강후보 종목:")
        for f_idx, tickers in add_candidates.items():
            lines.append(f"   - Factor {f_idx}: {', '.join(tickers)}")

    lines.append("\n6️⃣ 최근 6개월 요인 성과(누적 수익률 기준):")
    for fname, val in factor_momentum.sort_values(ascending=False).items():
        lines.append(f"   - {fname}: {val*100:.2f}%")

    summary_text = "\n".join(lines)

    return AnalysisResult(
        exposures=exposures,
        norm_exposures=norm_exposures,
        target_exposures=target_exposures,
        over_factors=[i + 1 for i in over_idx],
        under_factors=[i + 1 for i in under_idx],
        trim_candidates=trim_candidates,
        add_candidates=add_candidates,
        factor_momentum=factor_momentum,
        summary_text=summary_text
    )


# =========================
# Matplotlib 캔버스
# =========================

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=6, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(fig)
        self.setParent(parent)
        self.axes = fig.add_subplot(111)

# =========================
# PyQt StackedWidget용 PCA 페이지
# =========================
#done

class PCAAdvisorPage(QWidget):


    def _go_help(self):
        self.stack.setCurrentIndex(5)

    def _go_explain(self):
        if self.last_analysis_result is None:
            return

        # 1) 자연어 설명 생성기 호출
        from function.PCA_Report import generate_portfolio_report
        explanation = generate_portfolio_report(
            self.last_analysis_result,
            self.profile_combo.currentText()
        )

        # 2) ExplainPage 찾아서 텍스트 전달
        explain_page = self.stack.widget(6)   # ExplainPage index
        explain_page.set_explanation_text(explanation)

        # 3) 화면 전환
        self.stack.setCurrentIndex(6)



    def __init__(self, stack):
        super().__init__()
        self.stack = stack   # 🔹 AppWindow(QStackedWidget) 참조
        self.setWindowTitle("PCA 기반 포트폴리오 요인 분석 & 추천 (미국/한국 주식)")
        self.resize(1200, 800)

        # ---- 전체 레이아웃: 상단 타이틀 + 콘텐츠 ----
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(32, 24, 32, 24)
        root_layout.setSpacing(24)

        # 상단 타이틀 / 서브타이틀 (HomePage 느낌 유지)
        header_title = QLabel("PCA 기반 포트폴리오 요인 분석")
        header_title.setObjectName("title")
        header_title.setAlignment(Qt.AlignmentFlag.AlignLeft)

        header_subtitle = QLabel(
            "투자 성향에 맞는 요인별 쏠림과 리밸런싱 가이드를 Fin GPT가 정리해 드립니다."
        )
        header_subtitle.setObjectName("subtitle")
        header_subtitle.setWordWrap(True)

        root_layout.addWidget(header_title)
        root_layout.addWidget(header_subtitle)
        root_layout.addSpacing(8)

        # ---- 가운데: 좌우 카드 2개 배치 ----
        content_layout = QHBoxLayout()
        content_layout.setSpacing(24)
        root_layout.addLayout(content_layout, stretch=1)

        # ----- 좌측: 입력 카드 ----- #
        input_card = QFrame()
        input_card.setObjectName("card")
        input_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        input_layout = QVBoxLayout(input_card)
        input_layout.setSpacing(16)

        input_title = QLabel("내 포트폴리오 입력")
        input_title.setObjectName("subtitle")
        input_layout.addWidget(input_title)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form.setFormAlignment(Qt.AlignmentFlag.AlignTop)
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(10)

        self.ticker_edit = QLineEdit()
        self.ticker_edit.setPlaceholderText("예: AAPL, 005930.KS")
        form.addRow("보유 종목 티커들", self.ticker_edit)

        self.weight_edit = QLineEdit()
        self.weight_edit.setPlaceholderText("예: 0.3,0.7 (공란 균등처리)")
        form.addRow("각 종목 비중", self.weight_edit)

        self.profile_combo = QComboBox()
        self.profile_combo.addItems(["안정형", "안정추구형", "위험중립형", "적극투자형", "공격투자형"])
        form.addRow("투자 성향", self.profile_combo)

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addYears(-5))
        form.addRow("시작일", self.start_date)

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        form.addRow("종료일", self.end_date)

        input_layout.addLayout(form)

        # 실행 버튼 (동적 크기)
        self.run_button = QPushButton("분석 실행")
        self.run_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.run_button.setMinimumHeight(44)
        self.run_button.clicked.connect(self.on_run_analysis)
        input_layout.addSpacing(12)
        input_layout.addWidget(self.run_button)

        input_layout.addStretch(1)

        # ----- 우측: 결과 카드 ----- #
        result_card = QFrame()
        result_card.setObjectName("card")
        result_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        result_layout = QVBoxLayout(result_card)
        result_layout.setSpacing(16)

        result_title = QLabel("요인 분석 결과")
        result_title.setObjectName("subtitle")
        result_layout.addWidget(result_title)

        # TabWidget 그대로 사용, 카드 안에 넣기
        self.tabs = QTabWidget()
        self.tabs.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Tab 1: 요약 리포트
        self.summary_text = QPlainTextEdit()
        self.summary_text.setReadOnly(True)
        tab_summary = QWidget()
        v1 = QVBoxLayout(tab_summary)
        v1.setContentsMargins(0, 0, 0, 0)
        v1.addWidget(self.summary_text)
        self.tabs.addTab(tab_summary, "요약 리포트")

        # Tab 2: 요인 노출 테이블
        tab_table = QWidget()
        v2 = QVBoxLayout(tab_table)
        v2.setContentsMargins(0, 0, 0, 0)
        self.exposure_table = QTableWidget()
        v2.addWidget(self.exposure_table)
        self.tabs.addTab(tab_table, "요인 노출도 & Target")

        # Tab 3: 그래프
        tab_plot = QWidget()
        v3 = QVBoxLayout(tab_plot)
        v3.setContentsMargins(0, 0, 0, 0)

        label_ev = QLabel("요인별 설명분산 비율")
        label_ev.setObjectName("story")
        v3.addWidget(label_ev)

        self.canvas1 = MplCanvas(self, width=6, height=3)
        self.canvas1.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        v3.addWidget(self.canvas1)

        label_cum = QLabel("시장(평균) vs 요인 포트폴리오 누적 수익률")
        label_cum.setObjectName("story")
        v3.addWidget(label_cum)

        self.canvas2 = MplCanvas(self, width=6, height=3)
        self.canvas2.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        v3.addWidget(self.canvas2)

        self.tabs.addTab(tab_plot, "그래프")

        result_layout.addWidget(self.tabs)

        # 좌우 카드 레이아웃에 추가
        content_layout.addWidget(input_card, stretch=1)
        content_layout.addWidget(result_card, stretch=2)

        # ---- 하단: 다음(완료) 버튼 ----
        root_layout.addSpacing(16)
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch(1)
        # 첫 번째 버튼: 어려워요 도와주세요 ㅠㅠ
        self.help_button = QPushButton("어려워요 도와주세요 ㅠㅠ")
        self.help_button.setMinimumHeight(44)
        self.help_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.help_button.clicked.connect(self._go_help)   # 새로운 함수로 연결
        bottom_layout.addWidget(self.help_button)

        # 두 번째 버튼: 보고서 설명 듣기 (해설 페이지 이동)
        self.explain_button = QPushButton("보고서 설명 듣기")
        self.explain_button.setMinimumHeight(44)
        self.explain_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.explain_button.clicked.connect(self._go_explain)  # 새로운 함수
        bottom_layout.addWidget(self.explain_button)

        root_layout.addLayout(bottom_layout)

        # 마지막으로 스타일 적용
        apply_global_style(self)

        # 상태 보관용
        self.last_pca_result: Optional[PCAResult] = None
        self.last_analysis_result: Optional[AnalysisResult] = None

    # ------------- 이벤트 -------------




    def on_run_analysis(self):
        try:
            portfolio_input = self.collect_input()
            pca_res = self.perform_pca_analysis(portfolio_input)
            analysis_res = analyze_portfolio(
                pca_res,
                self.build_weight_series(portfolio_input),
                portfolio_input.risk_profile
            )

            self.last_pca_result = pca_res
            self.last_analysis_result = analysis_res

            self.update_summary_tab(analysis_res)
            self.update_table_tab(analysis_res)
            self.update_plot_tab(pca_res)

            QMessageBox.information(self, "완료", "분석이 완료되었습니다.")

        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "에러", f"분석 중 에러가 발생했습니다:\n{e}")

    # ------------- 입력 수집 -------------
    def collect_input(self) -> PortfolioInput:
        tickers_str = self.ticker_edit.text().strip()
        if not tickers_str:
            raise ValueError("보유 종목 티커를 입력해주세요.")

        tickers = [t.strip() for t in tickers_str.split(",") if t.strip()]
        if len(tickers) < 2:
            raise ValueError("최소 2개 이상의 종목을 입력해야 PCA 분석이 가능합니다.")

        weights_str = self.weight_edit.text().strip()
        if weights_str:
            parts = [p.strip() for p in weights_str.split(",") if p.strip()]
            if len(parts) != len(tickers):
                raise ValueError("종목 수와 비중의 개수가 일치하지 않습니다.")
            weights = np.array([float(p) for p in parts], dtype=float)
        else:
            weights = np.ones(len(tickers), dtype=float) / len(tickers)

        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")
        profile = self.profile_combo.currentText()

        return PortfolioInput(
            tickers=tickers,
            weights=weights,
            start=start,
            end=end,
            risk_profile=profile
        )

    def perform_pca_analysis(self, p_in: PortfolioInput) -> PCAResult:
        price = fetch_price_data(p_in.tickers, p_in.start, p_in.end)
        returns = prepare_returns(price)

        missing = set(p_in.tickers) - set(returns.columns)
        if missing:
            QMessageBox.warning(
                self,
                "경고",
                f"다음 종목은 데이터 부족으로 분석에서 제외되었습니다:\n{', '.join(missing)}"
            )

        pca_res = run_pca(returns, n_factors=4)
        return pca_res

    def build_weight_series(self, p_in: PortfolioInput) -> pd.Series:
        return pd.Series(p_in.weights, index=p_in.tickers)

    # ------------- UI 업데이트 -------------
    def update_summary_tab(self, analysis_res: AnalysisResult):
        self.summary_text.setPlainText(analysis_res.summary_text)

    def update_table_tab(self, analysis_res: AnalysisResult):
        exposures = analysis_res.exposures
        norm_exp = analysis_res.norm_exposures
        target = analysis_res.target_exposures

        factors = exposures.index.tolist()

        self.exposure_table.clear()
        self.exposure_table.setRowCount(len(factors))
        self.exposure_table.setColumnCount(3)
        self.exposure_table.setHorizontalHeaderLabels(
            ["Factor", "현재 노출 비중", "목표 노출 비중"]
        )

        for row, f in enumerate(factors):
            self.exposure_table.setItem(row, 0, QTableWidgetItem(f))
            self.exposure_table.setItem(row, 1, QTableWidgetItem(f"{norm_exp[f]*100:.2f}%"))
            self.exposure_table.setItem(row, 2, QTableWidgetItem(f"{target[f]*100:.2f}%"))

        self.exposure_table.resizeColumnsToContents()

        # ------------- 그래프 업데이트 -------------
    def update_plot_tab(self, pca_res: PCAResult):
        # 설명분산 그래프
        self.canvas1.axes.clear()
        ev = pca_res.explained_variance
        self.canvas1.axes.bar(range(len(ev.index)), ev.values)
        self.canvas1.axes.set_xticks(range(len(ev.index)))
        self.canvas1.axes.set_xticklabels(ev.index, rotation=0)
        self.canvas1.axes.set_ylabel("Explained Variance Ratio")
        self.canvas1.axes.set_xlabel("Factors")
        self.canvas1.axes.grid(True, axis='y', linestyle='--', alpha=0.4)
        self.canvas1.draw()

        # 누적 수익률 그래프 (시장 + Factor 1~3까지)
        self.canvas2.axes.clear()

        market_cum = (1 + pca_res.market_returns).cumprod() - 1
        self.canvas2.axes.plot(market_cum.index, market_cum.values, label="Market (Equal-weighted)")

        for i, col in enumerate(pca_res.factor_returns.columns[:3]):
            cum = (1 + pca_res.factor_returns[col]).cumprod() - 1
            self.canvas2.axes.plot(cum.index, cum.values, label=col)

        self.canvas2.axes.set_xlabel("Date")
        self.canvas2.axes.set_ylabel("Cumulative Return")
        self.canvas2.axes.legend()
        self.canvas2.axes.grid(True, linestyle='--', alpha=0.4)
        self.canvas2.draw()


