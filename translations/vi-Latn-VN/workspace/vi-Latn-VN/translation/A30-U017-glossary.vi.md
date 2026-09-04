---
title: "Bảng thuật ngữ: hàm số và phép kiểm tra đồ thị"
lang: vi-Latn-VN
subtitle: "A30 · Bài tự học 017 · Bản dịch thử nghiệm 0.1"
---

## Phạm vi và cách đọc {#vi-prerequisites}

Bài này dịch đủ 11 mục của bảng thuật ngữ ở cuối mô-đun m49301,
theo đúng thứ tự nguồn, sau phần bài tập ứng dụng thực tế.
Các định nghĩa bên dưới là bản dịch nguồn; mọi ghi chú và ví dụ
được biên soạn thêm đều có nhãn bổ sung. Bảng thuật ngữ nguồn
không có công thức, bài tập, lời giải hay hình.

*Lưu ý thuật ngữ bổ sung:* Theo cách dùng rộng của OpenStax trong
mô-đun này, đầu vào và đầu ra có thể là số hoặc những đối tượng
như tên gọi, nhãn. Bản dịch giữ từ “hàm số” nhất quán với các bài
trước; không vì vậy mà giới hạn mọi quan hệ trong bảng thuật ngữ
vào các cặp số thực. “Tập xác định” còn được gọi là “miền xác định”;
“tập giá trị” còn được gọi là “miền giá trị”.

## Các thuật ngữ {#vi-glossary}

### Biến phụ thuộc {#fs-id1165137758543}

