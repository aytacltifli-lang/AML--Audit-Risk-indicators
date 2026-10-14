import streamlit as st
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
import tempfile
import os

# Səhifənin tənzimlənməsi
st.set_page_config(page_title="Auditorlar Palatası - ƏL/TİMM Audit və Risk Sistemi", layout="wide", page_icon="🛡️")

# Müasir Glassmorphism və Qradient Dizayn (CSS)
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .main-header {
        font-size: 28px;
        color: #1E3A8A;
        font-weight: 800;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.05);
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.4);
        margin-bottom: 20px;
    }
    .card-success {
        background: rgba(209, 231, 221, 0.9);
        color: #0F5132;
        border-left: 6px solid #198754;
        padding: 20px;
        border-radius: 12px;
        margin-top: 15px;
    }
    .card-warning {
        background: rgba(255, 243, 205, 0.9);
        color: #664D03;
        border-left: 6px solid #FFC107;
        padding: 20px;
        border-radius: 12px;
        margin-top: 15px;
    }
    .card-danger {
        background: rgba(248, 215, 218, 0.9);
        color: #842029;
        border-left: 6px solid #DC3545;
        padding: 20px;
        border-radius: 12px;
        margin-top: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# YAN MENYU (SIDEBAR)
# ==========================================
st.sidebar.header("🏢 Təşkilat Məlumatları")
st.sidebar.markdown("Yoxlama aparılan subyektin parametrləri:")

teskilat_adi = st.sidebar.text_input("Auditor Təşkilatının Adı:", "Audit-Service MMC")
mesul_sexs = st.sidebar.text_input("Məsul Şəxs (Komplayens Ofisi):", "Ad Soyad")
yoxlama_tarixi = st.sidebar.date_input("Yoxlama Tarixi", datetime.now())

st.sidebar.divider()
st.sidebar.info("📌 **Sistem Statusu:** Aktiv\n\n✨ **Versiya:** 6.0 (PDF Export, Risk Matrix & Plotly)")

# Sessiya yaddaşı (State)
if 'dnp_faiz' not in st.session_state: st.session_state.dnp_faiz = 0.0
if 'dnp_bal' not in st.session_state: st.session_state.dnp_bal = 0.0
if 'risk_faiz' not in st.session_state: st.session_state.risk_faiz = 0.0
if 'risk_bal' not in st.session_state: st.session_state.risk_bal = 0.0
if 'meyar_cavablari' not in st.session_state: st.session_state.meyar_cavablari = {}
if 'audit_history' not in st.session_state: st.session_state.audit_history = []
if 'uploaded_evidences' not in st.session_state: st.session_state.uploaded_evidences = []

# Əsas Səhifə Başlığı
st.markdown("<p class='main-header'>🛡️ Auditorlar Palatası: ƏL/TİMM Peşəkar Audit və Risk Platforması</p>", unsafe_allow_html=True)
st.markdown(f"**Cari Yoxlama Subyekti:** `{teskilat_adi}` | **Məsul şəxs:** `{mesul_sexs}` | **Tarix:** `{yoxlama_tarixi}`")
st.divider()

# Naviqasiya Menusu (8 Tab)
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "📋 DNP Qiymətləndirmə", 
    "📊 Sahəvi Risk", 
    "🧮 Risk Matrisi",
    "🎯 Canlı Tərəzi & Radar", 
    "🤖 Tədbirlər Planı", 
    "📄 Rəsmi PDF Hesabat", 
    "📎 Sübut Sənədləri", 
    "📉 Tarixçə"
])

