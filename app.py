import streamlit as st
import base64
import zlib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

st.set_page_config(page_title="XML Data 디코더", layout="centered")
st.title("📊 XML <Data> 디코더")

# 입력창
raw_data = st.text_area("🔽 여기에 `<Data> ... </Data>` 내용만 붙여넣으세요", height=300)

if raw_data:
    # <Data> 태그 내부 값만 추출
    if "<Data>" in raw_data and "</Data>" in raw_data:
        start = raw_data.find("<Data>") + len("<Data>")
        end = raw_data.find("</Data>")
        encoded = raw_data[start:end].strip()
    else:
        encoded = raw_data.strip()

    # 디코딩 시도
    try:
        decoded_bytes = base64.b64decode(encoded)
        decompressed = zlib.decompress(decoded_bytes)
        decoded_text = decompressed.decode("utf-8")
        values = list(map(float, decoded_text.split(",")))

        st.success("✅ 디코딩 성공! 데이터 개수: {}".format(len(values)))

        # 그래프
        st.subheader("📈 그래프")
        fig, ax = plt.subplots()
        ax.plot(values, label="Decoded Signal")
        ax.set_xlabel("Index")
        ax.set_ylabel("Value")
        ax.set_title("Decoded Data Plot")
        st.pyplot(fig)

        # 최대 전압
        st.subheader("🔋 최대 전압")
        st.info(f"최대 전압: {max(values):.3f} V")

        # CSV 다운로드
        df = pd.DataFrame({"Decoded Data": values})
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 CSV 다운로드", csv, "decoded_data.csv", "text/csv")

    except Exception as e:
        st.error(f"❌ 디코딩 실패: {e}")
