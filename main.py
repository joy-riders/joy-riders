import streamlit as st
import pandas as pd
import requests
import xml.etree.ElementTree as ET
import os
from dotenv import load_dotenv
from API_Side.oilprice import ApiOil

# st.write("### 현재 코드 버전: v2 (업데이트 확인용)")
#
# if st.button("♻️ 시스템 초기화 (캐시 삭제)"):
#     st.cache_data.clear()
#     st.success("캐시가 삭제되었습니다. 다시 조회해 보세요!")

# 1. 설정 및 API 정보
st.set_page_config(page_title="차량 모델별 운영·관리 비용 계산 시스템", page_icon="🚗", layout="wide")

# .env 파일 로드
load_dotenv()

# 전역 변수로 API 키 설정
OPINET_API_KEY = os.getenv('OPINET_API_KEY')

# 키가 제대로 들어왔는지 콘솔이나 화면에 잠시 출력해봅니다 (확인 후 삭제)
if not OPINET_API_KEY:
    st.error("🚨 .env 파일에서 API 키를 읽어오지 못했습니다! 변수명을 확인하세요.")
st.write(OPINET_API_KEY)
# ---------------------------------------------------------
# 2. 데이터 처리 함수
# ---------------------------------------------------------

# @st.cache_data
def get_vehicle_info(comp_nm, model_nm, grade, year):
    """API 호출 실패 시 사용할 목업 데이터 리스트를 포함합니다."""

    # --- [MOCKUP DATA START] ---
    # 실제 API 응답 구조와 동일하게 GRADE와 YEAR 필드를 추가했습니다.
    mock_db = [
        {"MODEL_NM": "아반떼 1.6 가솔린", "FUEL_NM": "고급휘발유", "DISPLAY_EFF": "15.4", "URBAN_EFF": "13.8", "HIGHWAY_EFF": "17.7",
         "ENGINE_DISPLACEMENT": "1598"},
        {"MODEL_NM": "그랜저 2.5 가솔린", "FUEL_NM": "휘발유", "DISPLAY_EFF": "11.7", "URBAN_EFF": "10.1", "HIGHWAY_EFF": "14.5",
         "ENGINE_DISPLACEMENT": "2497"},
    ]
    # --- [MOCKUP DATA END] ---

    # url = "https://apis.data.go.kr/B553530/CAREFF/CAREFF_LIST"
    #
    # grade_num = grade.replace("등급", "")
    #
    # params = {
    #     'serviceKey': ENERGY_API_KEY,
    #     'pageNo': '1',
    #     'numOfRows': '10',
    #     'COMP_NM': comp_nm,
    #     'MODEL_NM': model_nm,
    #     'GRADE': grade_num,
    #     'YEAR': year
    # }
    #
    # try:
    #     response = requests.get(url, params=params, timeout=10)
    #
    #     if response.status_code == 200:
    #         root = ET.fromstring(response.content)
    #         item = root.find(".//item")
    #
    #         if item is not None:
    #             return {
    #                 "FUEL_NM": item.findtext("FUEL_NM"),
    #                 "ENGINE_DISPLACEMENT": item.findtext("ENGINE_DISPLACEMENT"),
    #                 "URBAN_EFF": item.findtext("URBAN_EFF"),
    #                 "HIGHWAY_EFF": item.findtext("HIGHWAY_EFF"),
    #                 "DISPLAY_EFF": item.findtext("DISPLAY_EFF"),
    #                 "MODEL_NM": item.findtext("MODEL_NM"),
    #                 "COMP_NM": item.findtext("COMP_NM"),
    #                 "GRADE": item.findtext("GRADE"),
    #                 "YEAR": item.findtext("YEAR")
    #             }
    # except:
    #     pass

    # # API 실패 시 목업 검색
    # search_query = model_nm.lower().replace(" ", "")
    # for data in mock_db:
    #     if search_query in data["MODEL_NM"].lower().replace(" ", ""):
    #         res = data.copy()
    #         res["GRADE"] = grade.replace("등급", "")
    #         res["YEAR"] = year
    #         return res
    #
    # # 매칭되는 목업조차 없다면 None을 반환 (전기차 잔상 방지 핵심)
    # return None

    # 입력한 글자가 포함된 차가 있는지 찾기
    for car in mock_db:
        if model_nm in car["MODEL_NM"]:
            return car

    # 아무것도 못 찾으면 에러 대신 None을 줍니다.
    return None

