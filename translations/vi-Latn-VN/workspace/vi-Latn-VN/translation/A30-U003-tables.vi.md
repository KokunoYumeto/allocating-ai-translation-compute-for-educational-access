---
title: "Biểu diễn hàm số bằng bảng"
lang: vi-Latn-VN
subtitle: "A30 · Bài tự học 003 · Bản dịch thử nghiệm 0.1"
---

## Trước khi học {#vi-prerequisites}

*Hướng dẫn bổ sung:* Bạn đã biết mỗi đầu vào trong tập xác định của
một hàm số phải có đúng một đầu ra, và biết đọc ký hiệu $y=f(x)$.
Bài này dùng bảng để biểu diễn các cặp đầu vào–đầu ra và kiểm tra
điều kiện đó. Không cần tìm công thức hoặc viết chương trình.

Bài dịch trọn tiểu mục **Representing Functions Using Tables** của
mô-đun `m49301`, không phải toàn bộ mục 1.1. Các lưu ý bổ sung và
thay đổi cách bố trí bảng được ghi rõ.

## Biểu diễn hàm số bằng bảng {#fs-id1165137804204}

::: {#fs-id1165137648317}
Một cách thông dụng để biểu diễn hàm số là dùng bảng. Các hàng hoặc
cột của bảng cho biết những giá trị đầu vào và đầu ra tương ứng.
Trong một số trường hợp, các giá trị ấy là toàn bộ thông tin ta biết
về mối quan hệ đang xét; trong những trường hợp khác, bảng chỉ cho
một vài ví dụ được chọn từ một mối quan hệ đầy đủ hơn.
:::

::: {#fs-id1165137761188}
[Bảng 3](#Table_01_01_03) liệt kê đầu vào là số thứ tự của từng tháng
(tháng Một = 1, tháng Hai = 2, v.v.) và đầu ra là số ngày trong tháng
đó. Bảng cho đầy đủ số ngày của từng tháng trong một năm xác định
**không nhuận**. Chú ý rằng hàm số {{math:fs-id1165137761188:0}}
cho số ngày trong tháng, với ký hiệu {{math:fs-id1165137761188:1}},
ở đây nhận đầu vào là **số nguyên chỉ tháng**, không phải tên tháng.
:::

::: {#Table_01_01_03}
**Bảng 3. Số ngày trong từng tháng của một năm không nhuận.**

| Số thứ tự tháng {{math:Table_01_01_03:0}} (đầu vào) | Số ngày {{math:Table_01_01_03:1}} (đầu ra) |
| ---: | ---: |
| 1 | 31 |
| 2 | 28 |
| 3 | 31 |
| 4 | 30 |
| 5 | 31 |
| 6 | 30 |
| 7 | 31 |
| 8 | 31 |
| 9 | 30 |
| 10 | 31 |
| 11 | 30 |
| 12 | 31 |
:::

*Ghi chú trình bày:* Bảng 3–5 của nguồn được đổi từ các hàng ngang
dài sang hai cột; mỗi hàng mới giữ nguyên một cặp đầu vào–đầu ra.
Không thêm, bỏ hoặc sắp xếp lại các cặp số liệu.

*Lưu ý bổ sung:* Trong Bảng 3, tập xác định là $\{1,2,\ldots,12\}$.
Đầu vào $2$ chỉ tháng Hai, không phải số ngày trong tháng.
Chữ $D$ viết hoa được giữ nguyên theo nguồn, khác với chữ $d$ dùng
trong ví dụ về tên tháng ở bài trước.

::: {#fs-id1165135191568}
[Bảng 4](#Table_01_01_04) xác định hàm số
{{math:fs-id1165135191568:0}} Nhớ rằng ký hiệu này cho biết
{{math:fs-id1165135191568:1}} là tên hàm số nhận đầu vào
{{math:fs-id1165135191568:2}} và cho đầu ra
{{math:fs-id1165135191568:3}}
:::

::: {#Table_01_01_04}
**Bảng 4. Các giá trị đầu vào và đầu ra của $g$.**

| {{math:Table_01_01_04:0}} (đầu vào) | {{math:Table_01_01_04:1}} (đầu ra) |
| ---: | ---: |
| 1 | 8 |
| 2 | 6 |
| 3 | 7 |
| 4 | 6 |
| 5 | 8 |
:::

::: {#fs-id1165137561574}
[Bảng 5](#Table_01_01_05) cho biết tuổi tính bằng năm và chiều cao
tương ứng của các em nhỏ. Bảng này chỉ trình bày một phần dữ liệu
có thể có về tuổi và chiều cao của trẻ em. Ta thấy ngay rằng bảng
**không biểu diễn một hàm số**: cùng đầu vào 5 tuổi lại có hai đầu ra
khác nhau, 40 inch và 42 inch.
:::

::: {#Table_01_01_05}
**Bảng 5. Tuổi và chiều cao của các em nhỏ.**

| Tuổi {{math:Table_01_01_05:0}}, tính bằng năm (đầu vào) | Chiều cao {{math:Table_01_01_05:1}}, tính bằng inch (đầu ra) |
| ---: | ---: |
| 5 | 40 |
| 5 | 42 |
| 6 | 44 |
| 7 | 47 |
| 8 | 50 |
| 9 | 52 |
| 10 | 54 |
:::

*Lưu ý bổ sung:* Giữ nguyên đơn vị inch của nguồn, không đổi các số
đo sang xentimét. Đây là dữ liệu về nhiều em nhỏ; không mâu thuẫn với
việc xét chiều cao của một người xác định theo tuổi ở bài trước.

### Cách làm — Kiểm tra một bảng {#fs-id1165137804163}

::: {#fs-id1165134200185}
**Cho một bảng giá trị đầu vào và đầu ra, hãy xác định xem bảng có
biểu diễn hàm số hay không.**
:::

::: {#fs-id1165137461155}
1. Xác định các giá trị đầu vào và đầu ra.
2. Kiểm tra xem mỗi giá trị đầu vào có được ghép với đúng một giá trị
   đầu ra hay không. Nếu có, bảng biểu diễn một hàm số.
:::

*Lưu ý bổ sung:* Đầu ra có thể lặp lại ở những đầu vào khác nhau;
điều đó không làm mất tính chất hàm số. Ta kiểm tra tính duy nhất của
đầu ra **cho từng đầu vào**, không đòi hỏi các đầu ra đều khác nhau.

### Ví dụ 5 — Nhận biết bảng biểu diễn hàm số {#Example_01_01_05}

::: {#fs-id1165137416794}
::: {#fs-id1165135591087}
::: {#fs-id1165135503697}
Trong [Bảng 6](#Table_01_01_06), [Bảng 7](#Table_01_01_07) và
[Bảng 8](#Table_01_01_08), bảng nào biểu diễn một hàm số, nếu có?
:::

::: {#Table_01_01_06}
**Bảng 6.**

| Đầu vào | Đầu ra |
| ---: | ---: |
| 2 | 1 |
| 5 | 3 |
| 8 | 6 |
:::

::: {#Table_01_01_07}
**Bảng 7.**

| Đầu vào | Đầu ra |
| ---: | ---: |
| −3 | 5 |
| 0 | 1 |
| 4 | 5 |
:::

::: {#Table_01_01_08}
**Bảng 8.**

| Đầu vào | Đầu ra |
| ---: | ---: |
| 1 | 0 |
| 5 | 2 |
| 5 | 4 |
:::
:::

::: {#fs-id1165137665675}
::: {#fs-id1165137401396}
**Lời giải.** [Bảng 6](#Table_01_01_06) và
[Bảng 7](#Table_01_01_07) xác định các hàm số. Trong cả hai bảng,
mỗi giá trị đầu vào tương ứng với đúng một giá trị đầu ra.
[Bảng 8](#Table_01_01_08) không xác định một hàm số, vì đầu vào 5
tương ứng với hai đầu ra khác nhau.
:::

::: {#fs-id1165135161143}
Khi một bảng biểu diễn hàm số, ta cũng có thể dùng ký hiệu hàm số để
nêu các giá trị đầu vào và đầu ra tương ứng.
:::

::: {#fs-id1165137806634}
Hàm số trong [Bảng 6](#Table_01_01_06) có thể được biểu diễn bằng
cách viết
:::

::: {#fs-id1165137404863}
{{math:fs-id1165137404863:0}}
:::

::: {#fs-id1165137619677}
Tương tự, các đẳng thức
:::

::: {#fs-id1165137589116}
{{math:fs-id1165137589116:0}}
:::

::: {#fs-id1165137715365}
biểu diễn hàm số trong [Bảng 7](#Table_01_01_07).
:::

::: {#fs-id1165137656795}
[Bảng 8](#Table_01_01_08) không thể được biểu diễn theo cách tương
tự, vì bảng không biểu diễn một hàm số.
:::
:::
:::

*Lưu ý bổ sung:* Trong Bảng 7, đầu ra 5 xuất hiện hai lần, nhưng nó
ứng với hai đầu vào khác nhau là $-3$ và $4$. Mỗi đầu vào của bảng
vẫn có đúng một đầu ra, nên bảng biểu diễn một hàm số.
Trong Bảng 8, chính một đầu vào $5$ lại cho hai đầu ra $2$ và $4$.
Đây là điểm khác nhau cần kiểm tra.

*Lưu ý bổ sung về tên hàm số:* Các chữ $f$ và $g$ trong Ví dụ 5 được
dùng để đặt tên các hàm số của riêng ví dụ này; chúng không chỉ các
hàm số cùng tên ở Bảng 3 và Bảng 4.

### Tự thử 3 {#fs-id1165137749258}

::: {#ti_01_01_03}
::: {#fs-id1165137698328}
::: {#fs-id1165137698329}
[Bảng 9](#Table_01_01_09) có biểu diễn một hàm số không?
:::

::: {#Table_01_01_09}
**Bảng 9.**

| Đầu vào | Đầu ra |
| ---: | ---: |
| 1 | 10 |
| 2 | 100 |
| 3 | 1000 |
:::

*Gợi ý bổ sung:* Kiểm tra từng đầu vào rồi xem
[lời giải](#fs-id1165135322022); không cần đoán một công thức.
:::
:::

### Tự thử 3 — Lời giải {#fs-id1165135322022}

::: {#fs-id1165137844279}
**Đáp án nguồn:** Có.
:::

*Giải thích bổ sung:* Mỗi đầu vào 1, 2, 3 có đúng một đầu ra tương
ứng là 10, 100, 1000. Vì thế, bảng biểu diễn một hàm số trên tập xác
định $\{1,2,3\}$. Ba cặp dữ liệu này không tự xác định đầu ra tại
những đầu vào khác ngoài bảng.

## Tự đánh giá và phần tiếp theo {#vi-next}

*Câu hỏi bổ sung:* Bạn đã sẵn sàng học tiếp nếu giải thích được vì
sao Bảng 7 là một hàm số nhưng Bảng 8 không phải, và vì sao Bảng 3
phải ghi rõ điều kiện năm không nhuận.

Tiếp theo: **Tìm giá trị đầu vào và đầu ra của hàm số**, bắt đầu tại
`fs-id1165137503241` trong cùng mô-đun `m49301`.

## Nguồn và ghi công {#vi-attribution}

Bản dịch độc lập `vi-Latn-VN` từ Jay Abramson và các cộng tác viên
OpenStax, *Precalculus 2e*, mô-đun `m49301`, UUID
`11f4eacc-c348-4836-8c5b-747577d249ca`;
[nguồn được ghim](https://github.com/openstax/osbooks-college-algebra-bundle/tree/789b54099106b071d1d32bfcee454fed72eb4768).
Đối chiếu với [ấn bản Bahasa Indonesia](https://github.com/KokunoYumeto/openstax-precalculus-2e-id)
`0.1.0-alpha.58-reader.1`.

Văn bản và bản dịch A30 này theo
[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
Giữ nguyên ghi công tác giả và các thông báo trong `notices/`; các
thành phần của những sách khác giữ giấy phép riêng. Những phần ghi
“bổ sung” và việc bố trí lại Bảng 3–5 là thay đổi của bản dịch. Dấu
gạch trước số âm trong Bảng 7 được chuẩn hóa thành dấu trừ; giá trị
$-3$ không đổi. Không phải ấn bản chính thức hay được tác giả nguồn
bảo trợ. Được thực hiện với sự hỗ trợ của OpenAI Codex theo yêu cầu
người dùng; chưa có thẩm định của người bản ngữ.
