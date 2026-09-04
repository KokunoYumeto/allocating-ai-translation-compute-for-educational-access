"""Visible provenance for two inherited Indonesian substitution redraws."""
OVERRIDES = {
 'fs-id1167836692989': ('CNX_ElemAlg_Figure_01_02_012b_img_new.jpg', '3^x', '3^4'),
 'fs-id1169149089480': ('CNX_ElemAlg_Figure_01_02_013b_img_new.jpg', '2x² + 3x + 8', '2(4)² + 3(4) + 8'),
}
def adaptation_caption(media_id, track):
    if media_id not in OVERRIDES: return ''
    name, original, replacement = OVERRIDES[media_id]
    if track == 'id-academic':
        label='Adaptasi warisan edisi Indonesia (v1.0.2)'
        explanation=f'Gambar ulang untuk langkah substitusi x = 4: {original} menjadi {replacement}. Ini bukan piksel kanonis OpenStax yang tidak diubah.'
        link='Bandingkan gambar kanonis'
    else:
        label='Adaptasi saka edisi Indonesia (v1.0.2)'
        explanation=f'Gambar ulang kanggo langkah ngganti x nganggo 4: {original} dadi {replacement}. Iki dudu piksel sumber kanonis OpenStax sing ora diowahi.'
        link='Bandhingna karo gambar kanonis'
    return f'<figcaption class="meta" data-provenance="inherited-indonesian-substitution-redraw"><details><summary>{label}</summary><p>{explanation} <a href="source/canonical-witness-assets/{name}">{link}</a> · <a href="provenance/ASSET-OVERRIDES.json">SHA-256 / provenance</a>.</p></details></figcaption>'
