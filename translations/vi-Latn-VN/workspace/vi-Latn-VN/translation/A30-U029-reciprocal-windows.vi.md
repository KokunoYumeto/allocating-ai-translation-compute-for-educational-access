---
title: "Bài tập dùng công cụ: đồ thị trên các đoạn đã cho"
lang: vi-Latn-VN
subtitle: "A30 · Bài tự học 029 · Bản dịch thử nghiệm 0.1"
---

## Phạm vi và cách đọc {#vi-prerequisites}

Bài này dịch trọn nhóm bài tập dùng công cụ của mô-đun
m49304, gồm Bài 55–56 theo thứ tự nguồn. Bài 55 có đáp án
và hai hình nguồn; Bài 56 không kèm đáp án, nên lời giải
và hai hình vẽ cho bài ấy được ghi rõ là **bổ sung**.

*Hướng dẫn bổ sung:* Trong hai đề này, mỗi đoạn ghi cho
“cửa sổ hiển thị” là đoạn giá trị của $x$ đang xét, không
phải một tập giá trị của $y$ đã biết. Hãy tìm các đầu ra
đạt được khi $x$ chạy trên đoạn ấy. Tập giá trị này có thể
khác tập giá trị của hàm số trên toàn bộ tập xác định tự
nhiên. Cả hai đầu mút của mỗi đoạn đều được lấy.

Xét các số thực. Hai công thức trong bài đều loại $x=0$;
không nối hai phần đồ thị qua đầu vào này. Trong hình
tạo mới, khung theo $y$ chỉ giúp nhìn rõ đường cong, không
phải đáp án cho tập giá trị.

## Bài tập dùng công cụ {#fs-id1165135194497}

### Bài 55 {#fs-id1165137780865}

