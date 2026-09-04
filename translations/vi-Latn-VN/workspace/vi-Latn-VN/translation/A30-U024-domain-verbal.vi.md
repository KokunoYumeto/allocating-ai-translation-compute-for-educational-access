---
title: "Bài tập giải thích về tập xác định và tập giá trị"
lang: vi-Latn-VN
subtitle: "A30 · Bài tự học 024 · Bản dịch thử nghiệm 0.1"
---

## Chuẩn bị làm bài {#vi-prerequisites}

Bài này giữ tiêu đề mở đầu phần bài tập của mô-đun m49304
và dịch trọn năm câu hỏi giải thích, đánh số Bài 1–5 theo
thứ tự nguồn. Ba lời giải có sẵn được ghi **Lời giải nguồn**;
hai lời giải do bản dịch bổ sung được ghi **Lời giải bổ sung**.
Không có hình nguồn trong nhóm bài này.

*Làm rõ bổ sung:* Các câu hỏi đang xét hàm số có đầu vào và
đầu ra là số thực. Khi chỉ cho công thức, ta thường tìm tập
xác định thực lớn nhất của công thức. Nếu đề bài hoặc bối
cảnh đã quy định tập xác định, phải giữ điều kiện đó.

## Bài tập của mục {#fs-id1165135176628}

### Câu hỏi giải thích {#fs-id1165135172218}

#### Bài 1 {#fs-id1165137665109}

