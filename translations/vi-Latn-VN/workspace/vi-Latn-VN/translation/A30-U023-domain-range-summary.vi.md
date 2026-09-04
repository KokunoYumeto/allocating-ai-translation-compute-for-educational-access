---
title: "Các ý chính về tập xác định và tập giá trị"
lang: vi-Latn-VN
subtitle: "A30 · Bài tự học 023 · Bản dịch thử nghiệm 0.1"
---

## Cách dùng phần ôn tập {#vi-prerequisites}

*Hướng dẫn bổ sung:* Bài này dịch trọn tám ý trong phần tổng kết
khái niệm của mô-đun m49304. Mười ba liên kết “Ví dụ” dẫn đến
các ví dụ đã dịch trong Bài 018–022, không phải ví dụ hay bài tập
mới. Phần tổng kết không có công thức MathML, hình hay đáp án
nguồn. Các lưu ý hỗ trợ tự học dưới đây được ghi rõ là bổ sung.

## Các ý chính cần nhớ {#fs-id1165134077347}

*Làm rõ bổ sung về phạm vi của ý thứ nhất:* Khi chỉ cho một
công thức và không quy định tập xác định khác, ta tìm **tập
xác định thực lớn nhất của công thức**: tất cả đầu vào thực
làm cho công thức có nghĩa. Nếu đề bài đã chỉ định tập xác
định, hoặc bối cảnh đặt ra giới hạn, phải giữ những điều kiện
đó; không tự mở rộng tập xác định chỉ vì biểu thức vẫn tính
được. Toàn bộ phần ôn tập này xét đầu vào và đầu ra là số thực.

::: {#fs-id1165137591772}

1. Tập xác định của một hàm số bao gồm tất cả các giá trị đầu
   vào thực không dẫn đến phép toán không xác định, chẳng hạn
   chia cho 0 hoặc lấy căn bậc hai của một số âm.

2. Có thể xác định tập xác định của một hàm số bằng cách liệt
   kê các giá trị đầu vào trong một tập hợp các cặp có thứ tự.
   Xem [Ví dụ 1](A30-U018-domain-equations.vi.html#Example_01_02_01).

3. Cũng có thể xác định tập xác định của một hàm số bằng cách
   tìm các giá trị đầu vào của hàm số được viết dưới dạng
   phương trình. Xem [Ví dụ 2](A30-U018-domain-equations.vi.html#Example_01_02_02),
   [Ví dụ 3](A30-U018-domain-equations.vi.html#Example_01_02_03)
   và [Ví dụ 4](A30-U018-domain-equations.vi.html#Example_01_02_04).

4. Các giá trị thuộc khoảng được biểu diễn trên trục số có
   thể được mô tả bằng bất đẳng thức, ký hiệu tập hợp theo
   điều kiện và ký hiệu khoảng.
   Xem [Ví dụ 5](A30-U019-set-notation.vi.html#Example_01_02_05).

5. Với nhiều hàm số, có thể xác định tập xác định và tập giá
   trị từ đồ thị. Xem [Ví dụ 6](A30-U020-domain-range-graphs.vi.html#Example_01_02_06)
   và [Ví dụ 7](A30-U020-domain-range-graphs.vi.html#Example_01_02_07).

6. Hiểu các hàm số cơ bản giúp ta tìm tập xác định và tập giá
   trị của những hàm số có liên quan.
   Xem [Ví dụ 8](A30-U021-toolkit-domains-ranges.vi.html#Example_01_02_08),
   [Ví dụ 9](A30-U021-toolkit-domains-ranges.vi.html#Example_01_02_09)
   và [Ví dụ 10](A30-U021-toolkit-domains-ranges.vi.html#Example_01_02_10).

7. Hàm số cho bởi nhiều công thức được mô tả bằng nhiều hơn
   một công thức. Xem [Ví dụ 11](A30-U022-piecewise-functions.vi.html#Example_01_02_11)
   và [Ví dụ 12](A30-U022-piecewise-functions.vi.html#Example_01_02_12).

8. Có thể vẽ đồ thị hàm số cho bởi nhiều công thức bằng cách
   áp dụng mỗi công thức đại số trên phần tập xác định được
   chỉ định cho công thức ấy.
   Xem [Ví dụ 13](A30-U022-piecewise-functions.vi.html#Example_01_02_13).
:::

## Lưu ý khi ôn tập {#vi-review-notes}

*Làm rõ bổ sung:* Tập giá trị gồm những đầu ra **thực sự nhận
được** từ các đầu vào trong tập xác định. Khi đọc đồ thị,
phải phân biệt điểm thuộc đồ thị với điểm bị loại, và không
tự suy ra phần đồ thị ngoài cửa sổ đã cho nếu thiếu thông tin.

*Làm rõ bổ sung:* “Nhiều công thức” không có nghĩa là một đầu
vào được nhận nhiều đầu ra khác nhau. Mỗi đầu vào thuộc tập
xác định vẫn phải tương ứng với đúng một giá trị đầu ra.
Điều kiện của từng nhánh quyết định lúc nào áp dụng công thức;
các nhánh chồng lấn chỉ hợp lệ khi cùng cho một đầu ra tại
mọi đầu vào thuộc phần giao.

## Nguồn và phạm vi {#vi-attribution}

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

Bài này chỉ dịch mục tổng kết fs-id1165134077347 và dừng trước
tiêu đề phần bài tập fs-id1165135176628. Các bài tập của mô-đun
không nằm trong bài đọc này. Mô-đun m49304, sách A30 và toàn bộ
lộ trình năm sách vẫn còn các phần cần tiếp tục.
