import streamlit as st
import xml.etree.ElementTree as ET
import base64
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="📈 XML 데이터 시각화", layout="centered")
st.title("📄 XML 실험 회차별 그래프 추출기")

xml_text = st.text_area("🔽 XML 전체 텍스트를 붙여넣으세요", height=400)

if xml_text.strip():
    try:
        root = ET.fromstring(xml_text.strip())
        series_list = root.findall(".//SeriesData")

        st.success(f"총 {len(series_list)}개의 SeriesData 블록이 감지되었습니다.")

        for idx, s in enumerate(series_list):
            try:
                title = s.findtext("Title") or "Unnamed"
                round_num = idx // 3 + 1  # 3개씩 묶기
                label = f"{round_num}회차: {title}"

                encoded = s.findtext("Data").strip()
                decoded = base64.b64decode(encoded)
                y_vals = np.frombuffer(decoded, dtype=np.float32)
                x_vals = np.arange(len(y_vals))

                max_val = np.max(y_vals)

                # Plot
                st.subheader(f"📊 {label}")
                fig, ax = plt.subplots()
                ax.plot(x_vals, y_vals, label=label, color="blue")
                ax.set_title(label)
                ax.set_xlabel("Index")
                ax.set_ylabel("Value")
                ax.grid(True)
                st.pyplot(fig)

                # Max
                st.markdown(f"**📌 최대값:** `{max_val:.4f}`")

                # Graph download
                buf = BytesIO()
                fig.savefig(buf, format="png")
                st.download_button(
                    label=f"🖼️ 그래프 다운로드 (PNG, {label})",
                    data=buf.getvalue(),
                    file_name=f"graph_{round_num}_{title}.png",
                    mime="image/png"
                )

                # CSV download
                df = pd.DataFrame({"Index": x_vals, "Value": y_vals})
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label=f"📥 CSV 다운로드 ({label})",
                    data=csv,
                    file_name=f"data_{round_num}_{title}.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.warning(f"⚠️ 그래프 {idx+1} 처리 중 오류: {e}")

    except Exception as e:
        st.error(f"❌ XML 파싱 실패: {e}")
