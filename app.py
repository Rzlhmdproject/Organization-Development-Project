import os
import streamlit as st
from google import genai
from google.genai import types

# Konfigurasi Halaman (Mode Wide agar terlihat seperti Dashboard Profesional)
st.set_page_config(
    page_title="OD Job Desc Generator - PT Complete Selular",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling CSS untuk tampilan yang lebih bersih dan elegan
st.markdown("""
    <style>
    .main-title {
        font-size: 26px;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 14px;
        color: #4B5563;
        margin-bottom: 20px;
    }
    .stButton>button {
        width: 100%;
        background-color: #2563EB;
        color: white;
        font-weight: 600;
        border-radius: 6px;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #1D4ED8;
    }
    </style>
""", unsafe_allow_html=True)

# Header Aplikasi
st.markdown('<p class="main-title">🏢 Organization Development - Job Description Generator</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">PT Complete Selular | Sistem Otomatisasi Penyusunan Standar Kompetensi & Tugas Jabatan</p>', unsafe_allow_html=True)

# Mengambil API Key dari Secrets Streamlit / Environment
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

# Layout Utama Menjadi 2 Kolom (Kiri: Input, Kanan: Output)
col_input, col_output = st.columns([1, 1], gap="large")

with col_input:
    st.markdown("### 📥 Input Draf PIC")
    
    # Opsi tambahan untuk memperkaya konteks jabatan
    job_title = st.text_input("Nama Jabatan / Posisi:", placeholder="Contoh: Store Supervisor / HR Staff")
    department = st.selectbox("Departemen:", ["Retail / Store Operations", "Human Resources (OD/HC)", "Finance & Accounting", "Marketing", "Supply Chain / Warehouse", "IT & Support"])
    
    raw_input = st.text_area(
        "Masukkan Catatan / Draf Kasar Tugas dari PIC:",
        height=280,
        placeholder="Contoh:\n- Tiap pagi cek absensi anak toko\n- Bikin laporan omzet mingguan ke SPV\n- Pastikan SOP kebersihan toko jalan\n- Urus administrasi klaim barang rusak"
    )
    
    process_btn = st.button("✨ Proses & Generate Job Desc")

with col_output:
    st.markdown("### 📄 Hasil Dokumen Resmi OD")
    
    output_container = st.container()
    
    if process_btn:
        if not api_key:
            with output_container:
                st.error("⚠️ API Key belum dikonfigurasi di Streamlit Secrets.")
        elif not raw_input.strip():
            with output_container:
                st.warning("⚠️ Mohon masukkan draf kasar tugas terlebih dahulu.")
        else:
            with st.spinner("🤖 AI sedang merumuskan draf sesuai standar kompetensi OD..."):
                try:
                    client = genai.Client(api_key=api_key)
                    
                    system_instruction = f"""
                    Anda adalah seorang pakar Organization Development (OD) dan HR Operations senior di PT Complete Selular.
                    Tugas Anda adalah mentransformasikan draf catatan tugas kasar dari PIC untuk posisi '{job_title or "Karyawan"}' di departemen '{department}' menjadi dokumen Job Description formal perusahaan yang profesional, tajam, dan terstruktur.

                    ATURAN MUTLAK PENULISAN:
                    1. Gunakan Bahasa Indonesia formal, lugas, dan bernada profesional korporat.
                    2. Setiap poin tugas WAJIB diawali dengan Kata Kerja Operasional (KKO) yang kuat, seperti: Bertanggung jawab atas..., Melaksanakan..., Memastikan..., Melakukan..., Mengoordinasikan..., Menyusun..., Mengawasi..., Memverifikasi..., Mengevaluasi...
                    3. Jangan mengubah esensi atau makna substansial dari informasi dasar yang diberikan oleh PIC, namun perhalus tata bahasanya menjadi kalimat efektif.
                    4. Klasifikasikan dan kelompokkan setiap tugas secara tegas ke dalam 3 kategori berikut TANPA ada duplikasi:
                       - A. Tugas Utama (Core Tasks / Tanggung jawab operasional inti jabatan)
                       - B. Administrasi (Administrative Tasks / Pengelolaan berkas, data, sistem, dan rutinitas penunjang)
                       - C. Laporan (Reporting Tasks / Pembuatan laporan berkala harian, mingguan, bulanan, dll)
                    5. Urutkan poin berdasarkan tingkat prioritas dan kepentingannya dari yang tertinggi.

                    FORMAT OUTPUT (Gunakan Markdown yang rapi):
                    ### POSISI: {job_title or "Professional Staff"}
                    ### DEPARTEMEN: {department}

                    A. Tugas Utama
                    1. [Kalimat efektif diawali KKO...]
                    2. [Kalimat efektif diawali KKO...]

                    B. Administrasi
                    1. [Kalimat efektif diawali KKO...]

                    C. Laporan
                    1. [Kalimat efektif diawali KKO...]
                    """

                    response = client.models.generate_content(
                        model='gemini-2.0-flash',
                        contents=f"Ubah catatan tugas kasar berikut menjadi Job Description profesional:\n\n{raw_input}",
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction,
                            temperature=0.2,
                        ),
                    )

                    if response and response.text:
                        st.session_state['generated_result'] = response.text
                    else:
                        st.error("Gagal memproses respons dari server.")
                        
                except Exception as e:
                    with output_container:
                        st.error(f"Terjadi kendala teknis: {e}")

    # Tampilkan hasil jika sudah ada di session state
    if 'generated_result' in st.session_state:
        with output_container:
            st.success("✅ Job Description Berhasil Disusun!")
            st.code(st.session_state['generated_result'], language="markdown")
            
            # Tombol unduh hasil teks
            st.download_button(
                label="📥 Unduh sebagai File (.txt)",
                data=st.session_state['generated_result'],
                file_name=f"JobDesc_{job_title.replace(' ', '_') if job_title else 'Employee'}.txt",
                mime="text/plain"
            )
    else:
        with output_container:
            st.info("👈 Silakan isi form di sebelah kiri lalu klik tombol **Proses & Generate Job Desc** untuk melihat hasil analisis AI di sini.")
