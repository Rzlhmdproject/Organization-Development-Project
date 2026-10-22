import os
import time
import streamlit as st
from google import genai
from google.genai import types

# Konfigurasi Halaman Streamlit
st.set_page_config(page_title="Generator Job Description - Complete Selular", page_icon="📝", layout="centered")

st.title("📝 Generator Job Description OD")
st.caption("Aplikasi otomatisasi penyusunan Job Description sesuai standar PT Complete Selular")

# Mengambil API Key langsung dari Secrets / Environment Variable
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

# Form Input Teks Kasar dari PIC
raw_input = st.text_area(
    "Masukkan Draf Kasar / Isian dari PIC:",
    height=250,
    placeholder="Contoh:\n1. Cek absen talenta anak-anak toko\n2. Pastikan SOP toko jalan\n3. Urus Laporan LPJ tiap minggu..."
)

if st.button("✨ Proses & Rapikan Job Desc", type="primary"):
    if not api_key:
        st.error("API Key belum terkonfigurasi di Streamlit Secrets! Silakan atur terlebih dahulu di dashboard Streamlit.")
    elif not raw_input.strip():
        st.warning("Mohon isi draf kasar dari PIC terlebih dahulu.")
    else:
        with st.spinner("Sedang memproses dan menyusun sesuai standar OD..."):
            # Daftar model prioritas (jika model utama 503, otomatis gunakan model cadangan)
            candidate_models = ['gemini-3.8-flash', 'gemini-1.5-pro', 'gemini-2.0-flash-exp']
            
            client = genai.Client(api_key=api_key)
            
            system_instruction = """
            Anda adalah seorang ahli Organization Development (OD) dan HR Operations profesional di PT Complete Selular.
            Tugas Anda adalah merapikan draf tugas kasar (Job Desc) dari PIC ke dalam format dokumen resmi perusahaan.

            KETENTUAN PENULISAN:
            1. Jangan mengubah makna substansial dari informasi dasar yang diberikan oleh PIC.
            2. Jangan menambahkan tugas baru di luar informasi yang diberikan, kecuali untuk menyempurnakan struktur kalimat.
            3. Gunakan kalimat efektif dan wajib diawali dengan Kata Kerja Operasional (KKO) seperti: Bertanggung jawab..., Melaksanakan..., Memastikan..., Melakukan..., Mengoordinasikan..., Menyusun..., Mengawasi..., Memverifikasi...
            4. Hindari pengulangan makna antar poin. Gabungkan aktivitas dengan tujuan serupa.
            5. Susun poin berdasarkan tingkat kepentingannya (prioritas tertinggi di awal).
            6. Klasifikasikan setiap poin ke dalam 3 kategori berikut secara tegas TANPA duplikasi antar kategori:
               - A. Tugas Utama
               - B. Administrasi
               - C. Laporan

            FORMAT OUTPUT:
            A. Tugas Utama
            1. [Poin...]
            
            B. Administrasi
            1. [Poin...]
            
            C. Laporan
            1. [Poin...]
            """

            response = None
            last_error = None

            # Coba setiap model yang tersedia
            for model_name in candidate_models:
                success = False
                for attempt in range(2): # Coba 2 kali per model
                    try:
                        response = client.models.generate_content(
                            model=model_name,
                            contents=f"Ubah draf kasar berikut sesuai standar OD:\n\n{raw_input}",
                            config=types.GenerateContentConfig(
                                system_instruction=system_instruction,
                                temperature=0.2,
                            ),
                        )
                        if response and response.text:
                            success = True
                            break
                    except Exception as err:
                        last_error = err
                        # Jika server sibuk (503), tunggu 2 detik sebelum retry
                        if "503" in str(err):
                            time.sleep(2)
                        else:
                            break # Jika error tipe lain (misal 404), langsung ganti model
                
                if success:
                    break

            if response and response.text:
                st.success("Berhasil disusun!")
                st.markdown("### 📄 Hasil Job Description Standar OD")
                st.code(response.text, language="markdown")
            else:
                st.error(f"Server Google AI sedang sangat padat saat ini. Silakan coba klik tombol kembali beberapa saat lagi. Detail: {last_error}")