::: {#fs-id1165137780867}

::: {#fs-id1165135641711}

Vẽ đồ thị {{math:fs-id1165135641711:0}} trên các cửa sổ
hiển thị {{math:fs-id1165135641711:1}} và
{{math:fs-id1165135641711:2}}
Xác định tập giá trị tương ứng với mỗi cửa sổ hiển thị.
Trình bày các đồ thị.
:::

:::

::: {#fs-id1165137501974}

**Đáp án nguồn.**

::: {#fs-id1165134258632}

![Hình đáp án nguồn Bài 55 trên phía x âm: đường cong y=1/x bình phương đi lên từ gần (-0.5,4) tới gần (-0.1,100). Khung còn kéo sang phải tới trục tung; đường cong có mũi tên ở hai phía, không có các điểm đầu mút tô kín.](../assets/CNX_Precalc_Figure_01_02_221.jpg)

*Mô tả bổ sung cho hình nguồn:* Trên đoạn $[-0.5,-0.1]$,
khi đi từ trái sang phải, $y$ tăng từ 4 tới 100.
Các mốc ghi trên trục đứng của ảnh cách nhau 8 đơn vị.
:::

::: {#fs-id1165135191028}

Cửa sổ: {{math:fs-id1165135191028:0}}
tập giá trị: {{math:fs-id1165135191028:1}}
:::

::: {#fs-id1165137442910}

![Hình đáp án nguồn Bài 55 trên phía x dương: đường cong y=1/x bình phương đi xuống từ gần (0.1,100) tới gần (0.5,4). Khung bắt đầu ở trục tung; đường cong có mũi tên ở hai phía, không có các điểm đầu mút tô kín.](../assets/CNX_Precalc_Figure_01_02_222-1958.jpg)

*Mô tả bổ sung cho hình nguồn:* Trên đoạn $[0.1,0.5]$,
khi đi từ trái sang phải, $y$ giảm từ 100 tới 4.
Đường cong vẫn nằm phía trên trục hoành.
:::

::: {#fs-id1165134378637}

Cửa sổ: {{math:fs-id1165134378637:0}}
tập giá trị: {{math:fs-id1165134378637:1}}
:::

:::

*Lưu ý bổ sung về hình nguồn:* Hai ảnh được giữ nguyên.
Khung ảnh có thêm vùng ngoài đoạn $x$ trong đề và dùng
mũi tên để biểu thị sự tiếp tục của đường cong. Không đọc
biên khung hoặc đầu mũi tên như các cận thay thế cho đề bài.
Dấu ngoặc vuông trong đề cho biết phải lấy cả bốn điểm
ứng với $x=-0.5,-0.1,0.1,0.5$, dù ảnh không đánh dấu
chúng bằng điểm tô kín.

*Giải thích bổ sung:* Trên mỗi đoạn đang xét,
$0.1\le |x|\le0.5$, nên $0.01\le x^2\le0.25$.
Lấy nghịch đảo của các số dương cho
$$4=\frac1{0.25}\le\frac1{x^2}\le\frac1{0.01}=100.$$
Đặt $f(x)=1/x^2$. Bốn giá trị ở đầu mút là
$$f(-0.5)=f(0.5)=4,\qquad f(-0.1)=f(0.1)=100.$$

Không chỉ hai đầu ra 4 và 100 được nhận. Với mọi
$y\in[4,100]$, chọn $x=-1/\sqrt y$ thì
$x\in[-0.5,-0.1]$; chọn $x=1/\sqrt y$ thì
$x\in[0.1,0.5]$. Trong cả hai trường hợp,
$1/x^2=y$. Vì vậy tập giá trị trên **mỗi** đoạn đều
chính xác là $[4,100]$, không có khoảng trống ở giữa.

Đây không phải tập giá trị trên toàn bộ tập xác định
$\mathbb R\setminus\{0\}$: với mọi $y>0$, ta có thể
chọn $x=1/\sqrt y$, nên tập giá trị tự nhiên của $1/x^2$
là $(0,\infty)$.

### Bài 56 {#fs-id1165131911953}

::: {#fs-id1165137842479}

::: {#fs-id1165137842481}

Vẽ đồ thị {{math:fs-id1165137842481:0}} trên các cửa sổ
hiển thị {{math:fs-id1165137842481:1}} và
{{math:fs-id1165137842481:2}}
Xác định tập giá trị tương ứng với mỗi cửa sổ hiển thị.
Trình bày các đồ thị.
:::

:::

**Lời giải bổ sung — nguồn không kèm đáp án.**

Trên đoạn $[-0.5,-0.1]$, đặt $t=-x$, nên
$t\in[0.1,0.5]$. Từ $2\le1/t\le10$, suy ra
$-10\le1/x=-1/t\le-2$.
Khi $x$ tăng từ $-0.5$ tới $-0.1$, $y=1/x$ giảm
từ $-2$ tới $-10$. Hai điểm đầu mút là
$$\left(-0.5,\frac1{-0.5}\right)=(-0.5,-2),\qquad
\left(-0.1,\frac1{-0.1}\right)=(-0.1,-10).$$
Tập giá trị trên đoạn này là $[-10,-2]$.
Các cận của tập giá trị được viết theo thứ tự từ nhỏ tới
lớn, không phải theo thứ tự gặp khi đi từ trái sang phải
trên đồ thị.

![Đồ thị bổ sung Bài 56 cho x thuộc đoạn [-0.5,-0.1]: đường cong y=1/x giảm từ điểm kín (-0.5,-2) bên trái xuống điểm kín (-0.1,-10) bên phải; tất cả các giá trị y từ âm 10 tới âm 2 đều được nhận.](../assets/A30-U029-ex56-negative.png)

**Hình bổ sung — tạo mới cho Bài 56, không phải hình nguồn.**
Đoạn theo $x$ đúng bằng $[-0.5,-0.1]$; khung theo $y$
là $[-11,-1]$ để có khoảng trống quanh đường cong.
Hai điểm kín giữ các đầu mút theo đề. Không kéo dài phần
đồ thị đang xét ra ngoài đoạn $x$ này.

Trên đoạn $[0.1,0.5]$, lấy nghịch đảo các số dương cho
$2\le1/x\le10$. Khi $x$ tăng từ $0.1$ tới $0.5$,
$y$ giảm từ 10 tới 2. Hai điểm đầu mút là
$$(0.1,10)\quad\text{và}\quad(0.5,2).$$
Tập giá trị trên đoạn này là $[2,10]$.

![Đồ thị bổ sung Bài 56 cho x thuộc đoạn [0.1,0.5]: đường cong y=1/x giảm từ điểm kín (0.1,10) bên trái xuống điểm kín (0.5,2) bên phải; tất cả các giá trị y từ 2 tới 10 đều được nhận.](../assets/A30-U029-ex56-positive.png)

**Hình bổ sung — tạo mới cho Bài 56, không phải hình nguồn.**
Đoạn theo $x$ đúng bằng $[0.1,0.5]$; khung theo $y$
là $[1,11]$, không phải tập giá trị $[2,10]$.
Đường cong chỉ gồm các đầu vào trên đoạn đã cho.

Để kiểm tra rằng không bỏ sót giá trị trung gian, với
mỗi $y\in[-10,-2]$ chọn $x=1/y\in[-0.5,-0.1]$;
với mỗi $y\in[2,10]$ chọn $x=1/y\in[0.1,0.5]$.
Khi đó $1/x=y$. Đây là lập luận cho toàn bộ hai tập
giá trị, không chỉ là kiểm tra các đầu mút.

Nếu xét hợp của **hai đoạn trong đề**, tập giá trị là
$[-10,-2]\cup[2,10]$. Không được lấp khoảng giữa $-2$
và 2, hay đưa $x=0$ vào để nối các phần đồ thị.
Trên toàn bộ tập xác định tự nhiên
$\mathbb R\setminus\{0\}$, tập giá trị của $1/x$ là
$\mathbb R\setminus\{0\}$: đầu ra không thể bằng 0,
còn mỗi đầu ra $y\ne0$ đều có đầu vào $x=1/y$.

## Tự kiểm tra và nguồn {#vi-attribution}

*Phần bổ sung:* Hãy phân biệt ba đối tượng: đoạn đầu vào
được đề bài yêu cầu, tập đầu ra thật sự đạt được, và khung
hiển thị dùng để nhìn đồ thị. Kiểm tra giá trị ở đầu mút
giúp phát hiện sai số, nhưng tự nó chưa chứng minh rằng
mọi giá trị ở giữa đều được nhận.

Chương trình đi kèm kiểm tra việc giữ nguồn, các giá trị
mẫu, đầu mút và hai hình tạo mới. Phép thử hữu hạn không
thay thế những lập luận về tập giá trị ở trên.
Hai hình mới có mã chương trình đi kèm để tạo lại cùng
hình; hai ảnh đáp án nguồn được giữ nguyên.

Nguồn: Jay Abramson và các cộng tác viên OpenStax, *Precalculus 2e*,
mô-đun m49304, UUID 1ca91f2c-f989-40da-b8cc-b930d5c0ad36;
[phiên bản được ghim](https://github.com/openstax/osbooks-college-algebra-bundle/tree/789b54099106b071d1d32bfcee454fed72eb4768).
Đối chiếu với [ấn bản Bahasa Indonesia](https://github.com/KokunoYumeto/openstax-precalculus-2e-id)
0.1.0-alpha.58-reader.1.

Văn bản, bản dịch, phần bổ sung, hai ảnh nguồn và hai hình
tạo mới A30 theo [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
Ảnh nguồn: Copyright Rice University, OpenStax. Giữ ghi công,
chia sẻ tương tự và các thông báo trong notices/; các sách
khác giữ giấy phép riêng. Bản dịch độc lập, không được tác
giả nguồn bảo trợ; thực hiện với sự hỗ trợ của OpenAI Codex
theo yêu cầu người dùng, chưa có thẩm định của người bản ngữ.

Bài này dịch toàn bộ mục fs-id1165135194497 và dừng trước
nhóm bài tập mở rộng fs-id1165137733672. Mô-đun m49304,
sách A30 và toàn bộ lộ trình năm sách vẫn còn các phần
cần tiếp tục.