::: {#fs-id1165137758548}
Biến đầu ra.
:::

### Tập xác định {#fs-id1165137758552}

::: {#fs-id1165137932576}
Tập hợp tất cả các giá trị đầu vào có thể có của một quan hệ.
:::

### Hàm số {#fs-id1165137932580}

::: {#fs-id1165137932585}
Quan hệ trong đó mỗi giá trị đầu vào tương ứng với đúng một
giá trị đầu ra.
:::

*Làm rõ bổ sung:* Ở đây xét các đầu vào thuộc tập xác định.
“Đúng một” bao gồm cả việc có đầu ra lẫn việc đầu ra ấy là duy nhất.
Hai đầu vào khác nhau vẫn có thể cho cùng một đầu ra.

### Kiểm tra bằng đường thẳng ngang {#fs-id1165137932588}

::: {#fs-id1165134149777}
Phương pháp kiểm tra một hàm số có đơn ánh hay không bằng cách
xác định xem có đường thẳng ngang nào cắt đồ thị tại nhiều hơn
một điểm hay không.
:::

*Làm rõ bổ sung:* Trước hết phải biết đồ thị biểu diễn một hàm số.
Nếu có một đường thẳng ngang cắt đồ thị tại nhiều hơn một điểm,
hàm số không đơn ánh. Hàm số là đơn ánh khi mọi đường thẳng ngang
có nhiều nhất một giao điểm với đồ thị.

### Biến độc lập {#fs-id1165134149782}

::: {#fs-id1165134149787}
Biến đầu vào.
:::

### Đầu vào {#fs-id1165135511353}

::: {#fs-id1165135511359}
Mỗi đối tượng hoặc giá trị trong tập xác định được liên hệ với
một đối tượng hoặc giá trị khác bởi một quan hệ gọi là hàm số.
:::

### Hàm số đơn ánh {#fs-id1165135511364}

::: {#fs-id1165135511369}
Hàm số mà mỗi giá trị đầu ra của nó tương ứng với đúng một
giá trị đầu vào.
:::

*Làm rõ bổ sung:* “Giá trị đầu ra” ở đây là giá trị thực sự đạt được,
tức là phần tử của tập giá trị. Không yêu cầu mọi giá trị trong
một tập đích lớn hơn đều phải được đạt tới. Điều kiện đơn ánh
không phải là điều kiện bắt buộc đối với mọi hàm số.

### Đầu ra {#fs-id1165135508564}

::: {#fs-id1165135508569}
Mỗi đối tượng hoặc giá trị trong tập giá trị được tạo ra khi
một giá trị đầu vào được đưa vào hàm số.
:::

### Tập giá trị {#fs-id1165135508573}

::: {#fs-id1165135315529}
Tập hợp các giá trị đầu ra tương ứng với các giá trị đầu vào
trong một quan hệ.
:::

### Quan hệ {#fs-id1165135315533}

::: {#fs-id1165135315539}
Tập hợp các cặp có thứ tự.
:::

*Làm rõ bổ sung:* Trong một cặp có thứ tự, thành phần thứ nhất là
đầu vào và thành phần thứ hai là đầu ra. Đổi thứ tự có thể tạo
ra một cặp khác. Vì quan hệ là một tập hợp, ghi lặp lại cùng một
cặp không tạo thêm phần tử mới.

### Kiểm tra bằng đường thẳng đứng {#fs-id1165135315542}

::: {#fs-id1165134186374}
Phương pháp kiểm tra một đồ thị có biểu diễn hàm số hay không
bằng cách xác định xem mỗi đường thẳng đứng có cắt đồ thị tại
nhiều nhất một điểm hay không.
:::

*Làm rõ bổ sung:* Dùng quy ước trục ngang biểu diễn đầu vào và
trục đứng biểu diễn đầu ra. Điều kiện “nhiều nhất một” áp dụng
cho mọi đường thẳng đứng, không chỉ một đường được chọn để thử.
Đồ thị khi đó biểu diễn một hàm số trên tập hợp các hoành độ của nó.
Đường thẳng ở ngoài tập xác định có thể không gặp đồ thị.
Nếu tập xác định đã được cho riêng, mỗi đầu vào trong tập đó
phải có đúng một đầu ra; không được bỏ sót đầu vào.

## Đối chiếu các khái niệm {#vi-comparison}

*Hai ví dụ bổ sung — không phải ví dụ nguồn:*

Quan hệ $\{(1,2),(2,2)\}$ là một hàm số: mỗi đầu vào có đúng
một đầu ra. Nhưng hàm số không đơn ánh vì cả hai đầu vào đều
cho đầu ra $2$.

Quan hệ $\{(1,2),(1,3)\}$ không phải là hàm số vì cùng đầu vào
$1$ có hai đầu ra. Việc mỗi đường thẳng ngang cắt đồ thị gồm
hai điểm đã cho tại nhiều nhất một điểm không khắc phục được vi phạm này:
điều kiện hàm số vẫn phải được kiểm tra trước.

*Ghi chú bổ sung về kiểm tra bằng mã:* Chương trình đi kèm
đối chiếu các định nghĩa, mã định danh nguồn và một số quan hệ hữu hạn
minh họa. Việc kiểm tra hữu hạn trường hợp không chứng minh
một mệnh đề cho mọi đồ thị.

## Giới hạn của bài và nguồn {#vi-attribution}

Bài này chỉ hoàn tất bản dịch nháp của bảng thuật ngữ.
Việc đã đến cuối tệp nguồn không tự chứng minh rằng mọi nội dung
trước đó đã được dịch, kiểm tra và tích hợp; không đánh dấu
hoàn thành mô-đun, sách hoặc toàn bộ chương trình dịch.

Bản dịch và phần bổ sung tiếng Việt độc lập, địa phương hóa vi-Latn-VN.
Nguồn: Jay Abramson và các cộng tác viên OpenStax, *Precalculus 2e*,
mô-đun m49301, UUID 11f4eacc-c348-4836-8c5b-747577d249ca;
[nguồn được ghim](https://github.com/openstax/osbooks-college-algebra-bundle/tree/789b54099106b071d1d32bfcee454fed72eb4768).
Đối chiếu với [ấn bản Bahasa Indonesia](https://github.com/KokunoYumeto/openstax-precalculus-2e-id)
0.1.0-alpha.58-reader.1. Giữ quyền ghi công của Jay Abramson,
OpenStax và các tác giả, cộng tác viên được liệt kê trong nguồn.

Văn bản nguồn, bản dịch và phần bổ sung A30 này theo
[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
Các thông báo nguồn được giữ trong thư mục notices/; các sách khác
giữ giấy phép riêng. Bản dịch giữ đủ 11 mục theo thứ tự nguồn,
làm rõ lượng từ trong phép kiểm tra đường thẳng đứng và thêm
những phần có nhãn bổ sung; không sửa bản trích nguồn.
Không phải ấn bản chính thức hoặc được các tác giả hay tổ chức nguồn
bảo trợ. Bản dịch và kiểm tra được thực hiện với sự hỗ trợ của
OpenAI Codex theo yêu cầu người dùng. Chưa có thẩm định độc lập
của người bản ngữ.
