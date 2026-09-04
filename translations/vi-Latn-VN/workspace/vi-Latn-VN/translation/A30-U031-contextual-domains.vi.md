---
title: "Ứng dụng thực tế: chọn tập xác định theo bối cảnh"
lang: vi-Latn-VN
subtitle: "A30 · Bài tự học 031 · Bản dịch thử nghiệm 0.1"
---

## Phạm vi và cách làm {#vi-prerequisites}

Bài này dịch trọn nhóm ứng dụng thực tế của mô-đun
m49304, gồm Bài 60–61. Phần nội dung đang hiển thị của
nguồn không kèm lời giải cho hai bài này. Các lời giải
dưới đây là **bổ sung**. Tệp nguồn còn có một đáp án Bài 60
nằm trong chú thích XML, không hiển thị; ghi chú sau lời
giải phân biệt rõ nội dung lưu trữ ấy.

*Hướng dẫn bổ sung:* Một công thức có thể tính được với
mọi số thực, nhưng không phải mọi đầu vào ấy đều có ý
nghĩa trong bài toán. Cần xét ý nghĩa của biến, đơn vị đo
và những giới hạn được nêu. Thời gian có thể nhận giá trị
không nguyên; số lượng sản phẩm nguyên chiếc phải là số
nguyên không âm.

## Ứng dụng thực tế {#fs-id1165137832031}

### Bài 60 {#fs-id1165135511303}

