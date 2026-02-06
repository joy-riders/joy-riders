import streamlit as st
import pandas as pd
from API_Side import OilPrice
from DB_Side import DBLoader

# ---------------------------------------------------------
# 페이지 전체 세팅
# ---------------------------------------------------------
st.set_page_config(page_title="TCO Insight: 데이터로 설계하는 스마트 차량 관리 솔루션", page_icon="🚗", layout="wide")
st.markdown(
    """
    <style>
    /* 1. 사이트 전체 바깥 배경색 (눈이 편한 연회색) */
    .stApp {
        background-color: #F0F2F6;
    }

    /* 2. 80% 너비의 메인 콘텐츠 박스 설정 */
    .block-container {
        max-width: 80% !important;
        background-color: #FFFFFF; /* 안쪽은 흰색으로 대비를 줌 */
        padding: 3rem 5rem !important;
        margin-top: 2rem;
        margin-bottom: 2rem;
        border-radius: 15px; /* 모서리를 둥글게 해서 부드러운 느낌 */
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05); /* 은은한 그림자 */
    }

    /* 상단 헤더 영역 배경색 맞춤 */
    header[data-testid="stHeader"] {
        background-color: rgba(0,0,0,0);
    }

    .subheader-box {
        background-color: rgba(205, 228, 247, 0.5);
        border: 1px solid #D1D5DB;
        border-radius: 8px;
        padding: 0px 20px; /* 위아래 패딩을 0으로 잡고 높이로 조절 */

        display: flex;
        align-items: center;

        height: 70px;             /* min-height 대신 고정 height가 정렬 확인에 유리합니다 */
        margin-bottom: 35px;
    }

    .subheader-box-result {
        background-color: rgba(255, 221, 223, 0.5);
        border: 1px solid #D1D5DB;
        border-radius: 8px;
        padding: 0px 20px; /* 위아래 패딩을 0으로 잡고 높이로 조절 */

        display: flex;
        align-items: center;

        height: 70px;             /* min-height 대신 고정 height가 정렬 확인에 유리합니다 */
        margin-bottom: 15px;
    }

    .subheader-text {
        font-size: 25px !important;
        font-weight: 600;
        color: #31333F;

        /* 이 세 줄이 핵심입니다 */
        margin: 0 !important;     
        padding: 0 !important;
        line-height: 1 !important; /* 글자 줄 간격 때문에 생기는 미세 여백 제거 */

        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)


@st.cache_data
def get_maintenance_db(displacement, monthly_km):
    """DB 데이터 조회 및 교체주기 계산"""
    rows = DBLoader.sendquery(
        "SELECT part_name, cycle_km, price_tierA, price_tierB, price_tierC FROM tco_system.parts"
    )

    if isinstance(displacement, str) and (displacement.upper() == "NULL" or not displacement.isdigit()):
        cc = 0
    else:
        cc = int(displacement) if displacement else 0

    data = []
    for row in rows:
        name, cycle, tierA, tierB, tierC = row

        # 전기차(cc=0)나 경차는 Tier A 가격 적용
        if cc <= 1000:
            price = tierA
        elif cc <= 2000:
            price = tierB
        else:
            price = tierC

        remain_months = int(cycle / monthly_km) if monthly_km > 0 else 0

        data.append({
            "부품명": name,
            "부품가격(원)": price,
            "교체주기(km)": cycle,
            "예상 교체 시기": f"약 {remain_months}개월 후"
        })

    return pd.DataFrame(data)


# ---------------------------------------------------------
# 메인 UI - 사용자 input
# ---------------------------------------------------------
n1, n2 = st.columns([2, 8])

with n1:
    st.write(" ")
    st.image("logo.png", width=200)
with n2:
    st.markdown("# TCO Insight")
    st.markdown("### 데이터로 설계하는 스마트 차량 관리 솔루션")

st.write("")
st.divider()

# --- 세션 상태 초기화 (요청하신 변수명 적용) ---
if "in_oil" not in st.session_state:
    st.session_state["in_oil"] = None
    # [0]:차종명, [1]:제조사, [2]:연료, [3]:복합, [4]:도심, [5]:고속,
    # [6]:주행거리, [7]:연료비, [8]:등급, [9]:배기량, [10]:연도

if "in_price" not in st.session_state:
    st.session_state["in_price"] = ["미선택", 0, 0]
    # [0]:가격명, [1]:최저가, [2]:최고가

if "open_result" not in st.session_state:
    st.session_state["open_result"] = False

# [STEP 1] 차량 정보 입력
st.markdown(f"""
    <div class="subheader-box">
        <p class="subheader-text">차량 정보 입력</p>
    </div>
    """, unsafe_allow_html=True)

with st.container(border=True):
    c1, c2, c3 = st.columns([2, 1, 1])

    with c1:
        # st.session_state["model_name"] 자동 바인딩
        st.text_input("모델명", value="아반떼", key="model_name")

    with c2:
        # st.session_state["use_grade"], st.session_state["in_grade"] 자동 바인딩
        st.checkbox("등급 지정", value=False, key="use_grade")
        st.selectbox(
            "등급",
            ["1등급", "2등급", "3등급", "4등급", "5등급"],
            index=1,
            disabled=not st.session_state["use_grade"],
            key="in_grade"
        )

    with c3:
        # st.session_state["use_year"], st.session_state["in_year"] 자동 바인딩
        st.checkbox("연도 지정", value=False, key="use_year")
        st.text_input(
            "출시연도",
            value="2023",
            disabled=not st.session_state["use_year"],
            key="in_year"
        )

    search_button = st.button("🔍 차량 사양 조회", use_container_width=True)

    st.session_state["open_result"] = st.session_state["open_result"] or search_button

st.divider()

# ---------------------------------------------------------
# 연비 입력
# ---------------------------------------------------------
if not st.session_state["open_result"]:
    st.stop()

# 2. API 데이터 호출
# ApiCar 내부의 keys 리스트와 순서가 일치해야 합니다.
columns = [
    "모델명", "제조사", "연료", "표시효율", "도심효율",
    "고속도로효율", "1회충전주행거리", "예상연료비", "등급", "배기량", "연식"
]

default_value = "모델을 선택해주세요"
search_result = DBLoader.db_search("car_oil", st.session_state["model_name"])

# -----------------------------------------------------------------------------------------------------

if not search_result:
    st.warning(f"'{st.session_state['model_name']}'에 대한 검색 결과가 API에 존재하지 않습니다.")
    st.stop()  # 이후 코드 실행을 중단합니다.

# -----------------------------------------------------------------------------------------------------

# 3. 데이터 필터링 및 리스트 생성
filtered_data = []
for row in search_result:
    # row[8]이 '등급', row[10]이 '연식' (ApiCar 클래스의 keys 순서 기준)
    if st.session_state["use_grade"] and row[8] != st.session_state["in_grade"]:
        continue
    if st.session_state["use_year"] and str(row[10]) != st.session_state["in_year"]:
        continue

    filtered_data.append(row)

# 4. 표 출력 및 상세 선택
if filtered_data:
    # Pandas DataFrame으로 변환
    df = pd.DataFrame([r[:-1] for r in filtered_data], columns=columns)

    st.markdown(f"""
        <div class="subheader-box">
            <p class="subheader-text">'{st.session_state['model_name']}' 검색 결과</p>
        </div>
        """, unsafe_allow_html=True)

    # 전체 결과를 표로 먼저 보여주기
    st.dataframe(df, use_container_width=True)

    select_options = [default_value, *df["모델명"].unique()]

    # 셀렉트박스로 특정 모델 상세 선택
    selected_model = st.selectbox(
        "상세 정보를 확인할 모델을 선택하세요",
        select_options
    )

    if selected_model == default_value:
        st.stop()

    # 선택한 모델의 정보만 추출해서 보여주기
    detail_info = df[df["모델명"] == selected_model]
    for row in search_result:
        if row[0] == selected_model:
            st.session_state["in_oil"] = row
            break
    st.write(f"### 🔍 {selected_model} 상세 정보")
    st.table(detail_info)  # 혹은 st.json(detail_info.to_dict('records')[0])
else:
    st.warning("검색 결과가 없습니다. 필터 조건을 확인해주세요.")
    st.stop()

# ---------------------------------------------------------
# 가격 입력
# ---------------------------------------------------------
price_list = DBLoader.db_search("car_price", st.session_state["model_name"])

option_list = [default_value, ]
for row in price_list:
    option_list.append(row[0])

st.write("")
st.divider()
st.markdown(f"""
        <div class="subheader-box">
            <p class="subheader-text">가격 정보</p>
        </div>
        """, unsafe_allow_html=True)

if st.session_state["in_oil"][11] == None:
    # 3개씩 끊어서 가로로 배치 (Grid Layout)
    if price_list:
        # 0부터 리스트 길이까지 3씩 증가 (0, 3, 6 ...)
        for i in range(0, len(price_list), 3):
            row_items = price_list[i: i + 3]  # 데이터 3개 가져오기 (마지막엔 남은 것만)
            cols = st.columns(3)  # 화면을 3등분

            # 3등분한 컬럼에 데이터 하나씩 넣기
            for idx, row in enumerate(row_items):
                with cols[idx]:
                    with st.container(border=True):
                        # [사진] 상단에 배치
                        st.image(row[3], use_container_width=True)

                        # [모델명]
                        st.markdown(f"**{row[0]}**")
                        st.divider()

                        # [가격] 하단에 배치 (문자열을 숫자로 변환하여 쉼표 처리)
                        try:
                            p_min = int(row[1]) if row[1] else 0
                            p_max = int(row[2]) if row[2] else 0
                        except (ValueError, TypeError):
                            p_min, p_max = 0, 0

                        st.markdown(f"""
                                        <div style="
                                            margin-top: -15px; 
                                            margin-bottom: 25px;
                                            padding: 0 5px;
                                            font-size: 0.95rem;
                                        ">
                                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                                <span style="color: #666;">최저</span>
                                                <span style="color: #1E1E1E; font-weight: bold; font-size: 1.1rem;">{p_min:,} 만원</span>
                                            </div>
                                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                                <span style="color: #666;">최고</span>
                                                <span style="color: #1E1E1E; font-weight: bold; font-size: 1.1rem;">{p_max:,} 만원</span>
                                            </div>
                                        </div>
                                    """, unsafe_allow_html=True)

        st.caption("※ 위 가격은 선택 옵션 및 트림에 따라 달라질 수 있습니다.")

    # 사용자 선택
    selected_model = st.selectbox("당신의 차종을 골라주세요", option_list, key="in_price_selected")

    if selected_model == default_value:
        st.stop()

    for row in price_list:
        if row[0] == selected_model:
            st.session_state["in_price"] = row
            break

else:
    # 데이터를 가져옴
    row = DBLoader.sendquery(f"select * from car_price where model_name = '{st.session_state['in_oil'][11]}'")[0]

    # 좌우 여백을 주어 카드를 가운데로 모음 [비율: 1(여백) : 2(카드) : 1(여백)]
    empty1, center_col, empty2 = st.columns([1, 2, 1])

    with center_col:
        with st.container(border=True):
            # 이미지와 텍스트를 1:1로 배치
            col1, col2 = st.columns([1, 1])

            with col1:
                st.image(row[3], use_container_width=True)

            with col2:
                st.subheader(row[0])
                st.divider()

                # 가격 정보 (오른쪽 정렬 및 위아래 여백 확보)
                st.markdown(f"""
                        <div style="text-align: right; padding: 10px 0;">
                            <p style="color: gray; margin: 0; font-size: 0.9rem;">최저가</p>
                            <h3 style="margin: 0; color: #1E1E1E;">{int(row[1]):,} 만원</h3>
                            <div style="margin: 20px 0;"></div>
                            <p style="color: gray; margin: 0; font-size: 0.9rem;">최고가</p>
                            <h3 style="margin: 0; color: #1E1E1E;">{int(row[2]):,} 만원</h3>
                        </div>
                    """, unsafe_allow_html=True)

            st.caption("※ 위 가격은 선택 옵션 및 트림에 따라 달라질 수 있습니다.")

    # 세션 상태에 저장
    st.session_state["in_price"] = row

st.write("")
st.divider()

# ---------------------------------------------------------
# 주행 패턴 / 연비 선택
# ---------------------------------------------------------

in_oil = st.session_state["in_oil"]

# [STEP 2] 주행 패턴 및 연비 선택
st.write("")
st.markdown(f"""
    <div class="subheader-box">
        <p class="subheader-text">주행 환경 및 주행거리 설정</p>
    </div>
    """, unsafe_allow_html=True)
col_p1, col_p2 = st.columns([3, 7])

with col_p1:
    pattern = st.radio("주행 패턴", ["복합 주행", "도심 위주", "고속도로 위주"])
    monthly_km = st.number_input("월간 예상 주행거리(km)", value=1500, step=100)
    annual_km = monthly_km * 12

with col_p2:
    # 리스트 인덱스로 연비 접근
    eff_map = {
        "복합 주행": float(in_oil[3]),  # [3] 복합
        "도심 위주": float(in_oil[4]),  # [4] 도심
        "고속도로 위주": float(in_oil[5])  # [5] 고속
    }
    applied_eff = eff_map[pattern]
    st.info(
        f"선택하신 **{pattern}**에 따라 적용된 연비는 **{applied_eff} {"km/L" if st.session_state["in_oil"][2] != "전기" else "km/kWh"}** 입니다.")
    st.write(f"- 복합: {in_oil[3]} | 도심: {in_oil[4]} | 고속: {in_oil[5]}")

# [STEP 3] 정비 부품 설정
st.write("")
st.markdown(f"""
    <div class="subheader-box">
        <p class="subheader-text">정비 부품 및 소모품 설정</p>
    </div>
    """, unsafe_allow_html=True)

cc_val = in_oil[9]
fuel_type = in_oil[2]  # 연료 타입 가져오기

# 데이터 가져오기
df_filtered = get_maintenance_db(cc_val, monthly_km)

# 📌 [추가] 전기차일 경우 내연기관 전용 부품 삭제
if fuel_type == "전기":
    exclude_parts = ["엔진오일", "점화플러그", "타이밍벨트/체인", "미션오일"]
    df_filtered = df_filtered[~df_filtered["부품명"].isin(exclude_parts)]
    st.info("💡 전기차는 엔진 관련 소모품(엔진오일, 점화플러그 등)이 제외된 견적이 제공됩니다.")

edited_df = st.data_editor(
    df_filtered,
    hide_index=True,
    use_container_width=True,
    disabled=["부품명", "교체주기(km)", "예상 교체 시기"],
    column_config={
        "부품가격(원)": st.column_config.NumberColumn(format="%d 원"),
        "교체주기(km)": st.column_config.NumberColumn(format="%d km"),
        "예상 교체 시기": st.column_config.TextColumn("교체 예정(현재 기준)")
    }
)

# [STEP 4] 최종 결과 산출
if st.button("💰 월간/연간 운영비용 합산 결과 보기", type="primary", use_container_width=True):

    # --- 1. 유가 정보 가져오기 ---
    fuel_type = in_oil[2]  # [2] 연료 종류
    current_fuel_price = 0

    try:
        # 하이브리드나 PHEV는 보통 휘발유 가격을 기준으로 계산 (전기 충전비는 별도 복잡하므로 휘발유 연비에 통합 계산됨)
        if fuel_type == "전기":
            current_fuel_price = 347
        else:
            fuel_map = {
                "가솔린": "휘발유",
                "디젤": "경유",
                "LPG": "자동차용부탄가스",
                "전기+휘발유": "휘발유",
                "휘발유 하이브리드": "휘발유"
            }

            # 내 차 연료에 맞는 검색어 추출 (없으면 기본 휘발유)
            search_fuel = fuel_map.get(fuel_type, "휘발유")

            # OilPrice 모듈의 getdata 함수 호출 (인자 전달)
            current_fuel_price = OilPrice.getdata(search_fuel)

    except Exception as e:
        st.error(f"유가 서비스 연결 중 오류 발생: {e}")
        current_fuel_price = -1

    # 유가 예외 처리 (기본값 세팅)
    if current_fuel_price <= 0:
        if "휘발유" in fuel_type or "전기+휘발유" in fuel_type:
            current_fuel_price = 1650
        elif "경유" in fuel_type:
            current_fuel_price = 1500
        elif "전기" in fuel_type:
            current_fuel_price = 347
        else:
            current_fuel_price = 1000

    if fuel_type == "전기":
        st.info(f"⚡ 적용 단가: **전기** 기준 **{current_fuel_price}원/kWh** (환경부 평균)")
    else:
        st.info(f"⛽ 적용 유가: **{search_fuel}** 기준 **{current_fuel_price:,.0f}원/L** (오피넷 실시간)")

    # --- 2. 비용 계산 ---

    # A. 유류비 (PHEV 연비는 이미 전기+휘발유가 혼합된 복합 연비로 API에서 제공됨)
    annual_fuel = (annual_km / applied_eff) * current_fuel_price

    # B. 자동차세 (전기차만 고정, 하이브리드/PHEV는 배기량 기준)
    if fuel_type == '전기':
        annual_tax = 130000
    else:
        cc_text = in_oil[9]
        cc = int(cc_text) if cc_text and str(cc_text).isdigit() else 0

        if cc <= 1000:
            rate = 80
        elif cc <= 1600:
            rate = 140
        else:
            rate = 200
        annual_tax = int((cc * rate) * 1.3)

    # C. 정비비
    annual_maint = sum((annual_km / row['교체주기(km)']) * row['부품가격(원)'] for _, row in edited_df.iterrows())

    # D. 합산
    total_annual = annual_fuel + annual_tax + annual_maint
    total_monthly = total_annual / 12

    # ----------------------------------------------------------------
    # 📌 차량 정보 및 가격 요약 (하이브리드/PHEV 대응)
    # ----------------------------------------------------------------
    st.divider()
    st.markdown(f"""
        <div class="subheader-box-result">
            <p class="subheader-text">📋 최종 견적 요약</p>
        </div>
        """, unsafe_allow_html=True)

    with st.container(border=True):
        info_c1, info_c2, info_c3, info_c4 = st.columns(4)

        with info_c1:
            st.caption("차량 모델")
            st.markdown(f"**{in_oil[0]}**")

        with info_c2:
            st.caption("상세 스펙")
            st.markdown(f"{in_oil[10]}년식 / {in_oil[2]}")

        with info_c3:
            # 연료 종류에 따른 맞춤형 정보 표시
            if fuel_type == "전기":
                st.caption("⚡ 1회 충전 주행거리")
                st.markdown(f"{in_oil[6]}km / {applied_eff}km/kWh")
            elif "전기+" in fuel_type or "하이브리드" in fuel_type:
                st.caption("🔋 EV 모드 / ⛽ 배기량")
                # PHEV인 경우 충전거리와 배기량을 동시에 표기
                range_val = in_oil[6] if in_oil[6] != "NULL" and in_oil[6] != 0 else "-"
                st.markdown(f"{range_val}km / {in_oil[9]}cc")
            else:
                st.caption("배기량 / 연비")
                st.markdown(f"{in_oil[9]}cc / {applied_eff}km/L")

        # 가격 정보 (in_price 변수 사용)
        with info_c4:
            st.caption("차량 가격")
            # 값이 없거나 0일 경우 예외 처리
            try:
                price_val_min = int(st.session_state["in_price"][1])
                price_val_max = int(st.session_state["in_price"][2])
                if price_val_min == 0:
                    p_text = "가격 미정"
                else:
                    p_max = f" ~ {price_val_max:,}" if price_val_max != 0 else ""
                    p_text = f"{price_val_min:,}{p_max} 만원"
            except:
                p_text = "가격 정보 없음"

            st.markdown(f"**{p_text}**")

    # ----------------------------------------------------------------
    # [비용 결과 출력]
    # ----------------------------------------------------------------
    st.write("")
    st.markdown(f"""
        <div class="subheader-box-result">
            <p class="subheader-text">💵 예상 운영 비용</p>
        </div>
        """, unsafe_allow_html=True)
    res_c1, res_c2 = st.columns(2)
    with res_c1:
        # 1. 메트릭 표시
        st.metric(label="🗓️ 월간 예상 비용", value=f"{int(total_monthly):,} 원")

        # 2. 강조 배지
        st.markdown(
            f"""
            <div style="
                display: inline-block;
                background-color: #e1f5fe; 
                color: #01579b; 
                padding: 4px 6px; 
                border-radius: 15px; 
                font-size: 0.85rem; 
                font-weight: bold;
                margin-top: -5px;
                margin-bottom: 30px;
                border: 1px solid #b3e5fc;">
                ✓ 유류비 + 세금 + 정비비 포함
            </div>
            """,
            unsafe_allow_html=True
        )
    res_c2.metric("🗓️ 연간 예상 비용", f"{int(total_annual):,} 원")

    # 상세 내역표
    st.table(pd.DataFrame({
        "항목": ["유류비 (실시간 유가 반영)", "자동차세 (배기량 기준)", "부품/정비비"],
        "연간 비용": [f"{int(annual_fuel):,}원", f"{int(annual_tax):,}원", f"{int(annual_maint):,}원"],
        "월간 환산": [f"{int(annual_fuel / 12):,}원", f"{int(annual_tax / 12):,}원", f"{int(annual_maint / 12):,}원"]
    }))

else:
    st.info("원하시는 옵션을 모두 선택했다면 결과 보기를 눌러주세요.")