"""
Snowflake → data.json (심화 옵션)

키페어 받은 분만 사용. 시트를 거치지 않고 Snowflake에서 바로 조회합니다.
fetch_sheets.py 대신 이 파일을 쓰려면:
  1. requirements.txt에 snowflake-connector-python, cryptography 추가
  2. GitHub Secrets 2개 추가:
       - SF_USER          (데이터팀이 발급한 ID)
       - SF_PRIVATE_KEY   (.p8 파일 내용 통째로)
  3. sync.yml의 "python fetch_sheets.py" 줄을 "python fetch_snowflake.py"로 교체
  4. 아래 QUERY를 본인 미션에 맞게 수정

⚠️ 본인 환경에 맞게 바꿔야 하는 곳:
  - ACCOUNT (사내 공통, 보통 그대로)
  - WAREHOUSE / DATABASE / SCHEMA / ROLE — 본인 권한에 맞게
  - QUERY — 본인이 받아오고 싶은 데이터
"""

import os
import json
import snowflake.connector
from cryptography.hazmat.primitives import serialization


# === 사내 환경 정보 (코드에 하드코딩) ===
ACCOUNT = "gv28284.ap-northeast-2.aws"
WAREHOUSE = "DEV_WH"
DATABASE = "FNF"
SCHEMA = "CRM_MEMBER"
ROLE = "PU_PF"

# === 본인 미션에 맞게 쿼리 수정 ===
QUERY = """
SELECT
    BRAND,
    CHANNEL,
    PROMO_NAME,
    TO_VARCHAR(START_DATE, 'YYYY-MM-DD') AS START_DATE,
    TO_VARCHAR(END_DATE, 'YYYY-MM-DD') AS END_DATE,
    STATUS
FROM PROMOTION_PLAN
ORDER BY END_DATE
"""


def get_connection():
    """RSA 키페어 인증으로 Snowflake 연결"""
    private_key_pem = os.environ['SF_PRIVATE_KEY'].encode()
    p_key = serialization.load_pem_private_key(private_key_pem, password=None)
    pkb = p_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    return snowflake.connector.connect(
        user=os.environ['SF_USER'],
        private_key=pkb,
        account=ACCOUNT,
        warehouse=WAREHOUSE,
        database=DATABASE,
        schema=SCHEMA,
        role=ROLE,
    )


def fetch_data():
    print("🚀 Snowflake 데이터 가져오기 시작...")
    conn = get_connection()
    cur = conn.cursor(snowflake.connector.DictCursor)
    try:
        cur.execute(QUERY)
        rows = cur.fetchall()
        print(f"✅ {len(rows)}개 행 로드 완료")

        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(rows, f, ensure_ascii=False, indent=2, default=str)

        print("✅ data.json 저장 완료")
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    fetch_data()
