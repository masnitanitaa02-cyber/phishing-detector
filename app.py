import streamlit as st
import pandas as pd
import joblib
import json
import os

from feature_extractor import extract_features, FEATURE_COLS
from styles import CUSTOM_CSS

# ============================================================
# KONFIGURASI HALAMAN
# ============================================================
st.set_page_config(
    page_title="Phishing Shield — Random Forest Detector",
    page_icon="🛡️",
    layout="wide",
)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

MODEL_PATH = "model_rf.pkl"
METRICS_PATH = "metrics.json"

# ============================================================
# LOAD MODEL
# ============================================================
@st.cache_resource
def load_model():
    if not os.path.exists(MODEL_PATH):
        return None
    return joblib.load(MODEL_PATH)

@st.cache_data
def load_metrics():
    if not os.path.exists(METRICS_PATH):
        return None
    with open(METRICS_PATH, "r") as f:
        return json.load(f)

def predict_single(artifact: dict, url: str):
    model = artifact["model"]
    scaler = artifact["scaler"]
    feature_cols = artifact["feature_cols"]

    feats = extract_features(url)
    X = pd.DataFrame([feats])[feature_cols]
    X_scaled = scaler.transform(X)

    pred = model.predict(X_scaled)[0]
    proba = model.predict_proba(X_scaled)[0]
    return pred, proba[1], feats

def predict_batch(artifact: dict, df_urls: pd.DataFrame, url_col: str):
    model = artifact["model"]
    scaler = artifact["scaler"]
    feature_cols = artifact["feature_cols"]

    all_feats = [extract_features(str(u)) for u in df_urls[url_col]]
    X = pd.DataFrame(all_feats)[feature_cols]
    X_scaled = scaler.transform(X)

    preds = model.predict(X_scaled)
    probas = model.predict_proba(X_scaled)[:, 1]

    result = df_urls.copy()
    result["prediksi"] = ["Phishing" if p == 1 else "Legitimate" for p in preds]
    result["probabilitas_phishing"] = probas.round(4)
    return result

