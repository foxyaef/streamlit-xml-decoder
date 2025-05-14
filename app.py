import streamlit as st
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import base64
import zlib
import io
import matplotlib.pyplot as plt

def decode_series_data(encoded):
    try:
        raw = base64.b64decode(encoded)
        decompressed = zlib.decompress(raw)
        return list(map(float, decompressed.decode("utf-8").split(",")))
    except Exception as e:
        return None

def parse_xml(xml_str):
    root = ET.fromstring(xml_str)
    data_series = []
    for series in root.findall(".//SeriesData"):
        title = series.findtext("Title") or "Unnamed"
        id_ = series.findtext("ID")
        encoded_data = series.findtext("Data")
        data = decode_series_data(encoded_data)
        if data:
            data_series.append({"title": title, "id": id_, "data": data})
    for series in root.findall(".//SeriesDataAutoIncr"):
        title = series.findtext("Title") or "Unnamed"
        id_ = series.findtext("ID")
        count = int(series.findtext("Count"))
        start = float(series.findtext("StartOffset"))
        step = float(series.findtext("Incr"))
        data = [start + i * step for i in range(count)]
        data_series.append({"title": title, "id": id_, "data": data})
    return data_series

def to_csv(data_dict):
    df = pd.DataFrame(data_dict)
    return df.to_csv(index=False).encode("utf-8")

st.title("📈 XML 데이터 시각화 (자기장 실험)")
uploaded = st.file_uploader("XML 파일을 업로드하세요", type="xml")

if uploaded:
    xml_bytes = uploaded.read().decode("utf-8")
    series_list = parse_xml(xml_bytes)

    data_dict = {}
    for s in series_list:
        key = f"{s['title']} ({s['id']})"
        data_dict[key] = s["data"]

    df = pd.DataFrame(data_dict)
    st.success("✅ 데이터 성공적으로 파싱됨")
    st.dataframe(df)

    # 그래프 출력
    st.subheader("📊 그래프 시각화")
    for col in df.columns[1:]:  # 첫 열은 X축으로 사용
        fig, ax = plt.subplots()
        ax.plot(df[df.columns[0]], df[col])
        ax.set_xlabel(df.columns[0])
        ax.set_ylabel(col)
        ax.set_title(f"{col} vs {df.columns[0]}")
        st.pyplot(fig)

    # 최대 전압 출력
    voltage_cols = [col for col in df.columns if "전압" in col]
    for col in voltage_cols:
        st.info(f"🔋 최대 전압 ({col}): {np.max(df[col]):.3f} V")

    # 다운로드
    st.download_button("📥 CSV로 다운로드", to_csv(data_dict), "decoded_data.csv", "text/csv")
