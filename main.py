import streamlit as st
import pandas as pd
import requests
import xml.etree.ElementTree as ET

# 1. 설정 및 API 정보
st.set_page_config(page_title="차량 모델별 운영·관리 비용 계산 시스템", page_icon="🚗", layout="wide")

ENERGY_API_KEY = 'Uhhs8hF9b7AmjW4N9NV3wfvFU67Rjcdw+hwr2UffYm4NAiAy32okNCSZSDBt2deDSRbAPenyi0QXvVnmpppQ0Q=='
OPINET_API_KEY = 'F260204142'


# ---------------------------------------------------------
# 2. 데이터 처리 함수
# ---------------------------------------------------------

@st.cache_data
def fetch_car_api(comp_nm, model_nm, grade, year):
    """에너지공단 API를 호출하여 차량 상세 정보를 가져옵니다."""
    url = "https://apis.data.go.kr/B553530/CAREFF/CAREFF_LIST"
    # 등급에서 '등급' 글자 제거 (API 사양에 맞춰 숫자만 추출 가능성 대비)
    grade_num = grade.replace("등급", "")

    params = {
        'serviceKey': ENERGY_API_KEY,
        'pageNo': '1',
        'numOfRows': '10',
        'COMP_NM': comp_nm,
        'MODEL_NM': model_nm,
        'GRADE': grade_num,
        'YEAR': year
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        # [참고] 실제로 만들어진 주소를 확인하고 싶다면 아래 주석을 풀어보세요.
        print(response.url)

        # 응답이 정상인지 확인
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            item = root.find(".//item")

            if item is not None:
                # API 결과에서 필요한 굵은 글씨 컬럼 추출
                return {
                    "FUEL_NM": item.findtext("FUEL_NM"),
                    "ENGINE_DISPLACEMENT": item.findtext("ENGINE_DISPLACEMENT"),
                    "URBAN_EFF": item.findtext("URBAN_EFF"),
                    "HIGHWAY_EFF": item.findtext("HIGHWAY_EFF"),
                    "DISPLAY_EFF": item.findtext("DISPLAY_EFF"),
                    "MODEL_NM": item.findtext("MODEL_NM"),
                    "COMP_NM": item.findtext("COMP_NM")
                }

        # API 호출 실패 시 테스트용 데이터 반환 (실습용)
        return {
            "FUEL_NM": "휘발유",
            "ENGINE_DISPLACEMENT": "1991",
            "URBAN_EFF": "10.9",
            "HIGHWAY_EFF": "14.4",
            "DISPLAY_EFF": "12.3",
            "MODEL_NM": model_nm,
            "COMP_NM": comp_nm
        }
    except Exception as e:
        st.error(f"API 호출 오류: {e}")
        return None


@st.cache_data
def get_maintenance_db():
    """소모품 10종 및 교환 주기"""
    data = [
        {"name": "엔진오일", "default_cost": 100000, "cycle_km": 5000, "fuel_type": "combustion"}, # 매 4~5천 km
        {"name": "점화플러그", "default_cost": 120000, "cycle_km": 30000, "fuel_type": "gasoline"}, # 매 3만 km
        {"name": "냉각수(부동액)", "default_cost": 70000, "cycle_km": 40000, "fuel_type": "all"}, # 매 2년 기준 거리 환산
        {"name": "타이밍벨트", "default_cost": 400000, "cycle_km": 60000, "fuel_type": "combustion"}, # 5~6만 km
        {"name": "브레이크 패드", "default_cost": 80000, "cycle_km": 30000, "fuel_type": "all"}, # 매 2~3만 km
        {"name": "브레이크 디스크", "default_cost": 200000, "cycle_km": 50000, "fuel_type": "all"}, # 매 4~5만 km
        {"name": "미션오일", "default_cost": 150000, "cycle_km": 30000, "fuel_type": "combustion"}, # 매 2~3만 km
        {"name": "타이어", "default_cost": 600000, "cycle_km": 50000, "fuel_type": "all"}, # 매 4~5만 km
        {"name": "배터리", "default_cost": 150000, "cycle_km": 60000, "fuel_type": "combustion"}, # 5~6만 km
        {"name": "쇼크업소버", "default_cost": 300000, "cycle_km": 80000, "fuel_type": "all"} # 이미지 리스트 기반
    ]
    return pd.DataFrame(data)


# ---------------------------------------------------------
# 3. 메인 UI
# ---------------------------------------------------------
st.title("📊 차량 모델별 운영·관리 비용 계산 시스템")

# [STEP 1] 차량 정보 입력 (API 호출용)
st.subheader("1️⃣ 차량 정보 입력 (API 조회)")
# 세션 상태 초기화 (결과 저장용)
if 'api_res' not in st.session_state:
    st.session_state.api_res = None

with st.container(border=True):
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        in_comp = st.text_input("업체명 (예: 벤츠)", "벤츠")
    with c2:
        in_model = st.text_input("모델명 (예: A220 Hatchback)", "A220 Hatchback")
    with c3:
        in_grade = st.selectbox("등급", ["1등급", "2등급", "3등급", "4등급", "5등급"], index=2)
    with c4:
        in_year = st.text_input("출시연도 (예: 2018)", "2018")

    # [수정 포인트] 차량 정보를 입력받고 버튼을 눌러야 API가 호출됩니다.
    if st.button("🔍 차량 사양 조회", use_container_width=True):
        with st.spinner('차량 정보를 불러오는 중...'):
            # 실제 fetch_car_api 함수 호출 (입력값 전달)
            result = fetch_car_api(in_comp, in_model, in_grade, in_year)
            if result:
                st.session_state.api_res = result
            else:
                st.error("해당 조건의 차량을 찾을 수 없습니다.")

# API 결과가 세션에 있을 때만 이후 단계(연비/정비 설정) 표시
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
        # API 결과값 중 굵은 글씨로 표기된 연비 정보만 매칭
        eff_map = {
            "복합 주행": float(api_res["DISPLAY_EFF"]),
            "도심 위주": float(api_res["URBAN_EFF"]),
            "고속도로 위주": float(api_res["HIGHWAY_EFF"])
        }
        applied_eff = eff_map[pattern]

        st.info(f"선택하신 **{pattern}**에 따라 적용된 연비는 **{applied_eff} km/L** 입니다.")
        st.write(f"- 복합: {api_res['DISPLAY_EFF']} | 도심: {api_res['URBAN_EFF']} | 고속: {api_res['HIGHWAY_EFF']}")

    # [STEP 3] 정비 부품 설정 (DB 기반)
    st.write("")
    st.subheader("3️⃣ 정비 부품 및 소모품 설정")
    df_maint = get_maintenance_db()

    # 연료 타입에 따른 필터링 (API의 FUEL_NM 활용)
    fuel_type = api_res['FUEL_NM']
    mask = df_maint.apply(lambda x: (x['fuel_type'] == 'all') or
                                    (x['fuel_type'] == 'combustion' and fuel_type != '전기') or
                                    (x['fuel_type'] == 'gasoline' and fuel_type == '휘발유') or
                                    (x['fuel_type'] == 'diesel' and fuel_type == '경유'), axis=1)

    df_filtered = df_maint[mask][['name', 'default_cost', 'cycle_km']]
    df_filtered.columns = ['부품명', '부품가격(원)', '교체주기(km)']

    edited_df = st.data_editor(df_filtered, hide_index=True, use_container_width=True, disabled=["부품명"])

    # [STEP 4] 최종 결과 산출
    st.write("")
    if st.button("💰 월간/연간 운영비용 합산 결과 보기", type="primary", use_container_width=True):
        # 1. 유류비
        fuel_price = 1650 if fuel_type == "휘발유" else 1500  # 오피넷 연동 가능
        annual_fuel = (annual_km / applied_eff) * fuel_price

        # 2. 자동차세 (API의 ENGINE_DISPLACEMENT 활용)
        @st.cache_data(ttl=3600)
        def get_realtime_fuel_prices():
            """오피넷 API 실시간 전국 평균 유가 호출"""
            url = f"https://www.opinet.co.kr/api/avgAllPrice.do?out=xml&code={OPINET_API_KEY}"
            prices = {'휘발유': 1650, '경유': 1500, 'LPG': 1000}
            try:
                response = requests.get(url, timeout=5)
                root = ET.fromstring(response.content)
                for oil in root.findall(".//oil"):
                    prod_nm = oil.find("PRODNM").text
                    price = float(oil.find("PRICE").text)
                    if "휘발유" in prod_nm and "고급" not in prod_nm:
                        prices['휘발유'] = price
                    elif "경유" in prod_nm:
                        prices['경유'] = price
            except:
                pass
            return prices

            cc = int(cc)
            # 이미지의 배기량 구간별 세율 적용
            if cc <= 1000:
                base_tax = cc * 80
            elif cc <= 1600:
                base_tax = cc * 140
            else:
                base_tax = cc * 200  # 1600cc 초과 구간

            # 자동차세 + 지방교육세(30%) 합산 금액 반환
            return int(base_tax * 1.3)

        # 3. 정비비
        annual_maint = sum((annual_km / row['교체주기(km)']) * row['부품가격(원)'] for _, row in edited_df.iterrows())

        # 최종 합산
        total_annual = annual_fuel + annual_tax + annual_maint
        total_monthly = total_annual / 12

        st.divider()
        res_c1, res_c2 = st.columns(2)
        res_c1.metric("🗓️ 월간 예상 운영 비용", f"{int(total_monthly):,} 원")
        res_c2.metric("🗓️ 연간 예상 운영 비용", f"{int(total_annual):,} 원")

        # 상세 내역표
        st.table(pd.DataFrame({
            "항목": ["유류비", "자동차세", "부품/정비비"],
            "연간": [f"{int(annual_fuel):,}원", f"{int(annual_tax):,}원", f"{int(annual_maint):,}원"],
            "월간": [f"{int(annual_fuel / 12):,}원", f"{int(annual_tax / 12):,}원", f"{int(annual_maint / 12):,}원"]
        }))

else:
    st.info("상단에 차량 정보를 입력하고 '차량 사양 조회' 버튼을 눌러주세요.")
