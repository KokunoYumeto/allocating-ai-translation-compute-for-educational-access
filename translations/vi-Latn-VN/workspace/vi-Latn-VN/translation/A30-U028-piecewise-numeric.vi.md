---
title: "Bài tập: tính giá trị và tìm tập xác định"
lang: vi-Latn-VN
subtitle: "A30 · Bài tự học 028 · Bản dịch thử nghiệm 0.1"
---

## Phạm vi và cách làm {#vi-prerequisites}

Bài này dịch trọn nhóm bài tập số của mô-đun m49304,
gồm chín bài theo thứ tự nguồn là Bài 46–54. Sáu bài đầu
yêu cầu tính giá trị tại bốn đầu vào; ba bài cuối yêu cầu
tìm tập xác định. Nguồn có đáp án cho bốn bài; năm lời giải
còn lại được viết mới và đánh dấu là **bổ sung**.

*Hướng dẫn bổ sung:* Với hàm số cho bởi nhiều công thức,
trước hết xét điều kiện của đầu vào để chọn nhánh, rồi mới
thay biến bằng đầu vào trong biểu thức của nhánh ấy. Dấu $<$ khác dấu
$\le$; dấu $>$ khác dấu $\ge$. Không chọn nhánh chỉ vì
biểu thức của nó vẫn tính được tại đầu vào đang xét.

*Nhắc lại bổ sung:* Xét các số thực. Tập xác định của hàm số
là hợp các tập đầu vào hợp lệ của từng nhánh. Trong một nhánh,
phải đồng thời thỏa điều kiện được chỉ định và điều kiện
để biểu thức có nghĩa. Việc các biểu thức là đa thức không
cho phép bỏ những giới hạn đã chỉ định cho các nhánh.

## Bài tập số {#fs-id1165134118450}

