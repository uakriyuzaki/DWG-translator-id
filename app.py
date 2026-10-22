import io, os, re, zipfile
import streamlit as st
import ezdxf
from deep_translator import GoogleTranslator

st.set_page_config(page_title='DWG Translator',page_icon='🌐',layout='wide')
st.title('DWG Translator — Mandarin → Indonesia')
st.caption('Terjemahkan TEXT, MTEXT dan atribut tanpa mengubah geometri, koordinat, nilai dimensi atau skala.')
st.warning('DWG asli memerlukan konversi server menggunakan ODA File Converter berlisensi/diizinkan. Versi siap jalan ini menerima DXF; konversikan DWG ke DXF terlebih dahulu. Jangan mengganti ekstensi DWG menjadi DXF.')
up=st.file_uploader('Unggah gambar DXF',type=['dxf'])
include_attrs=st.checkbox('Terjemahkan atribut blok (ATTRIB)',value=True)
include_dim=st.checkbox('Terjemahkan teks override dimensi (hanya teks Mandarin; angka dan placeholder tetap)',value=False)
preview=st.checkbox('Pratinjau teks sebelum memproses',value=True)
pattern=re.compile(r'[\u3400-\u9fff]')
translator=GoogleTranslator(source='zh-CN',target='id')

def translate_safe(value):
    if not pattern.search(value): return value
    # Protect AutoCAD inline codes, format codes, placeholders, numerical sequences.
    protected=[]
    token_pattern=re.compile(r'(\\[A-Za-z][^;]*;|\\[PpLlOoKk]|%%[A-Za-z0-9]+|<>|%<.*?>%|\{[^{}]*\}|\d+(?:[.,]\d+)*(?:\s?(?:mm|cm|m|°|%))?)')
    def mask(m):
        protected.append(m.group()); return f' ZXQPROTECT{len(protected)-1}QXZ '
    masked=token_pattern.sub(mask,value)
    try: result=translator.translate(masked)
    except Exception as e: raise RuntimeError(f'Layanan terjemahan gagal: {e}')
    for i,orig in enumerate(protected):
        result=re.sub(r'ZXQPROTECT\s*'+str(i)+r'QXZ',lambda _:orig,result,flags=re.I)
    if 'ZXQPROTECT' in result.upper(): raise RuntimeError('Token CAD tidak dapat dipulihkan; perubahan dibatalkan.')
    return result

if up:
    raw=up.getvalue()
    try:
        doc=ezdxf.read(io.StringIO(raw.decode('utf-8-sig',errors='strict')))
    except UnicodeDecodeError:
        try: doc=ezdxf.read(io.StringIO(raw.decode('gb18030')))
        except Exception as e: st.error(f'Gagal membaca DXF: {e}'); st.stop()
    except Exception as e: st.error(f'Gagal membaca DXF: {e}'); st.stop()
    entities=[]
    for layout in doc.layouts:
        for e in layout:
            if e.dxftype() in ('TEXT','MTEXT') or (include_attrs and e.dxftype() in ('ATTRIB','ATTDEF')):
                entities.append((e,'text',e.dxf.text if e.dxftype()!='MTEXT' else e.text))
            if include_dim and e.dxftype()=='DIMENSION' and e.dxf.hasattr('text'):
                entities.append((e,'dimension',e.dxf.text))
            if include_attrs and e.dxftype()=='INSERT':
                for a in e.attribs: entities.append((a,'text',a.dxf.text))
    candidates=[(e,kind,t) for e,kind,t in entities if pattern.search(t)]
    st.info(f'{len(candidates)} objek teks Mandarin ditemukan dari {len(entities)} objek teks yang diperiksa.')
    if preview: st.dataframe([{'Jenis':e.dxftype(),'Handle':e.dxf.handle,'Teks asli':t} for e,k,t in candidates],use_container_width=True)
    if st.button('Terjemahkan dan siapkan DXF',type='primary',disabled=not candidates):
        changes=[]
        with st.spinner('Menerjemahkan teks...'):
            try:
                cache={}
                for e,kind,original in candidates:
                    if original not in cache: cache[original]=translate_safe(original)
                    translated=cache[original]
                    if kind=='dimension' and ('<>' in original)!=( '<>' in translated): raise RuntimeError('Placeholder dimensi berubah.')
                    changes.append((e,kind,original,translated))
                # Only commit after all translations succeed.
                for e,kind,old,new in changes:
                    if e.dxftype()=='MTEXT': e.text=new
                    else: e.dxf.text=new
                out=io.StringIO(); doc.write(out)
                st.success(f'{len(changes)} teks diproses. Periksa tampilan dan font CAD sebelum penggunaan produksi.')
                st.dataframe([{'Jenis':e.dxftype(),'Asli':old,'Indonesia':new} for e,k,old,new in changes],use_container_width=True)
                st.download_button('Unduh DXF hasil terjemahan',out.getvalue().encode('utf-8-sig'),file_name=os.path.splitext(up.name)[0]+'_ID.dxf',mime='application/dxf')
            except Exception as e: st.error(f'Proses dibatalkan: {e}')
st.divider()
st.caption('Tidak menerjemahkan teks yang sudah menjadi outline/kurva, XREF, atau teks dalam gambar raster. Selalu audit file hasil di aplikasi CAD sebelum diterbitkan.')