@st.cache_data
def get_maintenance_db():
    """소모품 10종 및 교환 주기"""
    data = [
        {"name": "엔진오일", "default_cost": 100000, "cycle_km": 5000, "fuel_type": "combustion"},
        {"name": "점화플러그", "default_cost": 120000, "cycle_km": 30000, "fuel_type": "gasoline"},
        {"name": "냉각수(부동액)", "default_cost": 70000, "cycle_km": 40000, "fuel_type": "all"},
        {"name": "타이밍벨트", "default_cost": 400000, "cycle_km": 60000, "fuel_type": "combustion"},
        {"name": "브레이크 패드", "default_cost": 80000, "cycle_km": 30000, "fuel_type": "all"},
        {"name": "브레이크 디스크", "default_cost": 200000, "cycle_km": 50000, "fuel_type": "all"},
        {"name": "미션오일", "default_cost": 150000, "cycle_km": 30000, "fuel_type": "combustion"},
        {"name": "타이어", "default_cost": 600000, "cycle_km": 50000, "fuel_type": "all"},
        {"name": "배터리", "default_cost": 150000, "cycle_km": 60000, "fuel_type": "combustion"},
        {"name": "쇼크업소버", "default_cost": 300000, "cycle_km": 80000, "fuel_type": "all"}
    ]
    return pd.DataFrame(data)


# ---------------------------------------------------------
# 3. 메인 UI
# ---------------------------------------------------------
st.title("📊 차량 모델별 운영·관리 비용 계산 시스템")

if 'api_res' not in st.session_state:
    st.session_state.api_res = None

# [STEP 1] 차량 정보 입력
st.subheader("1️⃣ 차량 정보 입력 (API 조회)")
with st.container(border=True):
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        in_comp = st.text_input("업체명", "현대")  # 예시 변경
    with c2:
        in_model = st.text_input("모델명", "아반떼")
    with c3:
        in_grade = st.selectbox("등급", ["1등급", "2등급", "3등급", "4등급", "5등급"], index=1)
    with c4:
        in_year = st.text_input("출시연도", "2023")

    if st.button("🔍 차량 사양 조회", use_container_width=True):
        # [핵심] 버튼 누르자마자 세션을 비우고 화면을 강제로 다시 그리게 함
        st.session_state.api_res = None

        with st.spinner('데이터를 찾는 중...'):
            result = get_vehicle_info(in_comp, in_model, in_grade, in_year)
            if result:
                st.session_state.api_res = result
                st.rerun()  # 데이터를 새로 가져왔으므로 페이지를 다시 그림
            else:
                st.error(f"❌ '{in_model}'에 대한 정보를 찾을 수 없습니다. (아반떼, 그랜저, 아이오닉5, A220 중 입력해보세요)")

