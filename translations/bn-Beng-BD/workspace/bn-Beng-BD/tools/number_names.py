"""Independent arithmetic interpretation of the editorial Bangla number-name register.

This is a QA helper, not a nationally certified spelling dictionary. Common
variants are accepted; the canon ledger records the entries actually consulted.
"""
import re, unicodedata

WORDS = '''শূন্য এক দুই তিন চার পাঁচ ছয় সাত আট নয় দশ এগারো বারো তেরো চৌদ্দ পনেরো ষোলো সতেরো আঠারো উনিশ বিশ একুশ বাইশ তেইশ চব্বিশ পঁচিশ ছাব্বিশ সাতাশ আটাশ ঊনত্রিশ ত্রিশ একত্রিশ বত্রিশ তেত্রিশ চৌত্রিশ পঁয়ত্রিশ ছত্রিশ সাঁইত্রিশ আটত্রিশ ঊনচল্লিশ চল্লিশ একচল্লিশ বিয়াল্লিশ তেতাল্লিশ চুয়াল্লিশ পঁয়তাল্লিশ ছেচল্লিশ সাতচল্লিশ আটচল্লিশ ঊনপঞ্চাশ পঞ্চাশ একান্ন বাহান্ন তিপ্পান্ন চুয়ান্ন পঞ্চান্ন ছাপ্পান্ন সাতান্ন আটান্ন ঊনষাট ষাট একষট্টি বাষট্টি তেষট্টি চৌষট্টি পঁয়ষট্টি ছেষট্টি সাতষট্টি আটষট্টি ঊনসত্তর সত্তর একাত্তর বাহাত্তর তিয়াত্তর চুয়াত্তর পঁচাত্তর ছিয়াত্তর সাতাত্তর আটাত্তর ঊনআশি আশি একাশি বিরাশি তিরাশি চুরাশি পঁচাশি ছিয়াশি সাতাশি আটাশি ঊননব্বই নব্বই একানব্বই বিরানব্বই তিরানব্বই চুরানব্বই পঁচানব্বই ছিয়ানব্বই সাতানব্বই আটানব্বই নিরানব্বই'''.split()
assert len(WORDS)==100
def norm(text):return unicodedata.normalize('NFC',text)
VALUES={norm(word):i for i,word in enumerate(WORDS)}
VALUES.update({norm(k):v for k,v in {'ছয়':6,'নয়':9,'ষোল':16,'উনত্রিশ':29,'উনচল্লিশ':39,'বায়ান্ন':52,'উনপঞ্চাশ':49,'উনষাট':59,'উনসত্তর':69,'উনআশি':79,'উননব্বই':89,'ঊনশত':99}.items()})
SCALES={'হাজার':1000,'লক্ষ':100000,'লাখ':100000,'মিলিয়ন':10**6,'কোটি':10**7,'বিলিয়ন':10**9,'ট্রিলিয়ন':10**12}
SCALES={norm(k):v for k,v in SCALES.items()}

def small(tokens):
    if len(tokens)==1 and tokens[0] in VALUES:return VALUES[tokens[0]]
    assert 1<=len(tokens)<=2,tokens
    first=tokens[0]
    suffix='শত' if first.endswith('শত') else 'শ'
    assert first.endswith(suffix),tokens
    prefix=first[:-len(suffix)] or norm('এক')
    hundreds=VALUES[prefix]
    assert 1<=hundreds<=9,tokens
    rest=VALUES[tokens[1]] if len(tokens)==2 else 0
    assert 0<=rest<=99
    return hundreds*100+rest

def parse_name(text):
    tokens=norm(text).replace(',',' ').split()
    # Split recursively at the largest scale. This also handles এক লক্ষ কোটি.
    positions=[(SCALES[token],i) for i,token in enumerate(tokens) if token in SCALES]
    if not positions:return small(tokens)
    scale,index=max(positions)
    left=parse_name(' '.join(tokens[:index])) if index else 1
    right=parse_name(' '.join(tokens[index+1:])) if index+1<len(tokens) else 0
    assert right<scale,(text,right,scale)
    return left*scale+right

if __name__=='__main__':
    for i,word in enumerate(WORDS):assert parse_name(word)==i
    for h in range(1,10):
        for r in range(100):
            text=WORDS[h]+'শত'+(' '+WORDS[r] if r else '')
            assert parse_name(text)==100*h+r
    assert parse_name('এক লক্ষ কোটি')==10**12
    print('1000 under-thousand names and compound scale passed')
