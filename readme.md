# FinGPT - AI Asset Manager

<img width="836" height="342" alt="스크린샷 2025-12-06 034941" src="https://github.com/user-attachments/assets/50f7b24b-563a-4024-a6e5-ec186b73d798" />

---

## FinGPT : AI 자산 운용 매니저
**FinGPT**는 투자 성향 분석과 PCA를 활용한 요인 분석을 수행하고, 그 결과를 기반으로 개인별 포트폴리오의 요인 노출·쏠림·리밸런싱 가이드를 맞춤으로 제공하는 프로그램입니다.

<img width="1121" height="746" alt="image" src="https://github.com/user-attachments/assets/4504d48d-4b53-4f79-9543-1b84f24ff677" />


## Motivation

최근 한국 사회에서 자산 형성의 기회는 단기 투기와 부동산 중심의 시장 흐름에 지나치게 집중되어 있었습니다.

또한 주식 가격이 오른다는 뉴스를 보면서도 "경제는 어려운데...", "나는 잘 모르니까.." 와 같은 고민을 하는 사람이 늘어나고 있습니다.

그 결과, 많은 개인 투자자들이 건전하고 지속 가능한 방식으로 자산을 성장시키는 경험을 얻기 어려운 구조가 만들어지고 있었습니다.

저는 이 문제에서 착안했습니다.

“투자를 어렵게 느끼는 사람들이  도와줄 방법이 없을까?”

이 질문에서 시작된 것이 바로 본 프로젝트입니다.

이 프로젝트는 투자 경험이 부족한 사용자라도 요인의 움직임과 포트폴리오의 구조를 쉽게 파악하고, 이를 쉽게 분석한 리포트를 제공받아 장기적인 투자에 도움이 되길 바라는 마음에서 시작했습니다.
이 프로젝트는 아래와 같은 기능을 통해 여러분의 투자를 지원합니다.

- 개인별 투자성향 분석 및 설명

- PCA 기반 요인별 현재 노출 비중

- 투자 성향에 맞춘 이상적 목표 요인 비중 제공

- Yahoo Finance 데이터 기반 한/미 주식 포트폴리오의 요인 노출 분석

- 투자 성향에 따른 목표 요인 비중 비교

- 쏠림 진단 및 리밸런싱 가이드 제공

- 초보자용 도움말 제공

- 분석 결과 레포트 제공

이 프로그램이 당신의 투자 여정에 조금이나마 도움이 되길 바랍니다.



## 개발한 사람
- njm0333(노정민) : 전체 개발 총괄

