---
title: "Bài tập số: đọc bảng và tính giá trị hàm số"
lang: vi-Latn-VN
subtitle: "A30 · Bài tự học 014 · Bản dịch thử nghiệm 0.1"
---

## Phạm vi và cách học {#vi-prerequisites}

Bài này hoàn tất bản dịch nhóm *Numeric* trong phần bài tập mục 1.1
của mô-đun m49301 bằng 13 bài mới, mang số 63–75 theo thứ tự của toàn
bộ phần bài tập nguồn. Ba bài đầu nhóm, số 60–62, đã có trong U001
và được dẫn liên kết bên dưới, không dịch lặp lại. Giữ tiêu đề nhóm,
mọi hướng dẫn chung và bảng dùng chung; dừng trước nhóm *Technology*
fs-id1165134373511.

*Hướng dẫn bổ sung:* Khi đọc bảng, mỗi cặp đầu vào–đầu ra phải được
giữ nguyên. Khi tính từ công thức, thay biến bằng đầu vào đã cho và
đặt đầu vào trong ngoặc; chú ý dấu âm, bình phương, mẫu số và số mũ âm. Các hàm số ở những
nhóm bài khác nhau được xét độc lập, dù cùng dùng tên $f$.

Bốn bảng nguồn được chuyển từ các hàng ngang thành hai cột dọc để
dễ đọc, giữ nguyên mọi cặp và thứ tự. Nguồn kèm bảy đáp án cho 13
bài mới; sáu lời giải còn thiếu được đánh dấu bổ sung. Trong bài 71,
nguồn dùng dấu bằng cho ba số thập phân đã làm tròn. Bản dịch giữ
bản ghi ấy để đối chiếu, chỉ rõ sai sót và cung cấp ký hiệu đúng.

## Bài tập số {#fs-id1165135342204}

### Ba bài đã có trong U001 {#vi-u001-references}