if st.session_state.api_res:
    api_res = st.session_state.api_res
    st.success(f"✅ 데이터 로드 완료: {api_res['MODEL_NM']} ({api_res['FUEL_NM']})")

    # [STEP 2] 주행 패턴 및 연비 선택
    st.write("")
    st.subheader("2️⃣ 주행 환경 및 주행거리 설정")
    col_p1, col_p2 = st.columns([1, 2])

    with col_p1:
        pattern = st.radio("주행 패턴", ["복합 주행", "도심 위주", "고속도로 위주"])
        monthly_km = st.number_input("월간 예상 주행거리(km)", value=1500)
        annual_km = monthly_km * 12

    with col_p2:
        eff_map = {
            "복합 주행": float(api_res["DISPLAY_EFF"]),
            "도심 위주": float(api_res["URBAN_EFF"]),
            "고속도로 위주": float(api_res["HIGHWAY_EFF"])
        }
        applied_eff = eff_map[pattern]
        st.info(f"선택하신 **{pattern}**에 따라 적용된 연비는 **{applied_eff} km/L** 입니다.")
        st.write(f"- 복합: {api_res['DISPLAY_EFF']} | 도심: {api_res['URBAN_EFF']} | 고속: {api_res['HIGHWAY_EFF']}")

    # [STEP 3] 정비 부품 설정
    st.write("")
    st.subheader("3️⃣ 정비 부품 및 소모품 설정")
    df_maint = get_maintenance_db()
    fuel_type = api_res['FUEL_NM']

    mask = df_maint.apply(lambda x: (x['fuel_type'] == 'all') or
                                    (x['fuel_type'] == 'combustion' and fuel_type != '전기') or
                                    (x['fuel_type'] == 'gasoline' and fuel_type == '휘발유') or
                                    (x['fuel_type'] == 'diesel' and fuel_type == '경유'), axis=1)

    df_filtered = df_maint[mask][['name', 'default_cost', 'cycle_km']]
    df_filtered.columns = ['부품명', '부품가격(원)', '교체주기(km)']
    edited_df = st.data_editor(df_filtered, hide_index=True, use_container_width=True, disabled=["부품명"])

    # [STEP 4] 최종 결과 산출 (수정된 통합 로직)
    st.write("")
    if st.button("💰 월간/연간 운영비용 합산 결과 보기", type="primary", use_container_width=True):

        # 1. API 키를 전달하며 객체 생성
        try:
            apioil = ApiOil(OPINET_API_KEY)
            current_fuel_price = apioil.getdata(fuel_type)
        except Exception as e:
            current_fuel_price = -1

        # 유가 호출 실패 시 기본값 설정
        if current_fuel_price <= 0:
            current_fuel_price = 1650 if fuel_type == "휘발유" else 1500
            st.warning(f"⚠️ 유가 정보를 가져오지 못해 기본값({current_fuel_price:,}원)으로 계산합니다.")
        else:
            st.info(f"⛽ 실시간 **{fuel_type}** 유가 반영: **{current_fuel_price:,}원**")

        # 2. 유류비 계산
        annual_fuel = (annual_km / applied_eff) * current_fuel_price

        # 3. 자동차세 계산 (이미지 기준 세율 적용)
        cc_text = api_res.get('ENGINE_DISPLACEMENT', '0')
        cc = int(cc_text) if cc_text and cc_text.isdigit() else 0

        if fuel_type == '전기':
            annual_tax = 130000  # 이미지 기준 13만원
        else:
            # 이미지의 비영업용 세율 구간 적용
            if cc <= 1000:
                rate = 80
            elif cc <= 1600:
                rate = 140
            else:
                rate = 200
            # 자동차세 + 지방교육세(30%) 합산
            annual_tax = int((cc * rate) * 1.3)

        # 4. 정비비 계산
        annual_maint = sum((annual_km / row['교체주기(km)']) * row['부품가격(원)'] for _, row in edited_df.iterrows())

        # 최종 합산
        total_annual = annual_fuel + annual_tax + annual_maint
        total_monthly = total_annual / 12

        st.divider()
        res_c1, res_c2 = st.columns(2)
        res_c1.metric("🗓️ 월간 예상 운영 비용", f"{int(total_monthly):,} 원")
        res_c2.metric("🗓️ 연간 예상 운영 비용", f"{int(total_annual):,} 원")

        # 상세 내역표 출력
        st.table(pd.DataFrame({
            "항목": ["유류비 (실시간 유가 반영)", "자동차세 (배기량 기준)", "부품/정비비"],
            "연간 비용": [f"{int(annual_fuel):,}원", f"{int(annual_tax):,}원", f"{int(annual_maint):,}원"],
            "월간 환산": [f"{int(annual_fuel / 12):,}원", f"{int(annual_tax / 12):,}원", f"{int(annual_maint / 12):,}원"]
        }))

else:
    st.info("상단에 차량 정보를 입력하고 '차량 사양 조회' 버튼을 눌러주세요.")