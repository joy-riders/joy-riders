from DB_Side.DBLoader import dbloader

def sample():
    """소모품 10종 및 교환 주기"""
    return [
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

def target():
    rows = dbloader.sendquery(
        "SELECT name, default_cost, cycle_km, fuel_type FROM parts"
    )

    data = []
    for row in rows:
        data.append({
            "name": str(row[0]) if row[0] is not None else "",
            "default_cost": int(row[1]) if row[1] is not None else 0,
            "cycle_km": int(row[2]) if row[2] is not None else 0,
            "fuel_type": str(row[3]) if row[3] is not None else ""
        })

    return data

def normalize(data):
    return sorted(data, key=lambda x: x["name"])


print(sample())
print("========================================")
print(target())

# print("========================================")
if normalize(sample()) == normalize(target()):
    print("✅ 결과가 일치합니다.")
else:
    print("❌ 결과가 다릅니다.")