def render_confidence_bar(proba_phishing: float, is_phishing: bool):
    pct = proba_phishing * 100 if is_phishing else (1 - proba_phishing) * 100
    fill_class = "conf-fill-danger" if is_phishing else "conf-fill-safe"
    label = "Tingkat keyakinan phishing" if is_phishing else "Tingkat keyakinan aman"
    st.markdown(
        f"""
        <div class="conf-track">
            <div class="{fill_class}" style="width:{pct:.1f}%;"></div>
        </div>
        <div class="conf-label">
            <span>{label}</span>
            <span>{pct:.1f}%</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown(
        """
        <div style="padding: 8px 0 16px 0; text-align: center;">
            <div style="font-size: 48px; margin-bottom: 6px;">🛡️</div>
            <div style="font-family:'Inter',sans-serif; font-weight:800; font-size:20px; color:#1a2332; letter-spacing:-0.02em;">
                Phishing Shield
            </div>
            <div style="font-family:'JetBrains Mono',monospace; font-size:10px; color:#7a8aa5; letter-spacing:0.08em; background:#e8edff; padding:3px 14px; border-radius:20px; display:inline-block; margin-top:4px;">
                RANDOM FOREST
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    artifact = load_model()
    metrics = load_metrics()

    if artifact is None:
        st.error("⚠️ Model belum ditemukan.\nJalankan `train_model.py` dulu.")
    else:
        st.success("✅ Model siap digunakan")

    # ===== PERFORMANCE METRICS =====
    if metrics:
        st.markdown("---")
        st.markdown("### 📊 Performa Model")
        
        acc = metrics['accuracy'] * 100
        f1 = metrics['f1_score'] * 100
        prec = metrics['precision'] * 100
        rec = metrics['recall'] * 100
        
        st.markdown(
            f"""
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin: 4px 0 8px 0;">
                <div style="background: #f0f4ff; border-radius: 8px; padding: 8px 6px; text-align: center; border: 1px solid #e0e8f5;">
                    <div style="font-size: 14px; font-weight: 700; color: #1a2332;">{acc:.2f}%</div>
                    <div style="font-size: 9px; color: #7a8aa5; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em;">Accuracy</div>
                </div>
                <div style="background: #f0f4ff; border-radius: 8px; padding: 8px 6px; text-align: center; border: 1px solid #e0e8f5;">
                    <div style="font-size: 14px; font-weight: 700; color: #1a2332;">{f1:.2f}%</div>
                    <div style="font-size: 9px; color: #7a8aa5; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em;">F1-Score</div>
                </div>
                <div style="background: #f0f4ff; border-radius: 8px; padding: 8px 6px; text-align: center; border: 1px solid #e0e8f5;">
                    <div style="font-size: 14px; font-weight: 700; color: #1a2332;">{prec:.2f}%</div>
                    <div style="font-size: 9px; color: #7a8aa5; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em;">Precision</div>
                </div>
                <div style="background: #f0f4ff; border-radius: 8px; padding: 8px 6px; text-align: center; border: 1px solid #e0e8f5;">
                    <div style="font-size: 14px; font-weight: 700; color: #1a2332;">{rec:.2f}%</div>
                    <div style="font-size: 9px; color: #7a8aa5; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em;">Recall</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ===== MODE ANALISIS (3 MODE) =====
    st.markdown("---")
    st.markdown("### ⚡ Mode Analisis")
    
    mode = st.radio(
        "",
        ["🔗 Cek 1 URL", "📁 Upload CSV (batch)", "📊 Detail Model"],
        label_visibility="collapsed",
    )
    
    mode_descriptions = {
        "🔗 Cek 1 URL": "Analisis satu URL secara instan",
        "📁 Upload CSV (batch)": "Prediksi banyak URL sekaligus",
        "📊 Detail Model": "Lihat performa & fitur model"
    }
    st.caption(mode_descriptions.get(mode, ""))

# ============================================================
# HERO SECTION
# ============================================================
st.markdown(
    """
    <style>
    .hero-wrap {
        text-align: center;
        padding: 70px 30px;
        background: #f0f4ff;
        border-radius: 24px;
        margin: 10px 0;
        border: 1px solid #e0e8f5;
        box-shadow: 0 4px 20px rgba(0,0,0,0.04);
    }
    .hero-eyebrow {
        display: inline-block;
        font-size: 13px;
        color: #0d6efd;
        background: #ffffff;
        padding: 6px 22px;
        border-radius: 30px;
        letter-spacing: 1px;
        font-weight: 600;
        margin-bottom: 18px;
        border: 1px solid #dce3f0;
        box-shadow: 0 2px 8px rgba(13, 110, 253, 0.06);
    }
    .hero-title {
        font-size: 52px;
        font-weight: 700;
        color: #1a1a2e;
        line-height: 1.2;
    }
    .hero-title br {
        display: block;
        content: "";
        margin: 5px 0;
    }
    .hero-title br + * {
        color: #0d6efd;
        font-weight: 300;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-wrap">
        <div class="hero-eyebrow">⚡ Sistem Deteksi Phishing</div>
        <div class="hero-title">Stay safe, stay smart
        <br>cek link sebelum klik</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if artifact is None:
    st.warning(
        "⚠️ File `model_rf.pkl` tidak ditemukan di folder ini. "
        "Jalankan terminal: `python train_model.py` terlebih dahulu, lalu refresh halaman ini."
    )
    st.stop()

# ============================================================
# MODE 1: CEK 1 URL
# ============================================================
if mode == "🔗 Cek 1 URL":
    left, right = st.columns([3, 2])
    with left:
        st.markdown('<span class="section-label">Input URL</span>', unsafe_allow_html=True)
        url_input = st.text_input(
            "URL",
            placeholder="https://www.example.com/login",
            label_visibility="collapsed",
        )
        cek_btn = st.button("🔍  Analisis URL", type="primary")

    if cek_btn:
        if not url_input.strip():
            st.error("URL tidak boleh kosong.")
        else:
            with st.spinner("🔄 Mengekstrak fitur & menjalankan model..."):
                pred, proba_phishing, feats = predict_single(artifact, url_input)
            is_phishing = pred == 1

            st.markdown("<br>", unsafe_allow_html=True)
            res_col, feat_col = st.columns([2, 3])

            with res_col:
                if is_phishing:
                    st.markdown(
                        f"""
                        <div class="result-danger">
                            <div class="result-icon">⚠️</div>
                            <div class="result-label">TERDETEKSI PHISHING</div>
                            <div class="result-caption">{url_input}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"""
                        <div class="result-safe">
                            <div class="result-icon">✅</div>
                            <div class="result-label">WEBSITE LEGITIMATE</div>
                            <div class="result-caption">{url_input}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                render_confidence_bar(proba_phishing, is_phishing)

            with feat_col:
                st.markdown('<span class="section-label">Fitur yang Diekstrak</span>', unsafe_allow_html=True)
                feat_df = pd.DataFrame(list(feats.items()), columns=["Fitur", "Nilai"])
                st.dataframe(feat_df, use_container_width=True, height=320, hide_index=True)
    else:
        st.markdown(
            """
            <div class="cyber-card" style="text-align:center; color:#4a5a7a; padding:40px;">
                ✨ Masukkan URL di atas, lalu klik <b>Analisis URL</b> untuk melihat hasil klasifikasi.
            </div>
            """,
            unsafe_allow_html=True,
        )

# ============================================================
# MODE 2: UPLOAD CSV (BATCH)
# ============================================================
elif mode == "📁 Upload CSV (batch)":
    st.markdown('<span class="section-label">Upload Dataset</span>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "CSV", type=["csv"], label_visibility="collapsed"
    )

    if uploaded_file is not None:
        try:
            df_uploaded = pd.read_csv(uploaded_file)
        except Exception as e:
            st.error(f"❌ Gagal membaca file: {e}")
            st.stop()

        st.markdown('<span class="section-label">Preview Data</span>', unsafe_allow_html=True)
        st.dataframe(df_uploaded.head(), use_container_width=True)

        url_col = st.selectbox(
            "Pilih kolom yang berisi URL:",
            options=df_uploaded.columns.tolist(),
            index=0 if "url" not in df_uploaded.columns else df_uploaded.columns.get_loc("url"),
        )

        if st.button("🚀  Jalankan Prediksi Batch", type="primary"):
            with st.spinner(f"🔄 Memproses {len(df_uploaded)} URL..."):
                result_df = predict_batch(artifact, df_uploaded, url_col)

            n_phishing = int((result_df["prediksi"] == "Phishing").sum())
            n_legit = int((result_df["prediksi"] == "Legitimate").sum())

            st.markdown("<br>", unsafe_allow_html=True)
            m1, m2, m3 = st.columns(3)
            m1.metric("📊 Total URL", len(result_df))
            m2.metric("⚠️ Phishing", n_phishing)
            m3.metric("✅ Legitimate", n_legit)

            st.markdown('<span class="section-label">Hasil Prediksi</span>', unsafe_allow_html=True)
            st.dataframe(result_df, use_container_width=True)

            csv_result = result_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️  Download Hasil (CSV)",
                data=csv_result,
                file_name="hasil_prediksi_phishing.csv",
                mime="text/csv",
            )
    else:
        st.markdown(
            """
            <div class="cyber-card" style="text-align:center; color:#4a5a7a; padding:40px;">
                📂 Upload file CSV yang memiliki kolom berisi URL untuk memulai prediksi batch.
            </div>
            """,
            unsafe_allow_html=True,
        )

# ============================================================
# MODE 3: DETAIL MODEL
# ============================================================
elif mode == "📊 Detail Model":
    if metrics is None:
        st.warning("⚠️ File metrics.json tidak ditemukan.")
    else:
        st.markdown('<span class="section-label">Metrik Evaluasi (Data Uji 20%)</span>', unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("🎯 Accuracy", f"{metrics['accuracy']*100:.2f}%")
        m2.metric("📐 Precision", f"{metrics['precision']*100:.2f}%")
        m3.metric("📏 Recall", f"{metrics['recall']*100:.2f}%")
        m4.metric("⚖️ F1-Score", f"{metrics['f1_score']*100:.2f}%")

        st.markdown("<br>", unsafe_allow_html=True)
        col_cm, col_fi = st.columns(2)

        with col_cm:
            st.markdown('<span class="section-label">Confusion Matrix</span>', unsafe_allow_html=True)
            cm = metrics["confusion_matrix"]
            cm_df = pd.DataFrame(
                cm,
                index=["Aktual: Legitimate", "Aktual: Phishing"],
                columns=["Prediksi: Legitimate", "Prediksi: Phishing"],
            )
            st.dataframe(cm_df, use_container_width=True)

        with col_fi:
            st.markdown('<span class="section-label">Feature Importance (Top 10)</span>', unsafe_allow_html=True)
            fi_df = pd.DataFrame(metrics["feature_importance"][:10])
            st.bar_chart(fi_df.set_index("feature")["importance"], color="#4f7cff")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="cyber-card">
                <span class="section-label">Spesifikasi Model</span>
                <p style="color:#1a2332; margin:4px 0;"><b>🤖 Algoritma:</b> Random Forest Classifier</p>
                <p style="color:#1a2332; margin:4px 0;"><b>📊 Jumlah fitur:</b> 22 fitur numerik (URL, domain, konten)</p>
                <p style="color:#4a5a7a; margin:8px 0 0 0; font-family:'JetBrains Mono',monospace; font-size:12px; line-height:1.8; background:#f0f4ff; padding:12px 16px; border-radius:10px;">
                    {', '.join(FEATURE_COLS)}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ============================================================
# FOOTER
# ============================================================
st.markdown(
    """
    <div class="cyber-footer">
        <span>🛡️ Phishing Shield</span> — Implementasi Random Forest untuk Klasifikasi Website Phishing<br>
        Skripsi · Program Studi Teknik Informatika · Universitas Ibrahimy
    </div>
    """,
    unsafe_allow_html=True,
)