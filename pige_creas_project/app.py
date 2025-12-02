import streamlit as st
import io
import pandas as pd
from utils.gif_utils import read_gif_all_frames, save_gif
from utils.apng_utils import read_apng_all_frames, save_apng
from utils.imaging import resize_frames, overlay_text

st.set_page_config(page_title="Pige Créas", layout="wide")

st.sidebar.title("Pige Créas — Display/Native/App")
uploads = st.sidebar.file_uploader(
    "Uploader vos créas (GIF/APNG)", type=["gif", "png"], accept_multiple_files=True
)
default_loop = st.sidebar.number_input("Boucle (0 = infini)", value=0, min_value=0)
add_text = st.sidebar.text_input("Overlay texte (optionnel)")
resize = st.sidebar.checkbox("Redimensionner")
target_w = st.sidebar.number_input("Largeur", value=300, min_value=10) if resize else None
target_h = st.sidebar.number_input("Hauteur", value=250, min_value=10) if resize else None

tab1, tab2 = st.tabs(["Édition/Export", "Rapport & Téléchargements"])

all_reports = []

with tab1:
    if uploads:
        for f in uploads:
            st.subheader(f.name)
            file_bytes = f.read()
            is_png = f.type == "image/png" or f.name.lower().endswith(".png")
            try:
                if is_png:
                    frames, durations, meta = read_apng_all_frames(file_bytes)
                    format_in = "APNG"
                else:
                    frames, durations, meta = read_gif_all_frames(file_bytes)
                    format_in = "GIF"
            except Exception as e:
                st.error(f"Lecture échouée ({e}). On tente la lecture GIF…")
                frames, durations, meta = read_gif_all_frames(file_bytes)
                format_in = "GIF"

            if add_text:
                frames = overlay_text(frames, add_text)
            if resize:
                frames = resize_frames(frames, target_w, target_h)

            df = pd.DataFrame({"frame": list(range(len(frames))), "dur_ms": durations, "ordre": list(range(len(frames)))})
            st.caption("Éditez les durées (ms) et l’ordre si besoin ; double-cliquez pour modifier.")
            edited = st.data_editor(df, use_container_width=True, num_rows="dynamic")
            order = edited["ordre"].astype(int).tolist()
            frames = [frames[i] for i in order]
            durations = [int(edited.loc[edited["ordre"]==i, "dur_ms"].values[0]) for i in order]

            cols = st.columns(min(6, len(frames)))
            for i, fr in enumerate(frames):
                with cols[i % len(cols)]:
                    st.image(fr, caption=f"Frame {i} — {durations[i]} ms", use_column_width=True)

            c1, c2 = st.columns(2)
            with c1:
                if st.button(f"Exporter en GIF — {f.name}"):
                    out_bytes = save_gif(frames, durations, loop=default_loop)
                    st.download_button("Télécharger GIF", data=out_bytes, file_name=f"{f.name}.gif", mime="image/gif")
            with c2:
                if st.button(f"Exporter en APNG — {f.name}"):
                    out_bytes = save_apng(frames, durations, loop=default_loop)
                    st.download_button("Télécharger APNG", data=out_bytes, file_name=f"{f.name}.png", mime="image/png")

            all_reports.append({"Créa": f.name, "Format source": format_in, "Frames": len(frames), "Largeur": frames[0].width, "Hauteur": frames[0].height, "Durée totale (ms)": sum(durations)})

with tab2:
    if all_reports:
        report_df = pd.DataFrame(all_reports)
        st.dataframe(report_df, use_container_width=True)
        bio = io.BytesIO()
        with pd.ExcelWriter(bio, engine="openpyxl") as w:
            report_df.to_excel(w, index=False, sheet_name="Pige")
        st.download_button("Télécharger rapport Excel", data=bio.getvalue(), file_name="pige_creas.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.info("Uploadez des fichiers dans l’onglet Édition/Export pour générer le rapport.")