::: {#fs-id1165135188383}

Với các bài tập sau, cho hàm số {{math:fs-id1165135188383:0}}
hãy tính {{math:fs-id1165135188383:1}} và {{math:fs-id1165135188383:2}}
:::

### Bài 46 {#fs-id1165137471865}

::: {#fs-id1165137471867}
::: {#fs-id1165134043731}

{{math:fs-id1165134043731:0}}
:::
:::

[Lời giải Bài 46](#vi-sol-46)

### Bài 47 {#fs-id1165134122954}

::: {#fs-id1165134122956}
::: {#fs-id1165135168423}

{{math:fs-id1165135168423:0}}
:::
:::

[Lời giải Bài 47](#fs-id1165137804494)

### Bài 48 {#fs-id1165137556768}

::: {#fs-id1165137423742}
::: {#fs-id1165137423744}

{{math:fs-id1165137423744:0}}
:::
:::

[Lời giải Bài 48](#vi-sol-48)

::: {#fs-id1165137469026}

Với các bài tập sau, cho hàm số {{math:fs-id1165137469026:0}}
hãy tính {{math:fs-id1165137469026:1}} và {{math:fs-id1165137469026:2}}
:::

### Bài 49 {#fs-id1165134380351}

::: {#fs-id1165134380353}
::: {#fs-id1165137678245}

{{math:fs-id1165137678245:0}}
:::
:::

[Lời giải Bài 49](#fs-id1165137476514)

### Bài 50 {#fs-id1165137693713}

::: {#fs-id1165137679373}
::: {#fs-id1165137679375}

{{math:fs-id1165137679375:0}}
:::
:::

[Lời giải Bài 50](#vi-sol-50)

### Bài 51 {#fs-id1165137715004}

::: {#fs-id1165137715006}
::: {#fs-id1165137715008}

{{math:fs-id1165137715008:0}}
:::
:::

[Lời giải Bài 51](#fs-id1165135699157)

::: {#fs-id1165137837869}

Với các bài tập sau, hãy viết tập xác định của hàm số cho
bởi nhiều công thức bằng ký hiệu khoảng.
:::

### Bài 52 {#fs-id1165137837872}

::: {#fs-id1165135341427}
::: {#fs-id1165135341429}

{{math:fs-id1165135341429:0}}
:::
:::

[Lời giải Bài 52](#vi-sol-52)

### Bài 53 {#fs-id1165137704661}

::: {#fs-id1165137704664}
::: {#fs-id1165137704666}

{{math:fs-id1165137704666:0}}
:::
:::

[Lời giải Bài 53](#fs-id1165135420410)

### Bài 54 {#fs-id1165137772429}

::: {#fs-id1165137772431}
::: {#fs-id1165137675983}

{{math:fs-id1165137675983:0}}
:::
:::

[Lời giải Bài 54](#vi-sol-54)

## Đáp án và giải thích {#vi-solutions}

### Lời giải Bài 46 {#vi-sol-46}

**Lời giải bổ sung — nguồn không kèm đáp án:**

Chọn nhánh theo điều kiện của từng đầu vào:

- Vì $-3<-2$, dùng $x+1$: $f(-3)=-3+1=-2$.
- Vì $-2\ge-2$, dùng $-2x-3$: $f(-2)=-2(-2)-3=1$.
- Vì $-1\ge-2$, dùng $-2x-3$: $f(-1)=-2(-1)-3=-1$.
- Vì $0\ge-2$, dùng $-2x-3$: $f(0)=-2\cdot0-3=-3$.

Tại biên $x=-2$, phải chọn nhánh thứ hai vì điều kiện của
nhánh này có dấu “lớn hơn hoặc bằng”.

[Trở lại Bài 46](#fs-id1165137471865)

### Lời giải Bài 47 {#fs-id1165137804494}

**Đáp án nguồn:**

::: {#fs-id1165137804496}

{{math:fs-id1165137804496:0}}
:::

*Giải thích bổ sung:* Đầu vào $-3$ thỏa $x\le-3$, nên
nhận giá trị hằng 1. Các đầu vào $-2$, $-1$ và $0$ đều
lớn hơn $-3$, nên cùng nhận giá trị hằng 0. Dấu bằng ở
nhánh thứ nhất quyết định $f(-3)=1$, không phải 0.

[Trở lại Bài 47](#fs-id1165134122954)

### Lời giải Bài 48 {#vi-sol-48}

**Lời giải bổ sung — nguồn không kèm đáp án:**

Ba đầu vào $-3$, $-2$, $-1$ đều thỏa $x\le-1$, nên dùng
$-2x^2+3$. Đầu vào 0 thỏa $x>-1$, nên dùng $5x-7$.

- $f(-3)=-2(-3)^2+3=-18+3=-15$.
- $f(-2)=-2(-2)^2+3=-8+3=-5$.
- $f(-1)=-2(-1)^2+3=-2+3=1$.
- $f(0)=5\cdot0-7=-7$.

Khi thay một số âm vào $x^2$, đặt số đó trong ngoặc rồi
bình phương. Hệ số $-2$ vẫn ở ngoài bình phương.

[Trở lại Bài 48](#fs-id1165137556768)

### Lời giải Bài 49 {#fs-id1165137476514}

**Đáp án nguồn:**

::: {#fs-id1165137476516}

{{math:fs-id1165137476516:0}}
:::

*Giải thích bổ sung:* Đầu vào $-1$ dùng nhánh $7x+3$;
các đầu vào $0$, $2$, $4$ dùng nhánh $7x+6$.

- $f(-1)=7(-1)+3=-4$.
- $f(0)=7\cdot0+6=6$.
- $f(2)=7\cdot2+6=20$.
- $f(4)=7\cdot4+6=34$.

Tại 0, chọn nhánh thứ hai, không thay vào $7x+3$.

[Trở lại Bài 49](#fs-id1165134380351)

### Lời giải Bài 50 {#vi-sol-50}

**Lời giải bổ sung — nguồn không kèm đáp án:**

Các đầu vào $-1$ và $0$ nhỏ hơn 2, nên dùng $x^2-2$.
Các đầu vào $2$ và $4$ thuộc nhánh $x\ge2$, nên dùng
$4+|x-5|$.

- $f(-1)=(-1)^2-2=-1$.
- $f(0)=0^2-2=-2$.
- $f(2)=4+|2-5|=4+3=7$.
- $f(4)=4+|4-5|=4+1=5$.

Phải chọn nhánh trước rồi mới tính giá trị tuyệt đối.
Tại $x=2$, không dùng công thức của nhánh $x<2$.

[Trở lại Bài 50](#fs-id1165137693713)

### Lời giải Bài 51 {#fs-id1165135699157}

**Đáp án nguồn:**

::: {#fs-id1165137401550}

{{math:fs-id1165137401550:0}}
:::

*Giải thích bổ sung:* Ba nhánh có điều kiện khác nhau:

- Vì $-1<0$, $f(-1)=5(-1)=-5$.
- Vì $0$ và $2$ đều thuộc đoạn $[0,3]$, $f(0)=f(2)=3$.
- Vì $4>3$, $f(4)=4^2=16$.

Hai đầu mút 0 và 3 đều được nhánh hằng nhận.

[Trở lại Bài 51](#fs-id1165137715004)

### Lời giải Bài 52 {#vi-sol-52}

**Lời giải bổ sung — nguồn không kèm đáp án:**

Nhánh thứ nhất nhận $x<-2$; nhánh thứ hai nhận
$x\ge-2$. Cả hai biểu thức là đa thức, nên không có điều
kiện xác định nào khác. Hợp hai phần đầu vào là
$$(-\infty,-2)\cup[-2,\infty)=(-\infty,\infty).$$
Vậy tập xác định là toàn bộ tập số thực; đầu vào $-2$
được nhánh thứ hai nhận.

[Trở lại Bài 52](#fs-id1165137837872)

### Lời giải Bài 53 {#fs-id1165135420410}

**Đáp án nguồn:**

::: {#fs-id1165135570357}

Tập xác định: {{math:fs-id1165135570357:0}}
:::

*Giải thích bổ sung:* Các nhánh được chỉ định cho $x<1$
và $x>1$, nên không nhánh nào nhận $x=1$. Mặc dù cả hai
biểu thức đa thức đều tính được tại 1, điều đó không cho
phép tự thêm 1 vào tập xác định đã được chỉ định.

[Trở lại Bài 53](#fs-id1165137704661)

### Lời giải Bài 54 {#vi-sol-54}

**Lời giải bổ sung — nguồn không kèm đáp án:**

Nhánh thứ nhất nhận $x<0$; nhánh thứ hai nhận $x\ge2$.
Các biểu thức đều là đa thức, nên không có điều kiện loại
trừ nào thêm bên trong từng nhánh. Tập xác định là
$$(-\infty,0)\cup[2,\infty).$$
Không đầu vào nào thuộc $[0,2)$ được nhận. Đầu mút 0 bị
loại, còn đầu mút 2 được lấy theo dấu $x\ge2$.

[Trở lại Bài 54](#fs-id1165137772429)

## Tự kiểm tra và nguồn {#vi-attribution}

*Phần bổ sung:* Hãy kiểm tra lại nhánh được chọn tại các
đầu vào bằng đúng mốc phân chia, rồi kiểm tra dấu khi thay
số âm và khi tính giá trị tuyệt đối. Chương trình đi kèm
kiểm tra 24 giá trị được yêu cầu, những điều kiện biên và
việc giữ nội dung nguồn. Một số đầu vào thử không thay
thế lập luận về toàn bộ tập xác định.

Nguồn: Jay Abramson và các cộng tác viên OpenStax, *Precalculus 2e*,
mô-đun m49304, UUID 1ca91f2c-f989-40da-b8cc-b930d5c0ad36;
[phiên bản được ghim](https://github.com/openstax/osbooks-college-algebra-bundle/tree/789b54099106b071d1d32bfcee454fed72eb4768).
Đối chiếu với [ấn bản Bahasa Indonesia](https://github.com/KokunoYumeto/openstax-precalculus-2e-id)
0.1.0-alpha.58-reader.1.

Văn bản, bản dịch và phần bổ sung A30 theo
[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
Giữ ghi công, chia sẻ tương tự và các thông báo trong notices/;
các sách khác giữ giấy phép riêng. Bản dịch độc lập, không được
tác giả nguồn bảo trợ; thực hiện với sự hỗ trợ của OpenAI Codex
theo yêu cầu người dùng, chưa có thẩm định của người bản ngữ.

Bài này dịch toàn bộ mục fs-id1165134118450 và dừng trước
nhóm bài tập dùng công cụ fs-id1165135194497. Không có yêu
cầu vẽ đồ thị trong chín bài này. Mô-đun m49304, sách A30
và toàn bộ lộ trình năm sách vẫn còn các phần cần tiếp tục.
