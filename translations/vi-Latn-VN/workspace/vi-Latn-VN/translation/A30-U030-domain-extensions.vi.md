---
title: "Bài tập mở rộng về tập xác định và tập giá trị"
lang: vi-Latn-VN
subtitle: "A30 · Bài tự học 030 · Bản dịch thử nghiệm 0.1"
---

## Chuẩn bị làm bài {#vi-prerequisites}

*Hướng dẫn bổ sung:* Khi tìm tập giá trị, cần kiểm tra hai
điều: hàm số không cho đầu ra nằm ngoài tập đã nêu, và mọi
giá trị trong tập ấy đều thực sự được nhận. Chỉ tính vài
giá trị của hàm số chưa đủ để kết luận về toàn bộ tập giá
trị.

Các bài dưới đây được đánh số 57–59 theo thứ tự bài tập
của mô-đun. Bài 57 và Bài 59 có đáp án nguồn; lời giải
Bài 58 do bản dịch bổ sung và được ghi rõ. Mỗi bài là một
câu hỏi riêng, không buộc dùng cùng một hàm số cho cả ba
bài.

Trong Bài 57, lấy giá trị tuyệt đối của đầu ra nghĩa là
thay $f(x)$ bằng $|f(x)|$, giữ nguyên tập xác định của
$f$. “Không âm” bao gồm cả 0.

## Bài tập mở rộng {#fs-id1165137733672}

### Bài 57 {#fs-id1165137442197}

::: {#fs-id1165133221851}
::: {#fs-id1165133221853}
Giả sử tập giá trị của hàm số {{math:fs-id1165133221853:0}}
là {{math:fs-id1165133221853:1}}
Đâu là tập giá trị của {{math:fs-id1165133221853:2}}
:::
:::

[Xem đáp án Bài 57](#fs-id1165134555582).

### Bài 58 {#fs-id1165137679047}

::: {#fs-id1165137679049}
::: {#fs-id1165133410011}
Hãy xây dựng một hàm số có tập giá trị là toàn bộ các số
thực không âm.
:::
:::

[Xem lời giải Bài 58](#vi-answer-58).

### Bài 59 {#fs-id1165135209378}

::: {#fs-id1165135209380}
::: {#fs-id1165137645593}
Hãy xây dựng một hàm số có tập xác định là tập các số thực
thỏa mãn {{math:fs-id1165137645593:0}}
:::
:::

[Xem đáp án Bài 59](#fs-id1165133210812).

## Đáp án và lời giải {#vi-answers}

### Bài 57 {#fs-id1165134555582}

::: {#fs-id1165134555584}
**Đáp án nguồn:** {{math:fs-id1165134555584:0}}.
:::

*Giải thích bổ sung:* Gọi $X$ là tập xác định của $f$.
Với mọi $x\in X$, ta có $-5\le f(x)\le8$.
Nếu $f(x)<0$ thì $|f(x)|\le5$; nếu $f(x)\ge0$ thì
$|f(x)|=f(x)\le8$. Vì thế mọi đầu ra mới đều thuộc
$[0,8]$.

Ngược lại, lấy một số $y$ bất kỳ trong $[0,8]$.
Vì $y$ thuộc tập giá trị đã cho của $f$, tồn tại một
$x\in X$ sao cho $f(x)=y$. Do $y\ge0$, ta có
$|f(x)|=y$. Như vậy **mọi** giá trị trong $[0,8]$ đều
được nhận, kể cả hai đầu mút 0 và 8.

Lập luận này không cần biết công thức của $f$ hoặc giả
thiết $f$ liên tục. Các số 0 và 8 ở đây là đầu ra; không
suy ra rằng $f(0)=0$ hay $f(8)=8$.

### Bài 58 {#vi-answer-58}

**Lời giải bổ sung — nguồn không kèm đáp án.**

Một lựa chọn là

$$f(x)=x^2,\qquad x\in\mathbb{R}.$$

Với mọi đầu vào thực, $x^2\ge0$, nên hàm số không nhận
giá trị âm. Để thấy hàm số nhận được **tất cả** các giá
trị không âm, lấy $y\ge0$ bất kỳ và chọn đầu vào
$x=\sqrt{y}$. Khi đó

$$f(\sqrt{y})=(\sqrt{y})^2=y.$$

Vậy tập giá trị chính xác là $[0,\infty)$, không chỉ là
một tập con của tập các số thực không âm. Đặc biệt,
$f(0)=0$, nên đầu ra 0 được lấy. Có nhiều hàm số khác cũng
đáp ứng yêu cầu; ở đây chỉ cần xây dựng một hàm số.

### Bài 59 {#fs-id1165133210812}

::: {#fs-id1165137779064}
**Đáp án nguồn:** Có nhiều đáp án. Một hàm số như vậy là
{{math:fs-id1165137779064:0}}
:::

*Giải thích bổ sung:* Xét tập xác định lớn nhất trong các
số thực mà công thức này cho phép. Cần đồng thời thỏa
mãn hai điều kiện:

- Biểu thức dưới dấu căn không âm: $x-2\ge0$.
- Mẫu số khác 0: $\sqrt{x-2}\ne0$.

Điều kiện thứ nhất cho $x\ge2$. Trong các giá trị ấy,
điều kiện thứ hai loại $x=2$. Kết hợp lại, ta được

$$x>2,\qquad X=(2,\infty).$$

Ngược lại, với mọi $x>2$, ta có $x-2>0$, nên căn bậc hai
là một số thực dương và mẫu số khác 0. Vì vậy công thức
xác định với mọi đầu vào trong $(2,\infty)$ và không xác
định với đầu vào thực nào khác. Không thể chỉ giữ điều
kiện $x\ge2$: tại $x=2$, mẫu số bằng 0.

## Nguồn và bước tiếp theo {#vi-attribution}

Nguồn: Jay Abramson và các cộng tác viên OpenStax,
*Precalculus 2e*, mô-đun m49304, UUID
1ca91f2c-f989-40da-b8cc-b930d5c0ad36;
[phiên bản được ghim](https://github.com/openstax/osbooks-college-algebra-bundle/tree/789b54099106b071d1d32bfcee454fed72eb4768).
Đối chiếu với [ấn bản Bahasa Indonesia](https://github.com/KokunoYumeto/openstax-precalculus-2e-id)
0.1.0-alpha.58-reader.1. Giữ nguyên các mã nguồn và công
thức; ghi rõ lời giải mới và những giải thích bổ sung.

Văn bản, bản dịch và phần bổ sung A30 theo
[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
Copyright Rice University, OpenStax. Giữ ghi công, thông
báo thay đổi, chia sẻ tương tự và các thông báo riêng
trong notices/; các sách khác giữ giấy phép riêng. Đây là
bản dịch độc lập, không được tác giả nguồn bảo trợ; thực
hiện với sự hỗ trợ của OpenAI Codex theo yêu cầu người
dùng, chưa có thẩm định của người bản ngữ.

Mã đi kèm kiểm tra việc giữ nguồn, một số phép tính chính
xác và các điều kiện xác định. Những phép thử hữu hạn
không thay thế các lập luận về toàn bộ tập xác định hoặc
tập giá trị ở trên.

Bài này dịch trọn nhóm mở rộng fs-id1165137733672, gồm
Bài 57–59, và dừng trước nhóm ứng dụng thực tế
fs-id1165137832031. Phần còn lại của mô-đun, sách A30 và
toàn bộ nhiệm vụ năm sách vẫn cần tiếp tục.