# ==========================================
# TAB 1: DNP MEYARLAR ÜZRƏ QİYMƏTLƏNDİRMƏ
# ==========================================
with tab1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.header("📋 Daxili Nəzarət Proqramının (DNP) Yoxlama Cədvəli")
    st.markdown("Hər bir meyar üzrə: **Bəli** (1 bal), **Qismən** (0.5 bal), **Xeyr** (0 bal) seçin.")

    meyarlar = {
        "1. Şübhəli əməliyyat hesabatı (ŞƏH) mexanizmi": 
            st.radio("1. Şübhəli əməliyyatlara göz yumulmaması:", ["Bəli", "Qismən", "Xeyr"], key="m1"),
        "2. ƏL/TİMM üzrə təlim proqramları": 
            st.radio("2. Təlim proqramlarının mövcudluğu:", ["Bəli", "Qismən", "Xeyr"], key="m2"),
        "3. İşçi heyətin təlimlərdə iştirakı": 
            st.radio("3. İşçi heyətin təlim iştirak səviyyəsi:", ["Bəli", "Qismən", "Xeyr"], key="m3"),
        "4. Risk səviyyəsinə uyğun komplayens": 
            st.radio("4. Daxili komplayens tədbirləri:", ["Bəli", "Qismən", "Xeyr"], key="m4"),
        "5. Daxili və ya kənar auditin keçirilməsi": 
            st.radio("5. Daxili/kənar auditin təşkili:", ["Bəli", "Qismən", "Xeyr"], key="m5"),
        "6. Məsul şəxsin və əvəzedicinin təyini": 
            st.radio("6. Məsul şəxsin rəsmi təyini:", ["Bəli", "Qismən", "Xeyr"], key="m6"),
        "7. Əməliyyatlara sərbəst çıxış imkanı": 
            st.radio("7. Məlumatlara sərbəst çıxış:", ["Bəli", "Qismən", "Xeyr"], key="m7"),
        "8. KPI və mükafatlandırma sistemi": 
            st.radio("8. Motivasiya və KPI mexanizmləri:", ["Bəli", "Qismən", "Xeyr"], key="m8"),
        "9. PEP (Siyasi nüfuzlu şəxslər) skriningi": 
            st.radio("9. PEP-lərin eyniləşdirilməsi:", ["Bəli", "Qismən", "Xeyr"], key="m9"),
        "10. Verifikasiya və yurisdiksiya riski": 
            st.radio("10. Müştəri uyğunluğu və verifikasiya:", ["Bəli", "Qismən", "Xeyr"], key="m10")
    }
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀 DNP Hesabatını Hesabla", type="primary"):
        st.session_state.meyar_cavablari = meyarlar
        bali_hesabla = 0
        for k, v in meyarlar.items():
            if v == "Bəli": bali_hesabla += 1.0
            elif v == "Qismən": bali_hesabla += 0.5
            else: bali_hesabla += 0.0

        max_ball = len(meyarlar) * 1.0
        faiz = (bali_hesabla / max_ball) * 100

        st.session_state.dnp_bal = bali_hesabla
        st.session_state.dnp_faiz = faiz

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📋 DNP Qiymətləndirmə Nəticəsi:")
        col_m1, col_m2 = st.columns(2)
        with col_m1: st.metric(label="Toplanan Bal", value=f"{bali_hesabla} / {max_ball}")
        with col_m2: st.metric(label="Uyğunluq Faiz Göstəricisi", value=f"{faiz:.1f}%")
        st.progress(int(faiz))

        if faiz >= 80:
            st.markdown(f'<div class="card-success"><h4>🟢 ADEKVATDIR (Aşağı risk)</h4><p><b>{teskilat_adi}</b> üzrə uyğunluq <b>{faiz:.1f}%</b>-dir.</p></div>', unsafe_allow_html=True)
        elif faiz >= 50:
            st.markdown(f'<div class="card-warning"><h4>🟡 ƏSAS ETİBARİLƏ ADEKVATDIR (Orta risk)</h4><p><b>{teskilat_adi}</b> üzrə uyğunluq <b>{faiz:.1f}%</b>-dir.</p></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="card-danger"><h4>🔴 ADEKVAT DEYİL (Yüksək risk)</h4><p><b>{teskilat_adi}</b> üzrə uyğunluq yalnız <b>{faiz:.1f}%</b>-dir.</p></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# TAB 2: SAHƏVİ RİSK HESABLANMASI
# ==========================================
with tab2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.header("📊 Auditor Təşkilatları üzrə Sahəvi Risk Metodologiyası")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔹 Daxili Amillər")
        dovriyyə = st.selectbox("1. İllik dövriyyə (Çəki: 25%):", ["< 50,000 AZN (1 bal)", "50,000-200,000 AZN (2 bal)", "> 200,000 AZN (4 bal)"])
        isci_sayi = st.selectbox("2. İşçilərin sayı (Çəki: 5%):", ["11-dən az (1 bal)", "11-25 işçi (2 bal)", "> 25 işçi (4 bal)"])
        muddet = st.selectbox("3. Fəaliyyət müddəti (Çəki: 10%):", ["> 10 il (1 bal)", "3-10 il (2 bal)", "< 3 il (4 bal)"])
        riskli_musteri = st.selectbox("4. Risqli müştəri faizi (Çəki: 20%):", ["< 10% riskli (1 bal)", "10%-30% riskli (2 bal)", "> 30% riskli (4 bal)"])
        xidmet = st.selectbox("5. Xidmətin təqdim edilməsi (Çəki: 30%):", ["Üzbəüz (1 bal)", "Vasitəçi ilə (2 bal)", "Distant / Onlayn (4 bal)"])
        cografiya = st.selectbox("6. Coğrafiyası (Çəki: 10%):", ["Kəndlər (1 bal)", "Rayon / Şəhər rayonu (2 bal)", "Respublika tabeli şəhər (4 bal)"])

    with col2:
        st.subheader("🔸 Nəzarət Amilləri")
        dnp_status = st.selectbox("1. DNP Statusu (Çəki: 25%):", ["Adekvatdır >80% (1 bal)", "Əsasən adekvat 50-80% (2 bal)", "Adekvat deyil <50% (4 bal)"])
        tapshiriq = st.selectbox("2. Tapşırıqların icrası (Çəki: 20%):", ["Tam tətbiq olunur (1 bal)", "Qismən tətbiq olunur (2 bal)", "İcra edilmir (4 bal)"])
        yoxlama_muddeti = st.selectbox("3. Son səyyar yoxlama (Çəki: 10%):", ["1-3 il əvvəl (1 bal)", "4-6 il əvvəl (2 bal)", "Heç keçirilməyib (4 bal)"])
        sorgular = st.selectbox("4. Sorğulara cavab (Çəki: 5%):", ["Tam cavab verilib (1 bal)", "Qismən cavab verilib (2 bal)", "Cavab verilməyib (4 bal)"])
        reytinq = st.selectbox("5. Nəticə reytinqi (Çəki: 10%):", ["Əhəmiyyətli pozuntu yoxdur (1 bal)", "Pozuntu aşkar edilib (2 bal)", "Əhəmiyyətli pozuntu var (4 bal)"])
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀 Ümumi Sahəvi Riski Hesabla", type="primary"):
        def get_score(text):
            if "1 bal" in text: return 1.0
            elif "2 bal" in text: return 2.0
            elif "4 bal" in text: return 4.0
            return 1.0

        d_score = (get_score(dovriyyə)*0.25 + get_score(isci_sayi)*0.05 + 
                   get_score(muddet)*0.10 + get_score(riskli_musteri)*0.20 + 
                   get_score(xidmet)*0.30 + get_score(cografiya)*0.10)

        n_score = (get_score(dnp_status)*0.25 + get_score(tapshiriq)*0.20 + 
                   get_score(yoxlama_muddeti)*0.10 + get_score(sorgular)*0.05 + 
                   get_score(reytinq)*0.10)

        total_risk_val = d_score + n_score
        nisbi_faiz = (total_risk_val / 8.00) * 100

        st.session_state.risk_bal = total_risk_val
        st.session_state.risk_faiz = nisbi_faiz

        history_entry = {
            "Tarix": str(yoxlama_tarixi),
            "Təşkilat": teskilat_adi,
            "DNP Faiz (%)": round(st.session_state.dnp_faiz, 1),
            "Risk Faiz (%)": round(nisbi_faiz, 1),
            "Ümumi Risk Balı": round(total_risk_val, 2)
        }
        if history_entry not in st.session_state.audit_history:
            st.session_state.audit_history.append(history_entry)

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📈 Sahəvi Risk Təhlili Nəticəsi:")
        col_r1, col_r2 = st.columns(2)
        with col_r1: st.metric(label="Ümumi Risk Balı", value=f"{total_risk_val:.2f} / 8.00")
        with col_r2: st.metric(label="Nisbi Risk Faiz Göstəricisi", value=f"{nisbi_faiz:.1f}%")
        st.progress(int(nisbi_faiz))

        if nisbi_faiz < 35:
            st.markdown(f'<div class="card-success"><h4>🟢 AŞAĞI RİSK QRUPU (<35%)</h4><p><b>{teskilat_adi}</b> üzrə standart monitorinq həyata keçirilir.</p></div>', unsafe_allow_html=True)
        elif nisbi_faiz <= 70:
            st.markdown(f'<div class="card-warning"><h4>🟡 ORTA RİSK QRUPU (35% - 70%)</h4><p><b>{teskilat_adi}</b> üzrə ən azı 2 ildən bir səyyar yoxlama olmalıdır.</p></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="card-danger"><h4>🔴 YÜKSƏK RİSK QRUPU (>70%)</h4><p><b>{teskilat_adi}</b> üzrə gücləndirilmiş nəzarət tədbirləri zəruridir!</p></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# TAB 3: RİSK MATRİSİ CƏDVƏLİ
# ==========================================
with tab3:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.header("🧮 ƏL/TİMM Risk Matrisi və Qiymətləndirmə Cədvəli")
    st.markdown("Auditorlar Palatasının metodologiyasına əsasən risk kateqoriyalarının qruplaşdırılması:")

    matrix_data = {
        "Risk Səviyyəsi": ["Aşağı Risk", "Orta Risk", "Yüksək Risk"],
        "Bal Diapazonu": ["< 35%", "35% - 70%", "> 70%"],
        "Nəzarət Dövriliyi": ["3 ildə ən azı 1 dəfə", "2 ildə ən azı 1 dəfə", "İl ərzində ən azı 1 dəfə"],
        "Tədbirlər": ["Standart monitorinq", "Planlı səyyar yoxlama", "Gücləndirilmiş nəzarət və xüsusi izləmə"]
    }
    df_matrix = pd.DataFrame(matrix_data)
    st.dataframe(df_matrix, use_container_width=True)

    st.info("💡 Matris subyektin topladığı ümumi nisbi risk faizinə əsasən onun hansı nəzarət qrupuna aid olduğunu müəyyən edir.")
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# TAB 4: CANLI GAUGE TƏRƏZİ & RADAR QRAFIKLƏR
# ==========================================
with tab4:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.header("🎯 Canlı Risk Tərəzisi (Gauge Chart) & Radar Analitika")
    st.markdown("Plotly əsaslı interaktiv və futuristik vizualizasiya paneli:")

    if st.session_state.dnp_faiz > 0 or st.session_state.risk_faiz > 0:
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.subheader("🏎️ Risk Sürət Tərəzisi (Gauge)")
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=st.session_state.risk_faiz,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Nisbi Risk Səviyyəsi (%)", 'font': {'size': 18}},
                delta={'reference': 50},
                gauge={
                    'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                    'bar': {'color': "#1E3A8A"},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 35], 'color': '#D1E7DD'},
                        {'range': [35, 70], 'color': '#FFF3CD'},
                        {'range': [70, 100], 'color': '#F8D7DA'}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 70
                    }
                }
            ))
            fig_gauge.update_layout(height=350, margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig_gauge, use_container_width=True)

        with col_g2:
            st.subheader("🕸️ Hörümçək Toru (Radar Qrafiki)")
            categories = ['DNP Uyğunluğu', 'Sahəvi Risklər', 'Nəzarət Mexanizmi', 'Komplayens', 'Audit Effektivliyi']
            values = [st.session_state.dnp_faiz, st.session_state.risk_faiz, 
                      max(0, 100 - st.session_state.risk_faiz), 
                      st.session_state.dnp_faiz * 0.9, 
                      (st.session_state.dnp_faiz + (100 - st.session_state.risk_faiz))/2]

            fig_radar = go.Figure(data=go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                marker_color='#1E3A8A'
            ))
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=False,
                height=350,
                margin=dict(l=30, r=30, t=50, b=30)
            )
            st.plotly_chart(fig_radar, use_container_width=True)
    else:
        st.warning("⚠️ Zəhmət olmasa əvvəlcə 'DNP Qiymətləndirmə' və 'Sahəvi Risk' bölmələrində hesablamaları icra edin.")
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# TAB 5: AVTOMATİK TÖVSİYƏ VƏ TƏDBİRLƏR PLANI
# ==========================================
with tab5:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.header("🤖 Avtomatik Tədbirlər Planı & Tövsiyələr Generatoru")
    st.markdown("Seçilmiş cavablara əsasən çatışmazlıqların aradan qaldırılması üçün rəsmi tövsiyələr paketi:")

    if st.session_state.meyar_cavablari:
        zəif_meyarlar = [k for k, v in st.session_state.meyar_cavablari.items() if v in ["Xeyr", "Qismən"]]
        
        if zəif_meyarlar:
            st.warning(f"⚠️ Diqqət! Aşağıdakı {len(zəif_meyarlar)} meyar üzrə çatışmazlıqlar aşkar edilmişdir:")
            for m in zəif_meyarlar:
                st.markdown(f"- **{m}**")
            
            st.divider()
            st.subheader("📋 Təklif Olunan Düzəldici Tədbirlər Planı (Action Plan):")
            
            action_plan_text = f"""==================================================
TƏDBİRLƏR PLANI VƏ KOMPLAYENS TÖVSİYƏLƏRİ
Təşkilat: {teskilat_adi}
Tarix: {yoxlama_tarixi}
==================================================
1. Aşkar edilmiş çatışmazlıqların 30 gün ərzində aradan qaldırılması üçün daxili əmr imzalanmalıdır.
2. Zəif qiymətləndirilmiş meyarlar üzrə (Xeyr/Qismən) məsul şəxslərə əlavə təlimlər keçirilməlidir.
3. Daxili nəzarət proqramının (DNP) müvafiq bəndləri yenidən işlənilərək Auditorlar Palatasına təqdim olunmalıdır.
==================================================
"""
            st.text_area("Generasiya edilmiş Tədbirlər Planı:", value=action_plan_text, height=200)
            st.download_button(
                label="📥 Tədbirlər Planını Yüklə",
                data=action_plan_text,
                file_name=f"Tedbirler_Plani_{teskilat_adi.replace(' ', '_')}.txt",
                mime="text/plain"
            )
        else:
            st.success("🎉 Əla! Bütün meyarlar üzrə nəticələr tam adekvatdır ('Bəli').")
    else:
        st.info("ℹ️ Zəhmət olmasa əvvəlcə 'DNP Qiymətləndirmə' tabında qiymətləndirməni tamamlayın.")
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# TAB 6: RƏSMİ PDF HESABAT İXRACI
# ==========================================
with tab6:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.header("📄 Rəsmi PDF Hesabatının İxracı")
    st.markdown("Audit nəticələrini peşəkar rəsmi **PDF** sənədi şəklində yükləyin.")

    if st.button("🛠️ Rəsmi PDF Sənədi Hazırla", type="primary"):
        class PDF(FPDF):
            def header(self):
                self.set_font('Arial', 'B', 14)
                self.cell(0, 10, 'AZERBAYCAN RESPUBLIKASI AUDITORLAR PALATASI', 0, 1, 'C')
                self.set_font('Arial', '', 11)
                self.cell(0, 8, 'AL/TIMM Audit ve Sahevi Risk Qiymetlendirme Hesabati', 0, 1, 'C')
                self.ln(5)

            def footer(self):
                self.set_y(-15)
                self.set_font('Arial', 'I', 8)
                self.cell(0, 10, f'Sehife {self.page_no()}', 0, 0, 'C')

        pdf = PDF()
        pdf.add_page()
        pdf.set_font('Arial', '', 11)

        pdf.cell(0, 8, f"Teshkilat: {teskilat_adi}", 0, 1)
        pdf.cell(0, 8, f"Mesul Sexs: {mesul_sexs}", 0, 1)
        pdf.cell(0, 8, f"Yoxlama Tarixi: {yoxlama_tarixi}", 0, 1)
        pdf.ln(5)

        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, "1. DNP Uygunluq Neticesi:", 0, 1)
        pdf.set_font('Arial', '', 11)
        pdf.cell(0, 8, f"- Toplanan Bal: {st.session_state.dnp_bal} / 10.0", 0, 1)
        pdf.cell(0, 8, f"- Uygunluq Faizi: {st.session_state.dnp_faiz:.1f}%", 0, 1)
        pdf.ln(5)

        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, "2. Sahevi Risk Neticesi:", 0, 1)
        pdf.set_font('Arial', '', 11)
        pdf.cell(0, 8, f"- Umumi Risk Bali: {st.session_state.risk_bal:.2f} / 8.00", 0, 1)
        pdf.cell(0, 8, f"- Nisbi Risk Faizi: {st.session_state.risk_faiz:.1f}%", 0, 1)
        pdf.ln(10)

        pdf.set_font('Arial', 'I', 10)
        pdf.cell(0, 8, "Bu sened Auditorlar Palatasinin elektron platformasinda avtomatik generate olunmusdur.", 0, 1, 'C')

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            pdf.output(tmp_file.name)
            tmp_path = tmp_file.name

        with open(tmp_path, "rb") as f:
            pdf_bytes = f.read()

        st.success("✅ Rəsmi PDF Hesabatı uğurla hazırdır!")
        st.download_button(
            label="📥 PDF Hesabatını Yüklə",
            data=pdf_bytes,
            file_name=f"AML_Audit_Hesabati_{teskilat_adi.replace(' ', '_')}.pdf",
            mime="application/pdf",
            type="primary"
        )
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# TAB 7: SÜBUT SƏNƏDLƏRİ (EVIDENCE UPLOAD)
# ==========================================
with tab7:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.header("📎 Sənəd Sübutlarının Yüklənməsi (Evidence Upload)")
    st.markdown("Auditor yoxlama zamanı təşkilatın təqdim etdiyi sənədləri buraya yükləyə bilər.")

    uploaded_file = st.file_uploader("Sübut faylını seçin (PDF, PNG, JPG, XLSX)", type=["pdf", "png", "jpg", "xlsx", "docx"])
    evidence_desc = st.text_input("Faylın aid olduğu meyar və ya qeyd:")

    if st.button("📤 Sübutu Yüklə və Qeydə Al", type="primary"):
        if uploaded_file is not None:
            file_info = {
                "Fayl adı": uploaded_file.name,
                "Açıqlama": evidence_desc if evidence_desc else "Qeyd göstərilməyib",
                "Tarix": str(datetime.now().strftime("%Y-%m-%d %H:%M"))
            }
            st.session_state.uploaded_evidences.append(file_info)
            st.success(f"✅ '{uploaded_file.name}' faylı uğurla sübut kimi əlavə olundu!")
            st.balloons()
        else:
            st.warning("⚠️ Zəhmət olmasa əvvəlcə bir fayl seçin.")

    if st.session_state.uploaded_evidences:
        st.divider("📋 Yüklənmiş Sübut Sənədlərinin Siyahısı:")
        df_ev = pd.DataFrame(st.session_state.uploaded_evidences)
        st.dataframe(df_ev, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# TAB 8: TARİXÇƏ VƏ TREND ANALİZİ
# ==========================================
with tab8:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.header("📉 Tarixçə və İllik Müqayisə (Audit Trail & Trend)")
    st.markdown("Keçmiş yoxlamalar və cari dövrün risk göstəricilərinin müqayisəli dinamikası:")

    if st.session_state.audit_history:
        df_history = pd.DataFrame(st.session_state.audit_history)
        st.dataframe(df_history, use_container_width=True)
        
        st.bar_chart(df_history.set_index("Tarix")["Risk Faiz (%)"])
        st.info("💡 **Trend İzahı:** Bu qrafik müxtəlif yoxlama tarixləri üzrə təşkilatın risk faizinin dəyişmə dinamikasını göstərir.")
    else:
        st.warning("⚠️ Hələ ki, tarixçəyə yazılmış yoxlama yoxdur. 'Sahəvi Risk' bölməsində hesablama apardıq नंतर məlumatlar burada əks olunacaq.")
    st.markdown('</div>', unsafe_allow_html=True)
