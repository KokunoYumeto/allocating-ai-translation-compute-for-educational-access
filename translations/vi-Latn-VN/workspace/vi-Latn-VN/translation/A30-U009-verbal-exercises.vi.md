---
title: "Bài tập giải thích: quan hệ và hàm số"
lang: vi-Latn-VN
subtitle: "A30 · Bài tự học 009 · Bản dịch thử nghiệm 0.1"
---

## Phạm vi và cách học {#vi-prerequisites}

Bài này dịch trọn nhóm *Verbal* trong phần bài tập mục 1.1 của mô-đun
`m49301`. Năm câu được giữ theo thứ tự nguồn. Câu 1 và câu 2 đã có trong
[U001](A30-U001-functions.vi.html#vi-exercises); chúng được nhắc lại để
nhóm bài tập này đọc được độc lập. Vì vậy, U009 bổ sung **ba bài tập mới**,
không phải năm bài mới. Số câu dưới đây là số trong nhóm này.

*Hướng dẫn bổ sung:* Ôn lại [quan hệ và hàm số](A30-U001-functions.vi.html#fs-id1165133394710),
[hàm số đơn ánh](A30-U005-one-to-one.vi.html#fs-id1165135422920),
[kiểm tra bằng đường thẳng đứng](A30-U006-graph-tests.vi.html#fs-id1165135435781)
và [kiểm tra bằng đường thẳng ngang](A30-U006-graph-tests.vi.html#fs-id1165137610952)
nếu cần. Các liên kết sang bài khác cần những tệp HTML ấy nằm cùng thư mục;
nội dung và lời giải của năm câu dưới đây đều có ngay trong tệp này.

Trong bài này, *đầu vào* được hiểu là phần tử của tập xác định; *đầu ra*
là giá trị thực sự đạt được, thuộc tập giá trị. Khi biểu diễn một quan hệ
bằng các cặp, tập đầu vào đang xét là các thành phần thứ nhất của quan hệ,
trừ khi một tập đầu vào khác được chỉ định riêng. Cách dùng từ *hàm số*
cho cả nhãn không phải số theo quy ước rộng của OpenStax đã được giải
thích trong U001.

## Bài tập giải thích {#fs-id1165137432988}

### Câu 1 — Quan hệ và hàm số {#fs-id1165137432993}

::: {#fs-id1165137432995}
::: {#fs-id1165137432998}
Quan hệ và hàm số khác nhau ở điểm nào?
:::
:::

[Xem lời giải câu 1](#fs-id1165137667225).

### Câu 2 — Đầu vào và đầu ra {#fs-id1165137870912}

::: {#fs-id1165137870914}
::: {#fs-id1165137870917}
Đầu vào và đầu ra của một hàm số khác nhau ở điểm nào?
:::
:::

[Xem lời giải bổ sung câu 2](#vi-sol-verbal-2).

### Câu 3 — Đường thẳng đứng {#fs-id1165137870922}

::: {#fs-id1165134118508}
::: {#fs-id1165134118510}
Vì sao kiểm tra bằng đường thẳng đứng cho biết đồ thị của một quan hệ
có biểu diễn một hàm số hay không?
:::
:::

[Xem lời giải câu 3](#fs-id1165134118515).

### Câu 4 — Hàm số đơn ánh {#fs-id1165135570273}

::: {#fs-id1165135570275}
::: {#fs-id1165135570277}
Làm thế nào để xác định một quan hệ có phải là hàm số đơn ánh hay không?
:::
:::

[Xem lời giải bổ sung câu 4](#vi-sol-verbal-4).

### Câu 5 — Đường thẳng ngang {#fs-id1165134391600}

::: {#fs-id1165134391602}
::: {#fs-id1165134391604}
Vì sao kiểm tra bằng đường thẳng ngang cho biết một hàm số có đơn ánh
hay không?
:::
:::

[Xem lời giải câu 5](#fs-id1165137679053).

## Lời giải và giải thích {#vi-answers}

### Câu 1 — Lời giải nguồn, đã có trong U001 {#fs-id1165137667225}

::: {#fs-id1165137667227}
Một quan hệ là một tập hợp các cặp có thứ tự. Hàm số là một loại quan hệ
đặc biệt: hai cặp phân biệt không có cùng thành phần thứ nhất. Vì vậy, mỗi
đầu vào có đúng một đầu ra.
:::

*Giải thích bổ sung:* Từ “phân biệt” làm rõ rằng việc ghi lặp lại đúng cùng
một cặp không tạo ra hai đầu ra. Còn hai cặp $(7,11)$ và $(7,9)$ cho thấy
đầu vào 7 có hai đầu ra khác nhau; quan hệ chứa cả hai cặp ấy không phải
là hàm số. Hai đầu vào khác nhau vẫn có thể cho cùng một đầu ra.

### Câu 2 — Lời giải bổ sung, đã có trong U001 {#vi-sol-verbal-2}

Đầu vào là giá trị được đưa vào quy tắc, thuộc tập xác định. Đầu ra là
giá trị mà quy tắc gán cho đầu vào ấy, thuộc tập giá trị. Trong một cặp
$(x,y)$ biểu diễn hàm số, $x$ là đầu vào và $y$ là đầu ra. Ví dụ, cặp
$(3,6)$ trong quan hệ nhân đôi cho biết đầu vào 3 dẫn tới đầu ra 6.

Nguồn không kèm lời giải cho câu này; lời giải trên được biên soạn cho
bản tiếng Việt và được dùng lại từ U001.

### Câu 3 — Lời giải nguồn {#fs-id1165134118515}

::: {#fs-id1165134118518}
Khi một đường thẳng đứng cắt đồ thị của quan hệ tại nhiều hơn một điểm,
điều đó cho thấy cùng một đầu vào có nhiều hơn một đầu ra. Để quan hệ là
một hàm số, mỗi giá trị đầu vào chỉ được có một đầu ra.
:::

*Giải thích bổ sung:* Trên đường thẳng đứng $x=a$, mọi giao điểm đều có
cùng hoành độ $a$. Hai điểm phân biệt trên đường ấy phải có hai tung độ
khác nhau. Do đó, điều kiện “mỗi đường thẳng đứng có nhiều nhất một
giao điểm với đồ thị” chính là điều kiện không có một đầu vào nhận hai
đầu ra khác nhau. Với mỗi đầu vào thuộc tập xác định, phải có đúng một
giao điểm; ngoài tập xác định thì không có giao điểm. Nếu tập đầu vào
đã được chỉ định trước, cũng cần kiểm tra rằng mỗi phần tử của tập ấy
thật sự có đầu ra.

Ví dụ bổ sung: hai điểm $(2,-1)$ và $(2,1)$ đủ bác bỏ tính chất hàm số.
Ngược lại, chỉ kiểm tra một vài đường thẳng đứng không chứng minh được
tính chất ấy cho toàn bộ một đường cong.

### Câu 4 — Lời giải bổ sung {#vi-sol-verbal-4}

Nguồn không kèm lời giải cho câu này. Lời giải sau được biên soạn cho
bản tiếng Việt.

Trước hết, kiểm tra quan hệ có phải là **hàm số**: mỗi đầu vào trong tập
xác định phải có đúng một đầu ra. Sau đó, kiểm tra tính **đơn ánh**: hai
đầu vào khác nhau phải cho hai đầu ra khác nhau. Tương đương, mỗi giá trị
thuộc tập giá trị chỉ ứng với một đầu vào.

Nếu quan hệ được cho bằng đồ thị trong mặt phẳng tọa độ, trước hết dùng
kiểm tra bằng đường thẳng đứng để xác nhận tính chất hàm số, rồi dùng
kiểm tra bằng đường thẳng ngang để xét tính đơn ánh. Phải xét toàn bộ
đồ thị trên tập xác định, không chỉ một vài điểm lấy mẫu.

Ví dụ bổ sung: quan hệ gồm $(0,1)$ và $(2,1)$ là hàm số nhưng không đơn
ánh, vì hai đầu vào 0 và 2 cùng cho đầu ra 1. Quan hệ gồm $(2,-1)$ và
$(2,1)$ không phải là hàm số, dù các đường thẳng ngang không gặp hai
điểm của quan hệ này. Vì thế, kiểm tra bằng đường thẳng ngang riêng lẻ
không đủ để gọi một quan hệ là hàm số đơn ánh.

### Câu 5 — Lời giải nguồn {#fs-id1165137679053}

::: {#fs-id1165137679055}
Khi một đường thẳng ngang cắt đồ thị của hàm số tại nhiều hơn một điểm,
điều đó cho thấy cùng một đầu ra ứng với nhiều hơn một đầu vào. Hàm số
là đơn ánh nếu mỗi đầu ra chỉ ứng với một đầu vào.
:::

*Giải thích bổ sung:* Trên đường thẳng ngang $y=b$, mọi giao điểm đều có
cùng tung độ $b$. Hai giao điểm phân biệt vì thế có hai hoành độ khác
nhau: hai đầu vào khác nhau cho cùng đầu ra $b$, trái với tính đơn ánh.
Ngược lại, nếu hai đầu vào khác nhau cho cùng đầu ra $b$, đường thẳng
$y=b$ đi qua hai điểm ấy. Vì vậy, với một quan hệ **đã là hàm số**, điều
kiện mỗi đường thẳng ngang có nhiều nhất một giao điểm với đồ thị tương
đương với tính đơn ánh. Đường thẳng ngang nằm ngoài tập giá trị không
có giao điểm, và điều đó không làm hàm số mất tính đơn ánh.

## Tự kiểm tra và phần tiếp theo {#vi-next}

*Gợi ý bổ sung:* Trong mỗi lời giải, hãy chỉ ra điều kiện nói về cùng
đầu vào và điều kiện nói về cùng đầu ra. Bạn có giải thích được vì sao
“nhiều nhất một” áp dụng cho mọi đường thẳng, còn “đúng một” chỉ áp dụng
cho các giá trị trong tập xác định hoặc tập giá trị tương ứng không?

Tiếp theo trong nguồn là nhóm bài tập *Algebraic*, bắt đầu tại
`fs-id1165134080937`. Nhóm ấy chưa được dịch trong bài này.

## Nguồn và ghi công {#vi-attribution}

Bản dịch và phần bổ sung tiếng Việt độc lập, địa phương hóa `vi-Latn-VN`.
Nguồn: Jay Abramson và các cộng tác viên OpenStax, *Precalculus 2e*,
mô-đun `m49301`, UUID `11f4eacc-c348-4836-8c5b-747577d249ca`;
[nguồn được ghim](https://github.com/openstax/osbooks-college-algebra-bundle/tree/789b54099106b071d1d32bfcee454fed72eb4768).
Đối chiếu với [ấn bản Bahasa Indonesia](https://github.com/KokunoYumeto/openstax-precalculus-2e-id)
`0.1.0-alpha.58-reader.1`. Giữ nguyên quyền ghi công của Jay Abramson,
OpenStax và các tác giả, cộng tác viên được liệt kê trong nguồn.

Văn bản nguồn, bản dịch và phần bổ sung A30 này theo
[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
Các thông báo nguồn được giữ trong thư mục `notices/`; các tác phẩm B40
và B80 giữ giấy phép riêng, không bị đổi giấy phép bởi bài này.
Không phải ấn bản chính thức hoặc được các tác giả hay tổ chức nguồn bảo trợ.
Bản dịch, lời giải bổ sung và kiểm tra được thực hiện với sự hỗ trợ của
OpenAI Codex theo yêu cầu người dùng; thông tin quy trình này không thay
thế tên tác giả gốc. Chưa có thẩm định độc lập của người bản ngữ.
