"""REJECTED PROBE: ToUnicode derivatives for shaped ActualText clusters.

This does not change glyphs, advances or outline programs. Within each existing
ActualText cluster, the first painted glyph maps to the complete logical cluster
and later painted glyphs map to an empty string. The original ActualText remains.
Only fresh font dictionaries/ToUnicode streams are added; originals stay intact.
The empty mapping fixes pypdf, but PDF.js falls back to raw glyph codes for those
empty entries. Never use this experimental derivative as the production output.
"""
from pathlib import Path
import argparse
import json
from pypdf import PdfReader,PdfWriter
from pypdf.generic import ArrayObject,ByteStringObject,ContentStream,DictionaryObject,DecodedStreamObject,NameObject


def repair(source:Path,output:Path):
    reader=PdfReader(source);writer=PdfWriter();writer.clone_document_from_reader(reader)
    cache={};clusters=0;glyphs=0
    def font_variant(original,code,unicode_text):
        key=(original.idnum,bytes(code),unicode_text)
        if key in cache:return cache[key]
        copied=DictionaryObject(dict(original.get_object().items()))
        dst=unicode_text.encode('utf-16-be').hex().upper()
        src=bytes(code).hex().upper();width=len(code)
        cmap=DecodedStreamObject();cmap.set_data((f'''/CIDInit /ProcSet findresource begin
12 dict begin begincmap
/CIDSystemInfo << /Registry (Adobe) /Ordering (UCS) /Supplement 0 >> def
/CMapName /GujaratiActualText def /CMapType 2 def
1 begincodespacerange <{'00'*width}> <{'FF'*width}> endcodespacerange
1 beginbfchar <{src}> <{dst}> endbfchar
endcmap CMapName currentdict /CMap defineresource pop end end
''').encode('ascii'))
        copied[NameObject('/ToUnicode')]=writer._add_object(cmap)
        ref=writer._add_object(copied);cache[key]=ref
        return ref
    for page in writer.pages:
        resources=page['/Resources'];fonts=resources['/Font']
        # Isolate the resource-name dictionary in case Chrome shared resources.
        fonts=DictionaryObject(dict(fonts.items()));resources[NameObject('/Font')]=fonts
        stream=ContentStream(page.get_contents(),writer,'bytes');ops=[];stack=[]
        source_font=None;source_size=None;active_font=None;variants={}
        def emit_string(value):
            nonlocal glyphs,active_font
            actual=next((x for x in reversed(stack) if x is not None),None)
            if actual is None:
                if active_font!=source_font:ops.append(([source_font,source_size],b'Tf'));active_font=source_font
                ops.append(([value],b'Tj'));return
            data=bytes(value);orig=fonts.raw_get(source_font)
            subtype=orig.get_object()['/Subtype'];width=2 if subtype=='/Type0' else 1
            if len(data)%width:raise ValueError('Unexpected glyph code width')
            for i in range(0,len(data),width):
                code=data[i:i+width];text=actual['text'] if not actual['emitted'] else ''
                actual['emitted']=True
                ref=font_variant(orig,code,text)
                name=variants.get(ref.idnum)
                if name is None:
                    name=NameObject(f'/GUCM{ref.idnum}');fonts[name]=ref;variants[ref.idnum]=name
                if active_font!=name:ops.append(([name,source_size],b'Tf'));active_font=name
                ops.append(([ByteStringObject(code)],b'Tj'));glyphs+=1
        for operands,op in stream.operations:
            if op in (b'BDC',b'BMC'):
                props=operands[1] if op==b'BDC' and len(operands)>1 else {}
                actual=props.get('/ActualText') if hasattr(props,'get') else None
                if actual is not None:
                    text=actual if isinstance(actual,str) else bytes(actual).decode('utf-16')
                    stack.append({'text':text,'emitted':False});clusters+=1
                else:stack.append(None)
                ops.append((operands,op))
            elif op==b'EMC':
                stack.pop();ops.append((operands,op))
            elif op==b'Tf':
                source_font=operands[0];source_size=operands[1];active_font=source_font;ops.append((operands,op))
            elif op==b'Tj':emit_string(operands[0])
            elif op==b'TJ':
                for value in operands[0]:
                    if isinstance(value,(str,bytes)):emit_string(value)
                    else:ops.append(([ArrayObject([value])],b'TJ'))
            elif op in (b"'",b'"'):raise ValueError('Unreviewed shorthand text operator')
            else:ops.append((operands,op))
        if stack:raise ValueError('Unbalanced content')
        stream.operations=ops;page.replace_contents(stream)
    writer.write(output)
    print(json.dumps({'clusters':clusters,'glyphs':glyphs,'font_variants':len(cache),'pages':len(writer.pages)}))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--experimental',action='store_true')
    a=p.parse_args()
    if not a.experimental:p.error('Rejected PDF.js probe; --experimental is required for research-only output')
    repair(a.source,a.output)