::: {#fs-id1165135511305}
::: {#fs-id1165135336103}

Độ cao {{math:fs-id1165135336103:0}} của một vật được
phóng là hàm số của thời gian {{math:fs-id1165135336103:1}}
mà vật ở trên không. Độ cao, tính bằng foot (ft), sau
{{math:fs-id1165135336103:2}} giây được cho bởi hàm số
{{math:fs-id1165135336103:3}}
Tập xác định của hàm số là gì? Tập xác định đó có ý nghĩa
gì trong bối cảnh bài toán?
:::
:::

[Xem lời giải Bài 60](#vi-sol-60).

### Bài 61 {#fs-id1165137406705}

::: {#fs-id1165137406708}
::: {#fs-id1165133045371}

Chi phí, tính bằng đô la, để sản xuất
{{math:fs-id1165133045371:0}} sản phẩm được cho bởi hàm số
{{math:fs-id1165133045371:1}}
:::

::: {#fs-id1165137862357}

- ⓐ Chi phí cố định được xác định khi không sản xuất sản
  phẩm nào. Hãy tìm chi phí cố định.
- ⓑ Chi phí sản xuất 25 sản phẩm là bao nhiêu?
- ⓒ Giả sử chi phí tối đa được phép là 1500 đô la.
  Đâu là tập xác định và tập giá trị của hàm chi phí
  {{math:fs-id1165137862357:0}}
:::
:::

[Xem lời giải Bài 61](#vi-sol-61).

## Lời giải bổ sung {#vi-solutions}

### Lời giải Bài 60 {#vi-sol-60}

**Lời giải bổ sung — phần nội dung hiển thị của nguồn
không kèm đáp án.**

Nếu chỉ xét biểu thức đa thức, tập xác định lớn nhất
trong các số thực là $\mathbb R$. Nhưng ở đây $t$ là
thời gian tính từ lúc phóng, nên $t\ge0$, và ta theo dõi
vật từ lúc rời mặt đất đến lúc trở lại mặt đất.

Phân tích biểu thức độ cao:
$$h(t)=-16t^2+96t=16t(6-t).$$
Vật ở mặt đất khi
$$h(t)=0\quad\Longleftrightarrow\quad t=0\ \text{hoặc}\ t=6.$$

Với $0<t<6$, hai thừa số $t$ và $6-t$ đều dương, nên
$h(t)>0$. Tại $t=0$ và $t=6$, độ cao bằng 0. Nếu $t>6$,
công thức cho độ cao âm; phần đó không mô tả chuyển động
đang xét sau khi vật đã trở lại mặt đất. Các giá trị
$t<0$ cũng nằm ngoài khoảng thời gian kể từ lúc phóng.

Vì vậy, khi lấy cả hai thời điểm biên, tập xác định theo
bối cảnh là
$$D=[0,6],$$
với $t$ đo bằng giây. Vật rời mặt đất tại giây 0 và trở
lại mặt đất sau 6 giây. Mọi thời điểm giữa hai mốc đều
được xét, không chỉ các giây nguyên.

*Phân biệt bổ sung:* Nếu chỉ xét những thời điểm vật
ở **cao hơn** mặt đất thì $h(t)>0$ ứng với $(0,6)$.
Đoạn $[0,6]$ ở trên mô tả toàn bộ khoảng theo dõi, gồm cả
thời điểm phóng và thời điểm trở lại mặt đất. Độ cao vẫn
được đo bằng ft như trong nguồn; không đổi hệ đơn vị của
công thức.

*Ghi chú bổ sung về nguồn:* Cả tệp tiếng Anh và tệp
tiếng Indonesia đều giữ một đáp án bên trong chú thích
XML, nên đáp án ấy không thuộc nội dung đang hiển thị.
Nội dung lưu trữ này nêu tập xác định $[0,6]$ và thời
gian 6 giây từ lúc vật rời mặt đất đến lúc trở lại mặt
đất. Chú thích được giữ nguyên trong bản trích nguồn,
không được chuyển thành đáp án nguồn đang hiển thị.
Lập luận chi tiết ở trên do bản dịch bổ sung.

[Trở lại Bài 60](#fs-id1165135511303).

### Lời giải Bài 61 {#vi-sol-61}

**Lời giải bổ sung — phần nội dung hiển thị của nguồn
không kèm đáp án.**

ⓐ Khi không sản xuất sản phẩm nào, $x=0$, nên
$$C(0)=10\cdot0+500=500.$$
Chi phí cố định là **500 đô la**. Giá trị này không
bằng 0 dù số sản phẩm bằng 0.

ⓑ Với 25 sản phẩm,
$$C(25)=10\cdot25+500=750.$$
Chi phí là **750 đô la**.

ⓒ Điều kiện chi phí không vượt quá 1500 đô la cho
$$10x+500\le1500\quad\Longleftrightarrow\quad x\le100.$$
Đồng thời, số sản phẩm không thể âm.

Trong cách hiểu đếm từng sản phẩm nguyên chiếc, $x$ là
số nguyên. Vì vậy tập xác định là
$$D=\{0,1,2,\ldots,100\}
=\{x\in\mathbb Z\mid0\le x\le100\}.$$
Số 0 được lấy vì đề đã xét trường hợp không sản xuất;
số 100 được lấy vì $C(100)=1500$, đúng mức tối đa được
phép. Không có giới hạn công suất nào khác được cho
trong đề.

Tập giá trị tương ứng, tính bằng đô la, là
$$R=\{500,510,520,\ldots,1500\}.$$
Cụ thể,
$$R=\{500+10n\mid n\in\mathbb Z,\ 0\le n\le100\}.$$
Mỗi đầu vào nguyên $n$ trong tập xác định cho đúng giá
trị $500+10n$, và mỗi giá trị vừa liệt kê đều được nhận
tại đầu vào đó. Vì thế đây là toàn bộ tập giá trị, không
chỉ là hai cận 500 và 1500.

Tập này không phải đoạn $[500,1500]$: chẳng hạn, chi phí
505 đô la sẽ đòi hỏi $x=0.5$ sản phẩm, không phải số
nguyên chiếc.

*Phương án mô hình hóa bổ sung:* Nếu thay cách đếm sản
phẩm nguyên chiếc bằng mô hình liên tục, cho phép $x$
là mọi số thực giữa 0 và 100, thì tập xác định là
$[0,100]$ và tập giá trị là $[500,1500]$.
Thật vậy, mỗi $y\in[500,1500]$ cho đầu vào
$x=(y-500)/10\in[0,100]$ và $C(x)=y$.
Đây là một giả thiết mô hình hóa khác, không phải lý do
để tự thêm số lượng sản phẩm lẻ vào tập đếm nguyên chiếc.
Hai cách hiểu cần được ghi rõ, không dùng lẫn với nhau.

[Trở lại Bài 61](#fs-id1165137406705).

## Tự kiểm tra và nguồn {#vi-attribution}

*Phần bổ sung:* Trước khi viết tập xác định, hãy hỏi:
biến biểu thị thời gian hay số lượng đếm được? Các đầu
mút có được lấy không? Công thức có còn mô tả đúng bối
cảnh ở ngoài khoảng đang xét không? Khi viết tập giá trị,
hãy phân biệt một dãy hữu hạn các giá trị với cả một đoạn
số thực.

Chương trình đi kèm kiểm tra việc giữ nguồn, sự tách
biệt giữa nội dung hiển thị và chú thích XML, các phép
tính độ cao và chi phí, cùng toàn bộ 101 số lượng sản
phẩm được phép trong cách hiểu nguyên chiếc. Các đầu
vào thử của mô hình thời gian không thay thế lập luận
trên toàn bộ đoạn $[0,6]$.

Nguồn: Jay Abramson và các cộng tác viên OpenStax,
*Precalculus 2e*, mô-đun m49304, UUID
1ca91f2c-f989-40da-b8cc-b930d5c0ad36;
[phiên bản được ghim](https://github.com/openstax/osbooks-college-algebra-bundle/tree/789b54099106b071d1d32bfcee454fed72eb4768).
Đối chiếu với [ấn bản Bahasa Indonesia](https://github.com/KokunoYumeto/openstax-precalculus-2e-id)
0.1.0-alpha.58-reader.1.

Văn bản, bản dịch và phần bổ sung A30 theo
[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
Copyright Rice University, OpenStax. Giữ ghi công, chia
sẻ tương tự và các thông báo riêng trong notices/; các
sách khác giữ giấy phép riêng. Bản dịch độc lập, không
được tác giả nguồn bảo trợ; thực hiện với sự hỗ trợ của
OpenAI Codex theo yêu cầu người dùng, chưa có thẩm định
của người bản ngữ.

Bài này dịch toàn bộ mục fs-id1165137832031, kết thúc
phần bài tập của mô-đun và dừng trước bảng thuật ngữ.
Không có yêu cầu vẽ đồ thị trong hai bài này. Việc hoàn
thành bài tự học này không đồng nghĩa với hoàn thành
mô-đun m49304, sách A30 hay toàn bộ nhiệm vụ năm sách.
