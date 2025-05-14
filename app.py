import streamlit as st
import xml.etree.ElementTree as ET
import base64
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="XML Data 그래프 도구", layout="centered")
st.title("📊 XML `<Data>` 시각화 & 다운로드 도구")

# XML 텍스트 입력
xml_text = st.text_area("📋 XML 전체 텍스트 입력", height=400)

if xml_text.strip():
    try:
        root = ET.fromstring(xml_text.strip())
        data_elements = root.findall(".//Data")

        st.success(f"총 {len(data_elements)}개의 <Data> 블록을 찾았습니다.")

        for idx, data_elem in enumerate(data_elements):
            base64_str = data_elem.text.strip()
            decoded = base64.b64decode(base64_str)
            y_vals = np.frombuffer(decoded, dtype=np.float32)
            x_vals = np.arange(len(y_vals)) * 0.04

            st.subheader(f"📈 그래프 {idx + 1}")
            fig, ax = plt.subplots()
            ax.plot(x_vals, y_vals, label="신호", color="blue")
            ax.set_xlabel("Time (s)")
            ax.set_ylabel("Amplitude")
            ax.set_title(f"Decoded Data {idx + 1}")
            ax.grid(True)
            st.pyplot(fig)

            # 그래프 PNG 다운로드
            buf = BytesIO()
            fig.savefig(buf, format="png")
            st.download_button(
                label=f"🖼️ 그래프 {idx+1} 이미지 다운로드 (PNG)",
                data=buf.getvalue(),
                file_name=f"graph_{idx+1}.png",
                mime="image/png"
            )

            # CSV 다운로드
            df = pd.DataFrame({"Time (s)": x_vals, "Value": y_vals})
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label=f"📥 그래프 {idx+1} CSV 다운로드",
                data=csv,
                file_name=f"data_{idx+1}.csv",
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"❌ XML 파싱 또는 디코딩 오류: {e}")