::: {#fs-id1165133324912}
Trong các bài sau, hãy xác định quan hệ đã cho có biểu diễn một hàm số
hay không.
:::

Hướng dẫn nguồn này áp dụng cho ba bài đã dịch:

- [Bài 60 — B3 trong U001](A30-U001-functions.vi.html#fs-id1165133324915).
- [Bài 61 — B4 trong U001](A30-U001-functions.vi.html#fs-id1165135245507).
- [Bài 62 — B5 trong U001](A30-U001-functions.vi.html#fs-id1165135381342).

Các liên kết cần tệp U001 nằm cùng thư mục với tệp đọc hiện tại.
Mười ba bài còn lại và lời giải của chúng đều có ngay dưới đây.

### Quan hệ cho bằng bảng {#vi-table-functions}

::: {#fs-id1165133260452}
Trong ba bài tiếp theo, hãy xác định quan hệ cho bằng bảng có phải là
một hàm số hay không, với đầu ra {{math:fs-id1165133260452:0}}
và đầu vào {{math:fs-id1165133260452:1}}
:::

#### Bài 63 {#fs-id1165137644802}

::: {#fs-id1165137644804}
::: {#fs-id1165137644806}
Đầu vào: {{math:fs-id1165137644806:0}}.
Đầu ra: {{math:fs-id1165137644806:1}}.

| Đầu vào | Đầu ra |
| ---: | ---: |
| 5 | 3 |
| 10 | 8 |
| 15 | 14 |
:::
:::

[Xem lời giải bài 63](#fs-id1165137771736).

#### Bài 64 {#fs-id1165137771740}

::: {#fs-id1165137771742}
::: {#fs-id1165137771744}
Đầu vào: {{math:fs-id1165137771744:0}}.
Đầu ra: {{math:fs-id1165137771744:1}}.

| Đầu vào | Đầu ra |
| ---: | ---: |
| 5 | 3 |
| 10 | 8 |
| 15 | 8 |
:::
:::

[Xem lời giải bổ sung bài 64](#vi-sol-64).

#### Bài 65 {#fs-id1165137758640}

::: {#fs-id1165137758643}
::: {#fs-id1165137758645}
Đầu vào: {{math:fs-id1165137758645:0}}.
Đầu ra: {{math:fs-id1165137758645:1}}.

| Đầu vào | Đầu ra |
| ---: | ---: |
| 5 | 3 |
| 10 | 8 |
| 10 | 14 |
:::
:::

[Xem lời giải bài 65](#fs-id1165135641696).

### Tính giá trị và tìm đầu vào trong bảng {#vi-shared-table}

::: {#fs-id1165135641701}
Trong hai bài tiếp theo, hãy dùng hàm số {{math:fs-id1165135641701:0}}
được cho trong [bảng dưới đây](#fs-id1165137727218).
:::

::: {#fs-id1165137727218}
**Bảng dùng chung cho bài 66 và bài 67.**

| $x$ | $f(x)$ |
| ---: | ---: |
| 0 | 74 |
| 1 | 28 |
| 2 | 1 |
| 3 | 53 |
| 4 | 56 |
| 5 | 3 |
| 6 | 36 |
| 7 | 45 |
| 8 | 14 |
| 9 | 47 |
:::

*Lưu ý bổ sung:* Bài chỉ cho các cặp trong bảng. Không tự nội suy
giá trị giữa các đầu vào hoặc kết luận về những đầu vào không được ghi.

#### Bài 66 {#fs-id1165135541988}

::: {#fs-id1165135541990}
::: {#fs-id1165135541992}
Tính {{math:fs-id1165135541992:0}}
:::
:::

[Xem lời giải bổ sung bài 66](#vi-sol-66).

#### Bài 67 {#fs-id1165137453742}

::: {#fs-id1165137453744}
::: {#fs-id1165137723310}
Giải phương trình {{math:fs-id1165137723310:0}}
:::
:::

[Xem lời giải bài 67](#fs-id1165137832462).

### Tính giá trị từ công thức {#vi-formula-evaluation}

::: {#fs-id1165137757773}
Trong sáu bài tiếp theo, hãy tính các giá trị của hàm số
{{math:fs-id1165137757773:0}} sau đây:

{{math:fs-id1165137757773:1}}

và {{math:fs-id1165137757773:2}}
:::

#### Bài 68 {#fs-id1165135581074}

::: {#fs-id1165135581076}
::: {#fs-id1165134437212}
{{math:fs-id1165134437212:0}}
:::
:::

[Xem lời giải bổ sung bài 68](#vi-sol-68).

#### Bài 69 {#fs-id1165137812524}

::: {#fs-id1165137812526}
::: {#fs-id1165137812528}
{{math:fs-id1165137812528:0}}
:::
:::

[Xem lời giải bài 69](#fs-id1165135192892).

#### Bài 70 {#fs-id1165135445749}

::: {#fs-id1165135445751}
::: {#fs-id1165135445753}
{{math:fs-id1165135445753:0}}
:::
:::

[Xem lời giải bổ sung bài 70](#vi-sol-70).

#### Bài 71 {#fs-id1165137937596}

::: {#fs-id1165135181211}
::: {#fs-id1165135181213}
{{math:fs-id1165135181213:0}}
:::
:::

[Xem đáp án nguồn và hiệu chỉnh bài 71](#fs-id1165137755505).

#### Bài 72 {#fs-id1165134573828}

::: {#fs-id1165134573830}
::: {#fs-id1165134573832}
{{math:fs-id1165134573832:0}}
:::
:::

[Xem lời giải bổ sung bài 72](#vi-sol-72).

#### Bài 73 {#fs-id1165133248574}

::: {#fs-id1165133248576}
::: {#fs-id1165133248578}
{{math:fs-id1165133248578:0}}
:::
:::

[Xem lời giải bài 73](#fs-id1165137770304).

### Kết hợp giá trị của ba hàm số {#vi-three-functions}

::: {#fs-id1165135306461}
Trong hai bài tiếp theo, hãy tính các biểu thức đã cho bằng cách dùng
các hàm số {{math:fs-id1165135306461:0}} và
{{math:fs-id1165135306461:1}}
:::

::: {#eip-582}
{{math:eip-582:0}}

{{math:eip-582:1}}

{{math:eip-582:2}}
:::

#### Bài 74 {#fs-id1165135575197}

::: {#fs-id1165135575199}
::: {#fs-id1165135575201}
{{math:fs-id1165135575201:0}}
:::
:::

[Xem lời giải bổ sung bài 74](#vi-sol-74).

#### Bài 75 {#fs-id1165134086037}

::: {#fs-id1165134086039}
::: {#fs-id1165134086040}
{{math:fs-id1165134086040:0}}
:::
:::

[Xem lời giải bài 75](#fs-id1165134373506).

## Lời giải và giải thích {#vi-answers}

### Bài 63 — Lời giải nguồn {#fs-id1165137771736}

::: {#fs-id1165137771737}
Bảng biểu diễn một hàm số.
:::

*Giải thích bổ sung:* Mỗi đầu vào trong tập $\{5,10,15\}$ có đúng
một đầu ra: lần lượt là 3, 8 và 14.

### Bài 64 — Lời giải bổ sung {#vi-sol-64}

Nguồn không kèm lời giải cho bài này. Lời giải sau được biên soạn cho
bản tiếng Việt.

Bảng biểu diễn một hàm số: 5 ứng với 3, 10 ứng với 8, và 15 cũng
ứng với 8. Đầu ra 8 xuất hiện hai lần nhưng ở hai đầu vào khác nhau;
không có đầu vào nào nhận hai đầu ra. Hàm số này không đơn ánh,
nhưng bài chỉ hỏi nó có phải là hàm số hay không.

### Bài 65 — Lời giải nguồn {#fs-id1165135641696}

::: {#fs-id1165135641697}
Bảng không biểu diễn một hàm số.
:::

*Giải thích bổ sung:* Cùng đầu vào 10 ứng với cả 8 và 14, là hai đầu
ra khác nhau. Đây là vi phạm điều kiện hàm số, khác với việc lặp đầu ra
ở bài 64.

### Bài 66 — Lời giải bổ sung {#vi-sol-66}

Nguồn không kèm lời giải cho bài này. Lời giải sau được biên soạn cho
bản tiếng Việt.

Tìm đầu vào 3 trong [bảng dùng chung](#fs-id1165137727218). Đầu ra
tương ứng là 53, nên $f(3)=53$. Không nhầm với đầu ra 3: số đó thuộc
cặp $(5,3)$ và cho biết $f(5)=3$.

### Bài 67 — Lời giải nguồn {#fs-id1165137832462}

::: {#fs-id1165137832464}
{{math:fs-id1165137832464:0}}
:::

*Giải thích bổ sung:* Tìm giá trị 1 trong cột đầu ra. Nó ứng với
đầu vào 2, nên nghiệm trong các dữ liệu đã cho là $x=2$. Không có
đầu vào nào khác trong bảng cho đầu ra 1. Bảng không cho cơ sở để
khẳng định điều gì về đầu vào ngoài bảng.

### Bài 68 — Lời giải bổ sung {#vi-sol-68}

Nguồn không kèm lời giải cho bài này. Lời giải sau được biên soạn cho
bản tiếng Việt.

Thay lần lượt các đầu vào vào $4-2x$:

| $x$ | Phép tính $f(x)$ | Kết quả |
| ---: | --- | ---: |
| −2 | $4-2(-2)=4+4$ | 8 |
| −1 | $4-2(-1)=4+2$ | 6 |
| 0 | $4-2(0)$ | 4 |
| 1 | $4-2(1)$ | 2 |
| 2 | $4-2(2)$ | 0 |

### Bài 69 — Lời giải nguồn {#fs-id1165135192892}

::: {#fs-id1165135192893 style="overflow-x: auto; max-width: 100%;" tabindex="0" role="region" aria-label="Đáp án nguồn, có thể cuộn ngang"}
{{math:fs-id1165135192893:0}}
:::

*Giải thích bổ sung:* Tính theo công thức $8-3x$, chẳng hạn
$f(-2)=8-3(-2)=14$ và $f(2)=8-6=2$.
Để dễ đọc, các giá trị trong đáp án nguồn được trình bày lại theo cột:

| $x$ | $f(x)$ |
| ---: | ---: |
| −2 | 14 |
| −1 | 11 |
| 0 | 8 |
| 1 | 5 |
| 2 | 2 |

### Bài 70 — Lời giải bổ sung {#vi-sol-70}

Nguồn không kèm lời giải cho bài này. Lời giải sau được biên soạn cho
bản tiếng Việt.

Tính bình phương đầu vào trước, rồi thực hiện phép nhân và cộng trừ:

| $x$ | Phép tính $f(x)$ | Kết quả |
| ---: | --- | ---: |
| −2 | $8(-2)^2-7(-2)+3=32+14+3$ | 49 |
| −1 | $8(-1)^2-7(-1)+3=8+7+3$ | 18 |
| 0 | $8(0)^2-7(0)+3$ | 3 |
| 1 | $8(1)^2-7(1)+3=8-7+3$ | 4 |
| 2 | $8(2)^2-7(2)+3=32-14+3$ | 21 |

### Bài 71 — Đáp án nguồn và hiệu chỉnh ký hiệu {#fs-id1165137755505}

**Lưu ý về sai sót nguồn:** Trong bản ghi ngay dưới đây, nguồn dùng
dấu $=$ với 4.414, 4.732 và 5.236. Ba số đó chỉ là giá trị gần đúng
đã làm tròn, không phải giá trị chính xác. Khối này được giữ nguyên
để đối chiếu, không phải để khẳng định ba đẳng thức sai ấy.

::: {#fs-id1165137755506 style="overflow-x: auto; max-width: 100%;" tabindex="0" role="region" aria-label="Bản ghi nguồn có sai sót làm tròn, có thể cuộn ngang"}
{{math:fs-id1165137755506:0}}
:::

*Hiệu chỉnh và giải thích bổ sung:* Tập xác định thực là
$[-3,+\infty)$ vì $x+3\ge0$. Cả năm đầu vào được yêu cầu đều thuộc
tập xác định. Các giá trị đúng là:

| $x$ | Giá trị chính xác $f(x)$ | Làm tròn đến ba chữ số sau dấu thập phân |
| ---: | --- | --- |
| −2 | $3+\sqrt1=4$ | 4 chính xác |
| −1 | $3+\sqrt2$ | $\approx4.414$ |
| 0 | $3+\sqrt3$ | $\approx4.732$ |
| 1 | $3+\sqrt4=5$ | 5 chính xác |
| 2 | $3+\sqrt5$ | $\approx5.236$ |

Ví dụ, phải viết $f(-1)=3+\sqrt2\approx4.414$, không viết
$f(-1)=4.414$. Dấu thập phân dạng chấm được giữ như nguồn để tiện
đối chiếu; dấu $\approx$ phân biệt số gần đúng với giá trị chính xác.

### Bài 72 — Lời giải bổ sung {#vi-sol-72}

Nguồn không kèm lời giải cho bài này. Lời giải sau được biên soạn cho
bản tiếng Việt.

Mẫu số khác 0 khi $x\ne-3$; tập xác định là
$\mathbb{R}\setminus\{-3\}$. Cả năm đầu vào đều hợp lệ.

| $x$ | Phép tính $f(x)$ | Kết quả chính xác |
| ---: | --- | --- |
| −2 | $\dfrac{-2-2}{-2+3}=\dfrac{-4}{1}$ | $-4$ |
| −1 | $\dfrac{-1-2}{-1+3}=\dfrac{-3}{2}$ | $-\dfrac32$ |
| 0 | $\dfrac{0-2}{0+3}=\dfrac{-2}{3}$ | $-\dfrac23$ |
| 1 | $\dfrac{1-2}{1+3}=\dfrac{-1}{4}$ | $-\dfrac14$ |
| 2 | $\dfrac{2-2}{2+3}=\dfrac05$ | $0$ |

### Bài 73 — Lời giải nguồn {#fs-id1165137770304}

::: {#fs-id1165137770305 style="overflow-x: auto; max-width: 100%;" tabindex="0" role="region" aria-label="Đáp án nguồn, có thể cuộn ngang"}
{{math:fs-id1165137770305:0}}
:::

*Giải thích bổ sung:* Với cơ số 3, số mũ âm cho nghịch đảo:
$3^{-2}=1/3^2=1/9$ và $3^{-1}=1/3$. Ngoài ra $3^0=1$,
$3^1=3$ và $3^2=9$. Số mũ âm không có nghĩa là lấy số đối.
Các đáp án nguồn được trình bày lại theo cột:

| $x$ | $f(x)$ |
| ---: | --- |
| −2 | $1/9$ |
| −1 | $1/3$ |
| 0 | 1 |
| 1 | 3 |
| 2 | 9 |

### Bài 74 — Lời giải bổ sung {#vi-sol-74}

Nguồn không kèm lời giải cho bài này. Lời giải sau được biên soạn cho
bản tiếng Việt.

Theo các công thức dùng chung ở cuối phần bài tập,
$f(1)=3(1)-2=1$ và $g(-2)=5-(-2)^2=1$.
Vì thế

$$3f(1)-4g(-2)=3(1)-4(1)=-1.$$

Đây là phép kết hợp hai giá trị bằng nhân và trừ, không phải thay
đầu vào bằng $3-4$.

### Bài 75 — Lời giải nguồn {#fs-id1165134373506}

::: {#fs-id1165134373507}
20.
:::

*Giải thích bổ sung:* Dùng đúng ba công thức ở nhóm bài 74–75:

$$f\left(\frac73\right)=3\left(\frac73\right)-2.$$

$$f\left(\frac73\right)=7-2=5.$$

$$h(-2)=-2(-2)^2+3(-2)-1.$$

$$h(-2)=-8-6-1=-15.$$

Do đó

$$f\left(\frac73\right)-h(-2)=5-(-15)=20.$$

Giữ ngoặc khi trừ $h(-2)$ để không nhầm dấu của giá trị $-15$.

## Tự kiểm tra và phần tiếp theo {#vi-next}

*Gợi ý bổ sung:* Vì sao bảng của bài 64 vẫn biểu diễn hàm số dù có
đầu ra lặp lại? Vì sao đọc $f(3)$ khác với tìm đầu vào cho đầu ra 3?
Bạn có thể giải thích dấu âm trong bài 72, số mũ âm trong bài 73,
và sự khác nhau giữa $=$ với $\approx$ trong bài 71 không?

Các kiểm tra bằng mã đi kèm đối chiếu cặp dữ liệu, số hữu tỉ chính xác
và sai số làm tròn. Chúng không tự suy ra giá trị ngoài bảng hoặc
thay thế lập luận về tập xác định.

Phần tiếp theo là nhóm bài tập *Technology*, bắt đầu tại
fs-id1165134373511. Hoàn tất nhóm bài tập số không phải là hoàn tất
mô-đun, sách hay toàn bộ bộ sách tự học.

## Nguồn và ghi công {#vi-attribution}

Bản dịch và phần bổ sung tiếng Việt độc lập, địa phương hóa vi-Latn-VN.
Nguồn: Jay Abramson và các cộng tác viên OpenStax, *Precalculus 2e*,
mô-đun m49301, UUID 11f4eacc-c348-4836-8c5b-747577d249ca;
[nguồn được ghim](https://github.com/openstax/osbooks-college-algebra-bundle/tree/789b54099106b071d1d32bfcee454fed72eb4768).
Đối chiếu với [ấn bản Bahasa Indonesia](https://github.com/KokunoYumeto/openstax-precalculus-2e-id)
0.1.0-alpha.58-reader.1. Giữ nguyên quyền ghi công của Jay Abramson,
OpenStax và các tác giả, cộng tác viên được liệt kê trong nguồn.

Văn bản nguồn, bản dịch và phần bổ sung A30 này theo
[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
Các thông báo nguồn được giữ trong thư mục notices/; các tác phẩm B40
và B80 giữ giấy phép riêng, không bị đổi giấy phép bởi bài này.
Bản dịch chuyển cách trình bày bảng, thêm sáu lời giải và công khai
hiệu chỉnh ký hiệu làm tròn như đã nêu; không thay đổi bản trích nguồn.
Không phải ấn bản chính thức hoặc được các tác giả hay tổ chức nguồn bảo trợ.
Bản dịch, lời giải bổ sung và kiểm tra được thực hiện với sự hỗ trợ của
OpenAI Codex theo yêu cầu người dùng; thông tin quy trình này không thay
thế tên tác giả gốc. Chưa có thẩm định độc lập của người bản ngữ.
