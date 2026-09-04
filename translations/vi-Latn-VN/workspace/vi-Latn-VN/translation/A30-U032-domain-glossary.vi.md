---
title: "Bảng thuật ngữ: ký hiệu tập hợp và hàm số cho bởi nhiều công thức"
lang: vi-Latn-VN
subtitle: "A30 · Bài tự học 032 · Bản dịch thử nghiệm 0.1"
---

## Phạm vi và cách đọc {#vi-prerequisites}

Bài này dịch đủ ba mục của bảng thuật ngữ cuối mô-đun
m49304, theo đúng thứ tự nguồn. Các định nghĩa là bản
dịch nguồn; những đoạn làm rõ được ghi riêng là **bổ sung**.
Giữ nguyên công thức ký hiệu tập hợp, chỉ dịch phần chữ
bên trong công thức. Nguồn không có bài tập, lời giải
hay hình trong bảng thuật ngữ này.

## Các thuật ngữ {#vi-glossary}

### Ký hiệu khoảng {#fs-id1165135445751}

::: {#fs-id1165135190252}

Một cách mô tả tập hợp gồm tất cả các số nằm giữa một
cận dưới và một cận trên. Hai giá trị cận được viết giữa
các dấu ngoặc vuông hoặc ngoặc tròn. Dấu ngoặc vuông
cho biết cận tương ứng thuộc tập hợp; dấu ngoặc tròn
cho biết cận tương ứng không thuộc tập hợp.
:::

*Làm rõ bổ sung:* “Ký hiệu khoảng” ở đây là tên gọi chung
cho cách viết, bao gồm cả dạng lấy hai đầu mút, bỏ hai
đầu mút hoặc chỉ lấy một đầu mút. Với hai số thực $a<b$,
$[a,b]$ lấy cả hai cận, $(a,b)$ bỏ cả hai cận;
$[a,b)$ chỉ lấy $a$, còn $(a,b]$ chỉ lấy $b$.

Có thể dùng ký hiệu này cho tập không bị chặn. Các ký
hiệu $-\infty$ và $\infty$ không phải số thực, nên phía
có một trong hai ký hiệu ấy luôn dùng ngoặc tròn, không
dùng ngoặc vuông.

### Hàm số cho bởi nhiều công thức {#fs-id1165135487256}

::: {#fs-id1165137452169}

Hàm số dùng nhiều hơn một công thức để xác định đầu ra.
:::

*Làm rõ bổ sung:* Mỗi công thức đi kèm điều kiện cho
các đầu vào mà nó áp dụng. Xét các điều kiện trước khi
chọn công thức; công thức cũng phải có nghĩa tại đầu
vào được chọn. Nếu các điều kiện của hai nhánh cùng
nhận một đầu vào, hai công thức phải cho cùng một đầu
ra tại đó để vẫn xác định một hàm số. Mỗi đầu vào thuộc
tập xác định phải có đúng một đầu ra; đầu vào không
được nhánh nào nhận không thuộc tập xác định của quy
tắc đã cho.

### Ký hiệu tập hợp theo điều kiện {#fs-id1165137863188}

::: {#fs-id1165137863193}

Một cách mô tả tập hợp bằng một quy tắc mà mọi phần tử
của tập hợp đều thỏa mãn; ký hiệu có dạng
{{math:fs-id1165137863193:0}}
:::

*Làm rõ bổ sung:* Dấu $|$ trong ký hiệu này được đọc là
“sao cho”; nó ngăn cách biến với điều kiện, không phải
dấu giá trị tuyệt đối. Cần nói rõ $x$ chạy trong tập
nào, rồi lấy đúng các phần tử của tập đang xét thỏa mãn
điều kiện. Không chỉ lấy một vài phần tử thỏa điều kiện
và bỏ qua những phần tử khác cũng thỏa điều kiện ấy.

## Giới hạn của bài và nguồn {#vi-attribution}

*Ghi chú bổ sung về kiểm tra:* Chương trình đi kèm kiểm
tra việc giữ ba định nghĩa, các mã định danh, công thức
và một số trường hợp hữu hạn về dấu ngoặc, điều kiện
nhánh và cách chọn phần tử. Những phép thử ấy không
thay thế lập luận cho mọi tập hợp hoặc mọi hàm số.

Bài này chỉ dịch bảng thuật ngữ cuối mô-đun. Việc đã
đến cuối tệp nguồn không tự chứng minh rằng mọi phần
trước đó đã được dịch, kiểm tra và tích hợp. Không vì
thế mà đánh dấu hoàn thành mô-đun m49304, sách A30 hay
toàn bộ nhiệm vụ năm sách.

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
