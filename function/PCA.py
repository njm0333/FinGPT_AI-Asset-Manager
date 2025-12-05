import sys
import traceback
from dataclasses import dataclass
from typing import List, Dict, Optional

import numpy as np
import pandas as pd
import yfinance as yf

from sklearn.decomposition import PCA
from sklearn.preprocessing import scale

from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QComboBox,
    QDateEdit, QTabWidget, QPlainTextEdit,
    QTableWidget, QTableWidgetItem, QMessageBox,
    QSizePolicy
)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


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

    1) 수익률 winsorize (2.5%~97.5%)
    2) 각 종목별로 (mean, std) 정규화
    3) sklearn.preprocessing.scale 로 한 번 더 표준화
    4) 정규화된 수익률의 공분산 행렬에 PCA 적용
    5) pca.components_ 로 eigen portfolio 생성 (각 행의 합 = 1)
    6) eigen portfolio 수익률 계산
    """

    # 1) winsorize: 각 종목(column) 기준으로 2.5%~97.5% 범위로 자름
    lower = returns.quantile(q=0.025)
    upper = returns.quantile(q=0.975)
    winsorized = returns.clip(lower=lower, upper=upper, axis=1)

    # 2) 각 종목별 정규화 (z-score): (r - mean) / std
    standardized = winsorized.apply(lambda x: x.sub(x.mean()).div(x.std()), axis=0)

    # 3) sklearn scale로 추가 표준화 (교과서 코드 구조 반영)
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

    # 교과서와 동일: components → DataFrame → 각 행의 합이 1이 되도록 정규화
    eigen_portfolios = pd.DataFrame(components, columns=cov.columns)
    eigen_portfolios = eigen_portfolios.div(eigen_portfolios.sum(axis=1), axis=0)
    eigen_portfolios.index = [f'Factor {i+1}' for i in range(eigen_portfolios.shape[0])]

    explained = pd.Series(
        pca.explained_variance_ratio_[:max_factors],
        index=eigen_portfolios.index
    )

    # 6) Market(평균 수익률) & Factor 수익률 계산
    #    교과서 코드: returns.mul(eigen_portfolios.iloc[i]).sum(1)
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


# =========================
# 투자성향 반영 요인 타깃
# =========================

def get_risk_profile_targets(profile: str, n_factors: int) -> pd.Series:
    """
    투자 성향에 따라 '요인 노출' 목표 비중을 정의.
    Factor 1을 좀 더 안정/시장, Factor 2를 성장/공격 쪽이라고 가정한 간단 버전.
    (알고리즘과 직접적으로 연결된 부분은 아니라서, 여기서는 컨셉만 유지)
    """
    if profile == "Conservative":
        base = np.array([0.5, 0.2, 0.2, 0.1])
    elif profile == "Balanced":
        base = np.array([0.4, 0.3, 0.2, 0.1])
    else:  # Aggressive
        base = np.array([0.3, 0.4, 0.2, 0.1])

    if n_factors < len(base):
        base = base[:n_factors]
    elif n_factors > len(base):
        extra = np.full(n_factors - len(base), 0.05)
        base = np.concatenate([base, extra])

    base = np.abs(base)
    base = base / base.sum()

    idx = [f'Factor {i+1}' for i in range(n_factors)]
    return pd.Series(base, index=idx)


# =========================
# 포트폴리오 요인 분석
# =========================

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

    # 요인 노출도: factor k 에 대해 Σ_i w_i * eigen[k, i]
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
        trim_candidates[i + 1] = df.head(5).index.tolist()   # Factor 번호는 1-based로 저장

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
    factor_momentum = (1 + recent).prod() - 1.0  # 누적 수익률

    # 요약 텍스트 생성
    lines = []
    lines.append("📊 PCA 기반 포트폴리오 요인 분석 결과\n")

    lines.append("1️⃣ 요인별 현재 노출 비중 (정규화된 절대값 기준):")
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
        lines.append("\n4️⃣ 과투자 요인 관련, 비중 조정(줄이기) 후보 종목:")
        for f_idx, tickers in trim_candidates.items():
            lines.append(f"   - Factor {f_idx}: {', '.join(tickers)}")
    if add_candidates:
        lines.append("\n5️⃣ 과소투자 요인 관련, 비중 보강(늘리기) 후보 종목:")
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
# PyQt 메인 윈도우
# =========================

class PCAAdvisorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PCA 기반 포트폴리오 요인 분석 & 추천 (미국/한국 주식)")
        self.resize(1200, 800)

        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)

        # ----- 좌측: 입력 패널 -----
        input_panel = QWidget()
        input_layout = QVBoxLayout(input_panel)

        form = QFormLayout()

        self.ticker_edit = QLineEdit()
        self.ticker_edit.setPlaceholderText("예: AAPL,MSFT,GOOGL,005930.KS (쉼표로 구분)")
        form.addRow("보유 종목 티커들", self.ticker_edit)

        self.weight_edit = QLineEdit()
        self.weight_edit.setPlaceholderText("예: 0.3,0.3,0.4 (비워두면 균등 비중)")
        form.addRow("각 종목 비중", self.weight_edit)

        self.profile_combo = QComboBox()
        self.profile_combo.addItems(["Conservative", "Balanced", "Aggressive"])
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

        self.run_button = QPushButton("분석 실행")
        self.run_button.clicked.connect(self.on_run_analysis)
        input_layout.addWidget(self.run_button)

        input_layout.addStretch()

        # ----- 우측: 결과 탭 -----
        self.tabs = QTabWidget()

        # Tab 1: 요약 리포트
        self.summary_text = QPlainTextEdit()
        self.summary_text.setReadOnly(True)
        tab_summary = QWidget()
        v1 = QVBoxLayout(tab_summary)
        v1.addWidget(self.summary_text)
        self.tabs.addTab(tab_summary, "요약 리포트")

        # Tab 2: 요인 노출 테이블
        tab_table = QWidget()
        v2 = QVBoxLayout(tab_table)
        self.exposure_table = QTableWidget()
        v2.addWidget(self.exposure_table)
        self.tabs.addTab(tab_table, "요인 노출도 & Target")

        # Tab 3: 그래프
        tab_plot = QWidget()
        v3 = QVBoxLayout(tab_plot)

        self.canvas1 = MplCanvas(self, width=6, height=3)
        self.canvas2 = MplCanvas(self, width=6, height=3)

        self.canvas1.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.canvas2.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        v3.addWidget(QLabel("요인별 설명분산 비율"))
        v3.addWidget(self.canvas1)
        v3.addWidget(QLabel("시장(평균) vs 요인 포트폴리오 누적 수익률"))
        v3.addWidget(self.canvas2)
        self.tabs.addTab(tab_plot, "그래프")

        main_layout.addWidget(input_panel, stretch=1)
        main_layout.addWidget(self.tabs, stretch=2)

        self.setCentralWidget(main_widget)

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
            ["Factor", "현재 노출 비중(정규화)", "목표 노출 비중"]
        )

        for row, f in enumerate(factors):
            self.exposure_table.setItem(row, 0, QTableWidgetItem(f))
            self.exposure_table.setItem(row, 1, QTableWidgetItem(f"{norm_exp[f]*100:.2f}%"))
            self.exposure_table.setItem(row, 2, QTableWidgetItem(f"{target[f]*100:.2f}%"))

        self.exposure_table.resizeColumnsToContents()

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


def main():
    app = QApplication(sys.argv)
    win = PCAAdvisorWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