::: {#fs-id1165135245908}

::: {#fs-id1165135245910}

Vì sao các hàm số khác nhau có thể có tập xác định khác nhau?
:::

:::

::: {#fs-id1165134199600}

**Lời giải nguồn.**

::: {#fs-id1165135613709}

Tập xác định của hàm số phụ thuộc vào những giá trị của biến
độc lập làm cho hàm số không xác định hoặc cho giá trị không
thực.
:::

:::

*Làm rõ bổ sung về câu nguồn:* Nguồn dùng từ “imaginary”.
Trong phạm vi đang xét, đầu vào làm công thức không cho một
giá trị thực sẽ bị loại. Câu trả lời này giải thích sự hạn chế
do **công thức**; tập xác định còn có thể được chỉ định sẵn
hoặc bị giới hạn bởi bối cảnh. Vì thế không thể chỉ nhìn
biểu thức rồi bỏ qua tập xác định đã cho.

#### Bài 2 {#fs-id1165135440209}

::: {#fs-id1165135533141}

::: {#fs-id1165135533143}

Ta xác định tập xác định của một hàm số cho bởi phương trình
như thế nào?
:::

:::

**Lời giải bổ sung — nguồn không kèm đáp án.**

Nếu không có tập xác định được chỉ định riêng, hãy tìm tất cả
các đầu vào thực làm cho công thức có nghĩa và cho kết quả
thực. Xét từng phép toán và yêu cầu mọi điều kiện phải được
thỏa mãn **đồng thời**. Chẳng hạn, mẫu số phải khác 0;
biểu thức dưới dấu căn bậc chẵn phải không âm. Nếu căn ấy
nằm ở mẫu, đồng thời phải
bảo đảm mẫu khác 0. Căn bậc lẻ của một số thực tự nó không
tạo thêm hạn chế về dấu.

Sau đó giữ các điều kiện do đề bài hoặc bối cảnh đặt ra,
và viết tập đầu vào hợp lệ bằng ký hiệu tập hợp hoặc ký hiệu
khoảng. Không được đưa trở lại tập xác định một giá trị đầu
vào mà biểu thức ban đầu đã loại chỉ vì sau khi rút gọn, điều
kiện hạn chế ấy không còn hiện rõ.

#### Bài 3 {#fs-id1165137635386}

::: {#fs-id1165135390940}

::: {#fs-id1165135390942}

Giải thích vì sao tập xác định của {{math:fs-id1165135390942:0}}
khác tập xác định của {{math:fs-id1165135390942:1}}
:::

:::

::: {#fs-id1165137727146}

**Lời giải nguồn.**

::: {#fs-id1165137727148}

Không có hạn chế đối với {{math:fs-id1165137727148:0}}
trong {{math:fs-id1165137727148:1}} vì ta lấy được căn bậc ba
của mọi số thực. Vì vậy tập xác định là toàn bộ tập số thực,
{{math:fs-id1165137727148:2}}

Khi xét trong tập số thực, không thể lấy căn bậc hai của một
số âm. Do đó các giá trị {{math:fs-id1165137727148:3}}
của {{math:fs-id1165137727148:4}} bị giới hạn ở các số không âm,
và tập xác định là {{math:fs-id1165137727148:5}}
:::

:::

*Làm rõ bổ sung:* Căn bậc hai ở đây là căn chính không âm;
không tự thêm dấu $\pm$ vào giá trị của hàm số. Chẳng hạn,
$\sqrt{9}=3$, còn phương trình $y^2=9$ có hai nghiệm
$y=3$ và $y=-3$. Với căn bậc ba, số âm vẫn hợp lệ:
$\sqrt[3]{-8}=-2$.

#### Bài 4 {#fs-id1165134042454}

::: {#fs-id1165134042457}

::: {#fs-id1165137438149}

Khi mô tả các tập số bằng ký hiệu khoảng, khi nào ta dùng
dấu ngoặc tròn và khi nào dùng dấu ngoặc vuông?
:::

:::

**Lời giải bổ sung — nguồn không kèm đáp án.**

Ở một đầu mút hữu hạn, dùng ngoặc tròn nếu **không lấy**
đầu mút, và dùng ngoặc vuông nếu **lấy** đầu mút.
Chẳng hạn, với $a<b$:

- $(a,b)$ không lấy cả $a$ lẫn $b$.
- $[a,b]$ lấy cả hai đầu mút.
- $(a,b]$ không lấy $a$ nhưng lấy $b$.
- $[a,b)$ lấy $a$ nhưng không lấy $b$.

Luôn dùng ngoặc tròn ở phía $-\infty$ hoặc $\infty$,
vì chúng không phải số thực để đưa vào tập hợp. Ví dụ,
$[0,\infty)$ lấy 0 và mọi số thực dương, nhưng không có
một “phần tử vô cực”.

#### Bài 5 {#fs-id1165134211324}

::: {#fs-id1165137446310}

::: {#fs-id1165137446313}

Ta vẽ đồ thị của một hàm số cho bởi nhiều công thức như thế nào?
:::

:::

::: {#fs-id1165137574335}

**Lời giải nguồn.**

::: {#fs-id1165135415726}

Vẽ đồ thị từng công thức trên phần tập xác định tương ứng.
Giữ thống nhất thang chia của trục {{math:fs-id1165135415726:0}}
và thang chia của trục {{math:fs-id1165135415726:1}}
giữa các đồ thị thành phần. Dùng điểm tô kín cho đầu mút
được lấy và vòng tròn rỗng cho đầu mút bị loại.
Dùng mũi tên để chỉ hướng về {{math:fs-id1165135415726:2}}
hoặc {{math:fs-id1165135415726:3}}
Gộp các đồ thị lại để được đồ thị của hàm số cho bởi nhiều
công thức.
:::

:::

*Làm rõ bổ sung:* Sự thống nhất thang chia là giữa các đồ thị
thành phần; không bắt buộc một đơn vị trên trục ngang và một
đơn vị trên trục đứng có cùng độ dài trên giấy.
Chỉ vẽ tiếp một nhánh và thêm mũi tên khi cả công thức lẫn
điều kiện của nhánh cho phép phần đồ thị ấy tiếp tục vô hạn
theo hướng đó. Không tự kéo dài qua một đầu mút bị loại.

*Nhắc lại bổ sung:* Mỗi đầu vào trong tập xác định phải cho
đúng một đầu ra. Nếu điều kiện hai nhánh chồng lấn, chúng
phải cho cùng giá trị tại mọi đầu vào thuộc phần giao.

## Tự kiểm tra và nguồn {#vi-attribution}

*Phần bổ sung:* Đối chiếu điều kiện của phép toán với tập
xác định đã cho; sau đó kiểm tra từng đầu mút. Chương trình
đi kèm kiểm tra việc giữ nguồn và một số giá trị mẫu.
Kiểm tra hữu hạn không thay thế lập luận về toàn bộ tập số.

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

Bài này giữ tiêu đề phần bài tập fs-id1165135176628 và dịch
trọn nhóm câu hỏi fs-id1165135172218, dừng trước nhóm đại số
fs-id1165137771069. Những nhóm bài tập còn lại của mô-đun
m49304, sách A30 và lộ trình năm sách vẫn cần tiếp tục.