## 목차
- [설치](#설치)
- [사용법](#사용법)
- [전체 기능 및 구현 설명 _ for dev](#전체-기능-및-구현-설명-_-for-dev)
  - [windows/survey_window.py](#windowssurvey_windowpy)
  - [windows/pca_window.py](#windowspca_windowpy)
  - [function/PCA_Report.py](#functionpca_reportpy)
- [추가 개발예정 사항](#추가-개발예정-사항)
- [Reference](#reference)
- [License](#license)

## 설치

- 파이썬 3.11 이상을 사용하고 있다면 누구나 사용 할 수 있습니다!
- 폴더에서 터미널을 열어 아래의 코드를 현재 파이썬 버전으로 바꿔 사용하시면 됩니다.
- GPT API키가 필요하지 않습니다! 내장 코드로 돌아가니 편하게 사용하실 수 있습니다.

```
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
git clone https://github.com/njm0333/FinGPT_AI-Asset-Manager.git
cd FinGPT_AI-Asset-Manager
py -3.14 -m venv venv
.\venv\Scripts\activate
py -3.14 -m pip install --upgrade pip
py -3.14 -m pip install -r requirements.txt
py -3.14 main.py
```


## 사용법

<img width="2223" height="1475" alt="image" src="https://github.com/user-attachments/assets/92dcd009-2499-4fc2-958b-8baad970fcba" />
1. 시작 버튼을 누르면 프로그램 소개글이 천천히 생겨나며, 다음으로 넘어가기 버튼이 생깁니다.

<img width="2254" height="1672" alt="image" src="https://github.com/user-attachments/assets/c69dda8c-7c7e-4d38-b3f6-8db6381a988b" />
2. 7가지 설문에 응답하면

<img width="2254" height="1672" alt="image" src="https://github.com/user-attachments/assets/1d447d51-79c3-489a-94af-1fc184cdefcf" />
3. 설문자의 투자 성향을 계산하여 간략히 보여줍니다

<img width="2254" height="1672" alt="image" src="https://github.com/user-attachments/assets/a232b70c-ac71-45f8-8648-3aa4a886a7a1" />
4. 현재 포트폴리오를 분석할 수 있습니다

  - 현재 보유하고 있는 주식/ETF 종목들의 티커를 넣으면 작동합니다(티커는 한/미 주식 둘 다 가능합니다!)

  - 각 종목의 비중을 소수점 단위로 넣고
    
  - 투자 성향을 고르면 분석이 시작됩니다

<img width="2254" height="1672" alt="image" src="https://github.com/user-attachments/assets/18816aa5-d9f2-47f5-ace7-48dc1a4264a7" />
5. 용어가 어렵다면 설명창이 있습니다

<img width="2254" height="1672" alt="image" src="https://github.com/user-attachments/assets/bf631bea-2b8b-4e16-bdf0-eea358aedf02" />
6. 분석이 완료된 후 모습입니다

<img width="2254" height="1672" alt="image" src="https://github.com/user-attachments/assets/2d788f99-b242-429d-8ca3-b27fbde6a496" />
7. 완료한 분석에 대한 보고서를 볼 수 있습니다.



## 전체 기능 및 구현 설명 _ for dev

### windows/survey_window.py
<img width="1035" height="1215" alt="image" src="https://github.com/user-attachments/assets/00d2a22e-48db-4322-badf-feabed2238cd" />
windows/survey_window.py입니다. 레퍼런스의 금융권 성향 테스트 리스트를 차용했고, 해당 코드의 10번째 줄부터 31번째 줄까지 질문에 대한 점수표와 성향에 대한 설명이 적혀 있습니다. 총 5개의 성향으로 구분되고 그 성향들은 다음과 같습니다

```
"안정형": "예금이나 적금 수준의 수익률을 기대하며, 투자원금에 손실이 발생하는 것을 원하지 않는다. "
           "원금 손실의 우려가 없는 상품에 투자하는 데 바람직하다.",
"안정추구형": "투자원금의 손실 위험은 최소화하고, 이자·배당 등 안정적인 수익을 목표로 한다. "
         "다만 수익을 위해 단기적인 손실을 수용할 수 있으며 일부를 변동성 높은 상품에도 투자할 수 있다. "
         "채권형 금융상품이 적당하다.",
"위험중립형": "투자에는 그에 따른 위험이 있다는 것을 인식하고 있으며, 예·적금보다 높은 수익을 기대한다면 "
         "일정 수준의 손실 위험을 감수할 수 있다. 적립식펀드나 주식연동형 등 중위험·중수익 펀드가 적당하다.",
"적극투자형": "원금 보전보다 높은 수준의 수익을 추구하는 편이다. 투자자금의 상당 부분을 주식, 주식형 펀드, "
         "파생상품 등 위험자산에 투자할 의향이 있다. 해외·국내 주식형펀드나 비보장형 ELS도 고려할 수 있다.",
"공격투자형": "시장평균수익률보다 크게 높은 수익을 목표로 하며, 큰 손실 위험도 적극 수용한다. "
         "투자자금 대부분을 주식, 주식형 펀드, 파생상품 등 고위험 자산에 투자할 의향이 있다. "
         "주식 비중 70% 이상 펀드가 적당하다."
```

필요시 질문의 종류와 개수, 각 질문의 점수를 조정할 수 있습니다.


### windows/pca_window.py
PCA 알고리즘을 구현한 코드입니다

<img width="940" height="1318" alt="image" src="https://github.com/user-attachments/assets/f94f268e-8c58-4d97-a999-63109a96afaf" />

1. 가격 데이터 수집 & 수익률 전처리 (fetch_price_data, prepare_returns)

yfinance.download로 여러 티커의 Adj Close를 받아온 뒤,
MultiIndex 컬럼/Series 케이스를 전부 처리해서 하나의 DataFrame으로 정규화합니다.

이후 pct_change()로 일간 수익률을 만든 다음,
행·열 기준으로 유효 데이터가 95% 미만인 구간을 드롭해서
“구멍이 너무 많은 종목/기간”은 자동으로 필터링합니다.

유효 종목이 2개 미만이면 바로 ValueError를 던져서
PCA가 의미 없는 상황을 초기에 차단합니다.

---

<img width="891" height="1315" alt="image" src="https://github.com/user-attachments/assets/82be9bf6-feb4-420e-9d48-1af202c12b7f" />

2. 공분산 기반 PCA 요인 포트폴리오 (run_pca)

먼저 수익률에 대해
2.5%~97.5% 구간 winsorization을 적용해 양 극단의 이상치를 잘라냅니다.
그 뒤 각 종목별로 z-score 정규화((r - mean)/std)를 한 번,
sklearn.preprocessing.scale로 전체를 한 번 더 스케일링합니다.

이렇게 정규화된 수익률로 공분산 행렬을 만들고,
공분산 행렬 위에 PCA를 수행해서 components_를 가져옵니다.

이 컴포넌트를 그대로 쓰지 않고,
각 요인별 weight 합이 1이 되도록 정규화해서 **“eigen-portfolio(요인별 가상의 펀드 포트폴리오)”**로 해석합니다.

동시에, 각 요인 포트폴리오의 일간 수익률(factor_returns)과
동일 비중 시장 수익률(market_returns)도 함께 계산해서
팩터 vs 시장 성과를 직접 비교할 수 있게 만들어 둡니다.

---
<img width="888" height="560" alt="image" src="https://github.com/user-attachments/assets/3de7b617-5cd0-47a5-bb1e-f99f116ca425" />
<img width="792" height="1421" alt="image" src="https://github.com/user-attachments/assets/c3246888-6699-413a-afc4-27763ea874a1" />

3. 투자 성향 기반 요인 타깃 & 쏠림 진단 (get_risk_profile_targets, analyze_portfolio)

get_risk_profile_targets(profile, n_factors)에서
각 투자 성향(안정형~공격투자형)에 대해 요인별 목표 비중 벡터를 미리 정의해 두고,
실제 요인 개수에 맞게 자르거나 0.05씩 채운 뒤 합=1로 정규화합니다.

analyze_portfolio에서는

사용자가 입력한 종목 비중을 eigen 포트폴리오에 투영해
실제 요인 노출도 exposures를 계산하고,

절댓값 기준으로 정규화해 현재 요인 비중을 만들고,

투자 성향별 목표 비중 target_exposures와 비교해서
+10%p 이상이면 과투자 요인, -10%p 이하면 과소투자 요인으로 분류합니다.

과투자 요인에 대해서는
해당 요인의 factor loading이 크고, 실제 포트폴리오 비중도 있는 종목을 골라
Trim 후보(비중 줄이기) 리스트를 만들고,
과소투자 요인에 대해서는 factor loading만 보고
Add 후보(비중 늘리거나 편입 고려) 종목을 상위 5개까지 뽑습니다.

마지막으로 최근 120거래일 기준으로
각 요인 포트폴리오의 **누적 수익률(팩터 모멘텀)**을 계산해서,
“쏠림은 있는데 성과가 좋은 요인인지/안 좋은 요인인지”를
한 번에 보도록 summary_text로 정리합니다.

4. 해당 기능을 테스트 해보기 위해 좋은 데이터 집합입니다
```
AAPL, MSFT, NVDA, AMD, TSLA, GOOGL, AMZN, META, NFLX, QQQ
0.25, 0.20, 0.15, 0.15, 0.10, 0.05, 0.05, 0.03, 0.01, 0.01
```

### function/PCA_Report.py

PCA 요인은 이름이 “Factor 1, Factor 2, …” 형태로만 존재하기 때문에, 보고서에서는 각 요인에 의미를 부여하는 보조 함수들을 사용합니다.

_factor_role_comment(factor_idx, factor_name, n_factors)
요인 번호별로 다음과 같이 단순화된 해석을 부여합니다.
1번: 시장 전체 방향, 2번: 스타일(성장/가치, 공격/방어), 3번: 방어주·업종, 4번 이후: 특정 테마·섹터.
Factor 이름 그대로를 쓰지 않고, 요인 번호 기반 휴리스틱으로 텍스트를 생성하는 구조입니다.

_factor_short_name(factor_idx)
같은 정보를 더 짧은 레이블(“시장 전체 방향 요인”, “성장/스타일 요인” 등)로 요약할 때 사용합니다.

**!!주의!! : 이 두 함수는 실제 PCA 결과와 완전히 1:1로 대응되는 것은 아닙니다. 비전문 사용자에게 직관적인 설명을 제공하기 위해 만들어진 규칙 기반 레이어입니다.**

_diff_comment(actual, target)
(actual - target)의 절대값을 기준으로 3%, 8%, 15%를 경계값으로 사용하여
“거의 비슷”, “약간 많/적음”, “다소 많/부족”, “상당히 많/부족”과 같은 문장을 반환합니다.

_momentum_comment(v)
최근 6개월 누적 수익률 v에 대해 여러 구간(>50%, >20%, >5%, >-5%, >-20%, 이하)을 나누어
“매우 강한 상승”, “비교적 좋은 상승”, “보합권”, “다소 부진”, “상당히 부진” 등의 표현을 반환합니다.




## 추가 개발예정 사항

- UI 업데이트
- Factor 기반 주식 추천
- 백테스트 기능 
- MDD 조회
- CAGR 그래프 비교

## Reference

### 📌 README 및 프로젝트 구조 참고
- Valiant-Searching-Code-Assistant  
  https://github.com/Sungtae124/Valiant-Searching-Code-Assistant

### 📌 투자 성향 진단 설계 참고
- 투자 성향 및 위험 성향 유형 정의 참고  
  https://invest_test.isweb.co.kr/#:~:text=%E2%91%A3%20%EC%A0%81%EA%B7%B9%ED%88%AC...

### 📌 PCA 기반 요인 분석 참고
- *Machine Learning for Algorithmic Trading*  
  https://www.amazon.com/Machine-Learning-Algorithmic-Trading-alternative/dp/1839217715

## License

MIT License

Copyright (c) 2025 NOH JEONG MIN

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.



