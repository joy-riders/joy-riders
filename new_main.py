import sys
import streamlit as st
import pandas as pd
from API_Side.oilprice import ApiOil
from DB_Side.DBLoader import dbloader

# ---------------------------------------------------------
# 페이지 전체 세팅
# ---------------------------------------------------------
st.set_page_config(page_title="차량 모델별 운영·관리 비용 계산 시스템", page_icon="🚗", layout="wide")

# ---------------------------------------------------------
# 사용자 input
# ---------------------------------------------------------
st.title("📊 차량 모델별 운영·관리 비용 계산 시스템")

# --- 세션 상태 초기화 (요청하신 변수명 적용) ---
if "in_oil" not in st.session_state:
    st.session_state["in_oil"] = None
    # [0]:차종명, [1]:제조사, [2]:연료, [3]:복합, [4]:도심, [5]:고속,
    # [6]:주행거리, [7]:연료비, [8]:등급, [9]:배기량, [10]:연도

if "in_price" not in st.session_state:
    st.session_state["in_price"] = ["미선택", 0, 0]
    # [0]:가격명, [1]:최저가, [2]:최고가

if "open_result" not in st.session_state:
    st.session_state["open_result"] = [False, False]

# [STEP 1] 차량 정보 입력
st.subheader("1️⃣ 차량 정보 입력")
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

    st.session_state["open_result"] = st.session_state["open_result"] or st.button("🔍 차량 사양 조회", use_container_width=True)

# ---------------------------------------------------------
# 연비 입력
# ---------------------------------------------------------
if not st.session_state["open_result"][0]:
    st.stop()

st.text("hello")

# ---------------------------------------------------------
# 가격 입력
# ---------------------------------------------------------
if not st.session_state["open_result"][1]:
    sys.exit()


# ---------------------------------------------------------
# 주행 패턴 / 연비 선택
# ---------------------------------------------------------
if not st.session_state["open_result"][2]:
        st.stop()

in_oil = []

# [STEP 2] 주행 패턴 및 연비 선택
st.write("")
st.subheader("2️⃣ 주행 환경 및 주행거리 설정")
col_p1, col_p2 = st.columns([1, 2])

with col_p1:
    pattern = st.radio("주행 패턴", ["복합 주행", "도심 위주", "고속도로 위주"])
    monthly_km = st.number_input("월간 예상 주행거리(km)", value=1500)
    annual_km = monthly_km * 12

with col_p2:
    # 리스트 인덱스로 연비 접근
    eff_map = {
            "복합 주행": float(in_oil[3]),  # [3] 복합
            "도심 위주": float(in_oil[4]),  # [4] 도심
            "고속도로 위주": float(in_oil[5])  # [5] 고속
    }
    applied_eff = eff_map[pattern]
    st.info(f"선택하신 **{pattern}**에 따라 적용된 연비는 **{applied_eff} km/L** 입니다.")
    st.write(f"- 복합: {in_oil[3]} | 도심: {in_oil[4]} | 고속: {in_oil[5]}")

st.stop()

# 차량 정보가 로드되었을 때만 실행 (in_oil이 존재할 때)
if st.session_state["in_oil"]:
    # 편의를 위해 로컬 변수로 리스트 가져오기
    in_oil = st.session_state["in_oil"]

    st.success(f"✅ 데이터 로드 완료: {in_oil[0]} ({in_oil[2]})")  # [0]:모델명, [2]:연료



    # [STEP 3] 정비 부품 설정
    st.write("")
    st.subheader("3️⃣ 정비 부품 및 소모품 설정")

    # [9] 배기량 정보 사용
    cc_val = in_oil[9]

    # 데이터 가져오기
    df_filtered = get_maintenance_db(cc_val, monthly_km)

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
    st.write("")
    if st.button("💰 월간/연간 운영비용 합산 결과 보기", type="primary", use_container_width=True):

        # --- 1. 유가 정보 가져오기 ---
        try:
            apioil = ApiOil()
            fuel_type = in_oil[2]  # [2] 연료 종류

            fuel_map = {"가솔린": "휘발유", "디젤": "경유", "LPG": "자동차용부탄가스"}
            search_fuel = fuel_map.get(fuel_type, fuel_type)
            current_fuel_price = apioil.getdata(search_fuel)

        except Exception as e:
            st.error(f"유가 서비스 연결 중 오류 발생: {e}")
            current_fuel_price = -1

        if current_fuel_price <= 0:
            if "휘발유" in fuel_type:
                current_fuel_price = 1650
            elif "경유" in fuel_type:
                current_fuel_price = 1500
            else:
                current_fuel_price = 1000

        # --- 2. 비용 계산 ---
        # A. 유류비
        annual_fuel = (annual_km / applied_eff) * current_fuel_price

        # B. 자동차세
        cc_text = in_oil[9]
        cc = int(cc_text) if cc_text and str(cc_text).isdigit() else 0

        if fuel_type == '전기':
            annual_tax = 130000
        else:
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
        # 📌 차량 정보 및 가격 요약
        # ----------------------------------------------------------------
        st.divider()
        st.markdown("### 📋 최종 견적 요약")

        # 깔끔한 카드 형태 디자인
        with st.container(border=True):
            info_c1, info_c2, info_c3, info_c4 = st.columns(4)

            # 모델명
            with info_c1:
                st.caption("차량 모델")
                st.markdown(f"**{in_oil[0]}**")  # [0] 차종명

            # 상세 스펙 (연식/연료)
            with info_c2:
                st.caption("상세 스펙")
                st.markdown(f"{in_oil[10]}년식 / {in_oil[2]}")  # [10] 연도, [2] 연료

            # 배기량 및 연비
            with info_c3:
                st.caption("배기량 / 연비")
                st.markdown(f"{in_oil[9]}cc / {applied_eff}km/L")

            # 가격 정보 (in_price 변수 사용)
            with info_c4:
                st.caption("차량 가격")
                # 값이 없거나 0일 경우 예외 처리
                try:
                    price_val = st.session_state["in_price"][1]
                    if price_val == 0:
                        p_text = "가격 미정"
                    else:
                        p_text = f"{price_val:,} 만원"
                except:
                    p_text = "가격 정보 없음"

                st.markdown(f"**{p_text}**")

        # ----------------------------------------------------------------
        # [비용 결과 출력]
        # ----------------------------------------------------------------
        st.write("")
        st.markdown("#### 💵 예상 운영 비용")
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
    st.info("상단에 차량 정보를 입력하고 '차량 사양 조회' 버튼을 눌러주세요.")