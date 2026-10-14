import streamlit as st
from datetime import datetime
import pandas as pd

# Səhifənin tənzimlənməsi
st.set_page_config(page_title="Auditorlar Palatası - ƏL/TİMM Audit və Risk Sistemi", layout="wide")

# Xüsusi Dizayn və Rəngləndirmə (CSS Stylləri)
st.markdown("""
    <style>
    .main-header {
        font-size: 26px;
        color: #1E3A8A;
        font-weight: bold;
    }
    .card-success {
        padding: 20px;
        border-radius: 10px;
        background-color: #D1E7DD;
        color: #0F5132;
        border-left: 6px solid #198754;
    }
    .card-warning {
        padding: 20px;
        border-radius: 10px;
        background-color: #FFF3CD;
        color: #664D03;
        border-left: 6px solid #FFC107;
    }
    .card-danger {
        padding: 20px;
        border-radius: 10px;
        background-color: #F8D7DA;
        color: #842029;
        border-left: 6px solid #DC3545;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# YAN MENYU (SIDEBAR) - KORPORATİV PANEL
# ==========================================
st.sidebar.header("🏢 Təşkilat Məlumatları")
st.sidebar.markdown("Yoxlama aparılan subyektin məlumatları:")

teskilat_adi = st.sidebar.text_input("Auditor Təşkilatının Adı:", "Audit-Service MMC")
mesul_sexs = st.sidebar.text_input("Məsul Şəxs (Komplayens Ofisi):", "Ad Soyad")
yoxlama_tarixi = st.sidebar.date_input("Yoxlama Tarixi", datetime.now())

st.sidebar.divider()
st.sidebar.info("📌 **Sistem Statusu:** Aktiv\n\n✨ **Versiya:** 4.0 (Risk Matrisi, Sübutlar & Trend Analizi)")

# Sessiya yaddaşı (State)
if 'dnp_faiz' not in st.session_state: st.session_state.dnp_faiz = 0.0
if 'dnp_bal' not in st.session_state: st.session_state.dnp_bal = 0.0
if 'risk_faiz' not in st.session_state: st.session_state.risk_faiz = 0.0
if 'risk_bal' not in st.session_state: st.session_state.risk_bal = 0.0
if 'audit_history' not in st.session_state: st.session_state.audit_history = []
if 'uploaded_evidences' not in st.session_state: st.session_state.uploaded_evidences = []

# Əsas Səhifə Başlığı
st.markdown("<p class='main-header'>🛡️ Auditorlar Palatası: ƏL/TİMM Daxili Nəzarət və Sahəvi Risk Sistemi</p>", unsafe_allow_html=True)
st.markdown(f"**Cari Yoxlama Subyekti:** `{teskilat_adi}` | **Məsul şəxs:** `{mesul_sexs}` | **Tarix:** `{yoxlama_tarixi}`")
st.divider()

# Naviqasiya Menusu (6 Tab)
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📋 DNP Qiymətləndirmə", 
    "📊 Sahəvi Risk", 
    "📈 Qrafik və Risk Matrisi", 
    "📥 Hesabatı Yüklə", 
    "📎 Sübut Sənədləri", 
    "📉 Tarixçə və Trend"
])

# ==========================================
# TAB 1: DNP 29 MEYAR ÜZRƏ QİYMƏTLƏNDİRMƏ
# ==========================================
with tab1:
    st.header("📋 Daxili Nəzarət Proqramının (DNP) Yoxlama Cədvəli")
    st.markdown("Hər bir meyar üzrə: **Bəli** (1 bal), **Qismən** (0.5 bal), **Xeyr** (0 bal) seçin.")

    with st.expander("ℹ️ Meyarlar üzrə ətraflı təlimat və izahat üçün klikləyin"):
        st.write("Bu bölmədə daxili nəzarət proqramının effektivliyini ölçən əsas meyarlar təqdim olunub.")

    meyarlar = {
        "1. Şübhəli əməliyyat hesabatı (ŞƏH) mexanizmi": 
            st.radio("1. Şübhəli əməliyyatlara göz yumulmaması:", ["Bəli", "Qismən", "Xeyr"], key="m1"),
        "2. ƏL/TMM üzrə təlim proqramları": 
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

    if st.button("🚀 DNP Hesabatını Hesabla", type="primary"):
        bali_hesabla = 0
        for k, v in meyarlar.items():
            if v == "Bəli": bali_hesabla += 1.0
            elif v == "Qismən": bali_hesabla += 0.5
            else: bali_hesabla += 0.0

        max_ball = len(meyarlar) * 1.0
        faiz = (bali_hesabla / max_ball) * 100

        st.session_state.dnp_bal = bali_hesabla
        st.session_state.dnp_faiz = faiz

        st.divider()
        st.subheader("📋 DNP Qiymətləndirmə Nəticəsi:")
        col_m1, col_m2 = st.columns(2)
        with col_m1: st.metric(label="Toplanan Bal", value=f"{bali_hesabla} / {max_ball}")
        with col_m2: st.metric(label="Uyğunluq Faiz Göstəricisi", value=f"{faiz:.1f}%")
        st.progress(int(faiz))

        if faiz >= 80:
            st.markdown(f'<div class="card-success"><h4>🟢 ADEKVATDIR (Aşağı risk)</h4><p><b>{teskilat_adi}</b> üzrə uyğunluq <b>{faiz:.1f}%</b>-dir.</p></div>', unsafe_allow_html=True)
        elif faiz >= 50:
            st.markdown(f'<div class="card-warning"><h4>🟡 ƏSAS ETİBARİLƏ ADEKVATDIR (Orta risk)</h4><p><b>{teskilat_adi}</b> üzrə uyğunluq <b>{faiz:.1f}%</b>-dir. Çatışmazlıqlar var.</p></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="card-danger"><h4>🔴 ADEKVAT DEYİL (Yüksək risk)</h4><p><b>{teskilat_adi}</b> üzrə uyğunluq yalnız <b>{faiz:.1f}%</b>-dir.</p></div>', unsafe_allow_html=True)

# ==========================================
# TAB 2: SAHƏVİ RİSK HESABLANMASI
# ==========================================
with tab2:
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

        # Avtomatik olaraq tarixçəyə də əlavə edirik
        history_entry = {
            "Tarix": str(yoxlama_tarixi),
            "Təşkilat": teskilat_adi,
            "DNP Faiz (%)": round(st.session_state.dnp_faiz, 1),
            "Risk Faiz (%)": round(nisbi_faiz, 1),
            "Ümumi Risk Balı": round(total_risk_val, 2)
        }
        if history_entry not in st.session_state.audit_history:
            st.session_state.audit_history.append(history_entry)

        st.divider()
        st.subheader("📈 Sahəvi Risk Təhlili Nəticəsi:")
        col_r1, col_r2 = st.columns(2)
        with col_r1: st.metric(label="Ümumi Risk Balı", value=f"{total_risk_val:.2f} / 8.00")
        with col_r2: st.metric(label="Nisbi Risk Faiz Göstəricisi", value=f"{nisbi_faiz:.1f}%")
        st.progress(int(nisbi_faiz))

        if nisbi_faiz < 35:
            st.markdown(f'<div class="card-success"><h4>🟢 AŞAĞI RİSK QRUPU</h4><p><b>{teskilat_adi}</b> üzrə standart monitorinq həyata keçirilir.</p></div>', unsafe_allow_html=True)
        elif nisbi_faiz <= 70:
            st.markdown(f'<div class="card-warning"><h4>🟡 ORTA RİSK QRUPU</h4><p><b>{teskilat_adi}</b> üzrə ən azı 2 ildən bir səyyar yoxlama olmalıdır.</p></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="card-danger"><h4>🔴 YÜKSƏK RİSK QRUPU</h4><p><b>{teskilat_adi}</b> üzrə gücləndirilmiş nəzarət tədbirləri zəruridir!</p></div>', unsafe_allow_html=True)

# ==========================================
# TAB 3: QRAFIK VƏ RİSK MATRİSİ (HEATMAP)
# ==========================================
with tab3:
    st.header("📈 Qrafik Analitika və 2D Risk Matrisi")
    st.markdown("Subyektin risk səviyyəsinin vizual paylanması və istilik xəritəsi (Risk Matrix):")

    if st.session_state.dnp_faiz > 0 or st.session_state.risk_faiz > 0:
        chart_data = pd.DataFrame({
            "Göstəricilər": ["DNP Uyğunluq Faiz Göstəricisi", "Sahəvi Risk Faiz Göstəricisi"],
            "Faiz (%)": [st.session_state.dnp_faiz, st.session_state.risk_faiz]
        })
        st.bar_chart(chart_data.set_index("Göstəricilər"))
        
        st.subheader("🎯 Risk İstilik Xəritəsi (Risk Heatmap Matrisi)")
        
        r_val = st.session_state.risk_faiz
        if r_val < 35:
            matrix_color = "background-color: #D1E7DD; color: #0F5132; padding: 15px; border-radius: 8px;"
            matrix_text = "🟢 YAŞIL ZONA: Aşağı Risk (Low Risk Matrix Position)"
        elif r_val <= 70:
            matrix_color = "background-color: #FFF3CD; color: #664D03; padding: 15px; border-radius: 8px;"
            matrix_text = "🟡 SARI ZONA: Orta Risk (Medium Risk Matrix Position)"
        else:
            matrix_color = "background-color: #F8D7DA; color: #842029; padding: 15px; border-radius: 8px;"
            matrix_text = "🔴 QIRMIZI ZONA: Yüksək Risk (High Risk Matrix Position)"

        st.markdown(f"""
            <div style="{matrix_color}">
                <h4>Cari Matris Vəziyyəti: {matrix_text}</h4>
                <p><b>Təşkilat:</b> {teskilat_adi} | <b>Riskin nisbi səviyyəsi:</b> {r_val:.1f}%</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ Zəhmət olmasa əvvəlcə 'DNP Qiymətləndirmə' və 'Sahəvi Risk' bölmələrində hesablamaları icra edin.")

# ==========================================
# TAB 4: HESABATIN YÜKLƏNMƏSİ
# ==========================================
with tab4:
    st.header("📥 Audit Hesabatının İxracı və Yüklənməsi")
    st.markdown("Aparılmış qiymətləndirmə nəticələrini rəsmi hesabat şəklində kompüterinizə endirin.")

    report_content = f"""
==================================================
AUDİTORLAR PALATASI - ƏL/TİMM AUDİT HESABATI
==================================================
Təşkilat: {teskilat_adi}
Məsul Şəxs: {mesul_sexs}
Yoxlama Tarixi: {yoxlama_tarixi}
--------------------------------------------------
1. DNP Uyğunluq Nəticəsi:
   - Toplanan Bal: {st.session_state.dnp_bal} / 10.0
   - Uyğunluq Faiz Göstəricisi: {st.session_state.dnp_faiz:.1f}%

2. Sahəvi Risk Nəticəsi:
   - Ümumi Risk Balı: {st.session_state.risk_bal:.2f} / 8.00
   - Nisbi Risk Faiz Göstəricisi: {st.session_state.risk_faiz:.1f}%

3. Yüklənmiş Sübut Sənədlərinin Sayı: {len(st.session_state.uploaded_evidences)} ədəd
==================================================
Sistem tərəfindən avtomatlaşdırılmış şəkildə generasiya edilmişdir.
"""

    st.text_area("Hesabatın Ön İzləməsi:", value=report_content, height=220)

    st.download_button(
        label="📥 Rəsmi Hesabatı TXT olaraq Yüklə",
        data=report_content,
        file_name=f"AML_Audit_Hesabati_{teskilat_adi.replace(' ', '_')}.txt",
        mime="text/plain",
        type="primary"
    )

# ==========================================
# TAB 5: SÜBUT SƏNƏDLƏRİ (EVIDENCE UPLOAD)
# ==========================================
with tab5:
    st.header("📎 Sənəd Sübutlarının Yüklənməsi (Evidence Upload)")
    st.markdown("Auditor yoxlama zamanı təşkilatın təqdim etdiyi sənədləri, PDF və ya şəkilləri sübut olaraq buraya yükləyə bilər.")

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

# ==========================================
# TAB 6: TARİXÇƏ VƏ TREND ANALİZİ
# ==========================================
with tab6:
    st.header("📉 Tarixçə və İllik Müqayisə (Audit Trail & Trend)")
    st.markdown("Keçmiş yoxlamalar və cari dövrün risk göstəricilərinin müqayisəli dinamikası:")

    if st.session_state.audit_history:
        df_history = pd.DataFrame(st.session_state.audit_history)
        st.dataframe(df_history, use_container_width=True)
        
        st.bar_chart(df_history.set_index("Tarix")["Risk Faiz (%)"])
        st.info("💡 **Trend İzahı:** Bu qrafik müxtəlif yoxlama tarixləri üzrə təşkilatın risk faizinin dəyişmə dinamikasını göstərir.")
    else:
        st.warning("⚠️ Hələ ki, tarixçəyə yazılmış yoxlama yoxdur. 'Sahəvi Risk' bölməsində hesablama apardıqdan sonra məlumatlar burada əks olunacaq.")