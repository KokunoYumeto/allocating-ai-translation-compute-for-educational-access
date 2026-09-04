---
title: "Đọc tập xác định và tập giá trị từ đồ thị"
lang: vi-Latn-VN
subtitle: "A30 · Bài tự học 026 · Bản dịch thử nghiệm 0.1"
---

## Chuẩn bị làm bài {#vi-prerequisites}

*Hướng dẫn bổ sung:* Tập xác định gồm các hoành độ của những
điểm trên đồ thị; tập giá trị gồm các tung độ thực sự được
nhận. Khi đọc đầu mút, phân biệt điểm tô kín với vòng tròn
rỗng. Một điểm bị loại không nhất thiết làm tung độ của nó
bị loại khỏi tập giá trị: tung độ ấy có thể xuất hiện ở một
điểm khác.

Bài này giữ mười một hình nguồn nguyên trạng, dùng số Bài
27–37 theo thứ tự bài tập của mô-đun. Hãy làm trước rồi theo
liên kết đến lời giải. Sáu đáp án có sẵn trong nguồn được
ghi rõ; năm bài còn lại có lời giải bổ sung. Riêng giới hạn
trên của tập giá trị ở Bài 34 chưa được nguồn xác định rõ:
lời giải phân biệt điều đọc được với một cách hiểu có thêm
giả thiết.

Đọc các số và chiều dương ghi trên trục, không chỉ nhìn
hướng lên hay xuống trên trang. Những đường nét đứt và mũi
tên chú thích không tự trở thành các nhánh của hàm số.
Không suy ra một công thức, một tiệm cận hay tính không bị
chặn chỉ từ hình dáng trong một khung vẽ hữu hạn.

## Bài tập đồ thị {#fs-id1165137580833}

::: {#fs-id1165135186809}
Với các bài tập sau, hãy viết tập xác định và tập giá trị
của mỗi hàm số bằng ký hiệu khoảng.
:::

### Bài 27 {#fs-id1165135168172}

::: {#fs-id1165137647479}
::: {#fs-id1165137891294}
![Đoạn thẳng đi xuống từ vòng tròn rỗng tại (2,8) đến điểm tô kín tại (8,6). Trên hai trục, các vạch số được ghi cách nhau 2 đơn vị.](../assets/CNX_Precalc_Figure_01_02_202-95dc.jpg)
:::
:::

[Xem đáp án Bài 27](#fs-id1165137820038).

### Bài 28 {#fs-id1165135160181}

::: {#fs-id1165135160183}
::: {#fs-id1165137837830}
![Đoạn thẳng đi xuống từ điểm tô kín tại (4,8) đến vòng tròn rỗng tại (8,2). Các tọa độ được đọc theo vạch số trên hai trục.](../assets/CNX_Precalc_Figure_01_02_203-38f5.jpg)
:::
:::

[Xem lời giải Bài 28](#vi-answer-28).

### Bài 29 {#fs-id1165137723404}

::: {#fs-id1165137809982}
::: {#fs-id1165137733767}
![Đường cong từ điểm tô kín (−4,0), đi qua điểm cao nhất (0,2), đến điểm tô kín (4,0). Toàn bộ đường cong nằm phía trên hoặc trên trục ngang.](../assets/CNX_Precalc_Figure_01_02_204-d2ad.jpg)
:::
:::

[Xem đáp án Bài 29](#fs-id1165137847285).

### Bài 30 {#fs-id1165137590678}

::: {#fs-id1165134168421}
::: {#fs-id1165137837060}
![Đường cong dạng chữ U trên trang, có hai đầu mút tô kín (2,2) và (6,2), đi qua (4,6). Trục y của hình có chiều dương hướng xuống; các số 1 đến 7 đều dương.](../assets/CNX_Precalc_Figure_01_02_205-5a91.jpg)
:::
:::

*Lưu ý về hình nguồn:* Ở hình này, các giá trị trên trục
$y$ **tăng theo hướng xuống dưới**. Bản mô tả Indonesia
cũng nêu rõ quy ước ấy. Không đổi dấu các số hoặc lật lại
ảnh theo thói quen vẽ trục đứng hướng lên.

[Xem lời giải Bài 30](#vi-answer-30).

### Bài 31 {#fs-id1165137737326}

::: {#fs-id1165137737328}
::: {#fs-id1165134129572}
![Đường cong từ điểm tô kín (−5,2), hạ xuống chạm mức y=0 gần x=−1, rồi đi lên đến vòng tròn rỗng (3,2). Đầu mút trái được lấy, đầu mút phải bị loại.](../assets/CNX_Precalc_Figure_01_02_206-059d.jpg)
:::
:::

[Xem đáp án Bài 31](#fs-id1165137657479).

### Bài 32 {#fs-id1165137404973}

::: {#fs-id1165137404975}
::: {#fs-id1165134305418}
![Đường cong từ điểm tô kín (−3,−5), đi lên qua trục ngang đến điểm cao nhất (0,4), rồi đi xuống và kết thúc ở vòng tròn rỗng (2,0).](../assets/CNX_Precalc_Figure_01_02_207-ec92.jpg)
:::
:::

[Xem lời giải Bài 32](#vi-answer-32).

### Bài 33 {#fs-id1165137544188}

::: {#fs-id1165137437269}
::: {#fs-id1165137447903}
![Đường cong có điểm cuối tô kín tại (1,0). Từ điểm đó, đường cong đi về phía trên bên trái và có mũi tên chỉ sự tiếp tục; không có điểm ở bên phải x=1.](../assets/CNX_Precalc_Figure_01_02_208-7f09.jpg)
:::
:::

*Ghi chú đối chiếu:* Mô tả thay thế tiếng Anh ghi cận phải
của tập xác định là 2. Điểm trong ảnh là $(1,0)$; đáp án
nguồn và mô tả Indonesia đều xác nhận cận phải là 1.
Bản mô tả tiếng Việt dùng 1, không sửa ảnh nguồn.

[Xem đáp án Bài 33](#fs-id1165137445711).

### Bài 34 {#fs-id1165135176309}

::: {#fs-id1165134323791}
::: {#fs-id1165135192955}
![Đường cong đi lên từ điểm tô kín (−4,−2), qua gần (−2,0) và (0,2), rồi thoải dần với mũi tên hướng sang phải và lên trên. Hình không cho công thức hoặc đường tiệm cận ngang.](../assets/CNX_Precalc_Figure_01_02_209-37f5.jpg)
:::
:::

[Xem lời giải và giới hạn thông tin ở Bài 34](#vi-answer-34).

### Bài 35 {#fs-id1165137642580}

::: {#fs-id1165137642582}
::: {#fs-id1165134482733}
![Hai nhánh cong có bốn đầu mút tô kín, được ghi (−6,−1/6), (−1/6,−6), (1/6,6), (6,1/6). Đường nét đứt đứng tại x=0 và các mũi tên đen chỉ đến nhãn tọa độ là phần chú thích.](../assets/CNX_Precalc_Figure_01_02_210-a5dd.jpg)
:::
:::

[Xem đáp án Bài 35](#fs-id1165134043582).

### Bài 36 {#fs-id1165137442385}

::: {#fs-id1165137812572}
::: {#fs-id1165137645308}
![Đường cong dạng chữ W bắt đầu ở vòng tròn rỗng (−2.5,10), có hai điểm thấp nhất ở mức y=−4 và điểm nhô lên giữa tại (0,0). Nhánh phải đi lên với mũi tên.](../assets/CNX_Precalc_Figure_01_02_211-3cb1.jpg)
:::
:::

[Xem lời giải Bài 36](#vi-answer-36).

### Bài 37 {#fs-id1165137851981}

::: {#fs-id1165137851983}
::: {#fs-id1165137602824}
![Đường gấp khúc bắt đầu ở điểm tô kín (−3,0), đi lên đến (0,5), nằm ngang đến (3,5), rồi đi lên về phía phải với mũi tên. Hai điểm nối cũng được tô kín.](../assets/CNX_Precalc_Figure_01_02_212-f3f3.jpg)
:::
:::

*Ghi chú đối chiếu:* Mô tả Indonesia ghi điểm nối đầu tiên
là $(-1,5)$. Trong ảnh, điểm đó nằm trên trục đứng, tức là
$(0,5)$. Bản mô tả tiếng Việt đọc theo ảnh; các đáp án về tập
xác định và tập giá trị của nguồn vẫn được giữ nguyên.

[Xem đáp án Bài 37](#fs-id1165137575572).

## Đáp án và lời giải {#vi-answers}

Phần ghi **Đáp án nguồn** giữ kết quả đã có trong nguồn.
Phần ghi **Giải thích bổ sung** hoặc **Lời giải bổ sung** do
bản dịch thêm để nêu cách đọc hình và những điều kiện cần
chú ý. Bài 34 có một kết luận về tập giá trị chỉ đúng dưới
giả thiết được nêu rõ.

### Bài 27 {#fs-id1165137820038}

::: {#fs-id1165137424631}
**Đáp án nguồn:** tập xác định {{math:fs-id1165137424631:0}}
tập giá trị {{math:fs-id1165137424631:1}}.
:::

*Giải thích bổ sung:* $x=2$ bị loại, $x=8$ được lấy.
Đầu ra 6 được nhận ở đầu mút tô kín, còn 8 bị loại ở đầu
mút rỗng. Vì vậy 8 thuộc tập xác định nhưng không thuộc tập
giá trị của hàm số này.

### Bài 28 {#vi-answer-28}

**Lời giải bổ sung — nguồn không kèm đáp án.**

Tập xác định là $[4,8)$; tập giá trị là $(2,8]$.
Điểm $(4,8)$ được lấy nên cả đầu vào 4 lẫn đầu ra 8 được
nhận. Điểm $(8,2)$ bị loại; trên đoạn còn lại không có đầu
vào 8 hoặc đầu ra 2.

### Bài 29 {#fs-id1165137847285}

::: {#fs-id1165137541038}
**Đáp án nguồn:** tập xác định {{math:fs-id1165137541038:0}}
tập giá trị {{math:fs-id1165137541038:1}}.
:::

*Giải thích bổ sung:* Cả hai đầu mút $x=-4$ và $x=4$ đều
được lấy. Đầu ra nhỏ nhất là 0, nhận ở hai đầu mút; đầu ra
lớn nhất là 2, nhận tại điểm cao nhất của đường cong.

### Bài 30 {#vi-answer-30}

**Lời giải bổ sung — nguồn không kèm đáp án.**

Tập xác định là $[2,6]$; tập giá trị cũng là $[2,6]$.
Hai đầu mút cho đầu ra 2; điểm $(4,6)$ cho đầu ra 6.
Đường cong nhận mọi giá trị nằm giữa chúng.

Do chiều dương của trục $y$ hướng xuống, điểm nằm thấp
nhất trên trang lại có tung độ **lớn nhất**, bằng 6.
Tập giá trị không phải $[-6,-2]$. Phải sắp các cận theo
giá trị số, không theo vị trí cao hay thấp trên trang.

### Bài 31 {#fs-id1165137657479}

::: {#fs-id1165137657482}
**Đáp án nguồn:** tập xác định {{math:fs-id1165137657482:0}}
tập giá trị {{math:fs-id1165137657482:1}}.
:::

*Giải thích bổ sung:* Đầu vào $-5$ được lấy, còn 3 bị loại.
Đường cong chạm mức 0, nên 0 thuộc tập giá trị. Vòng tròn
rỗng $(3,2)$ không loại đầu ra 2: điểm tô kín $(-5,2)$ vẫn
cho đầu ra ấy.

### Bài 32 {#vi-answer-32}

**Lời giải bổ sung — nguồn không kèm đáp án.**

Tập xác định là $[-3,2)$; tập giá trị là $[-5,4]$.
Đầu mút tô kín cho đầu vào $-3$ và đầu ra $-5$; điểm cao
nhất của đường cong cho đầu ra 4. Đầu vào 2 bị loại.

Đầu ra 0 vẫn được nhận tại giao điểm khác của đường cong
với trục ngang, ở bên trái trục đứng. Không được loại 0
khỏi tập giá trị chỉ vì điểm $(2,0)$ là một vòng tròn rỗng.

### Bài 33 {#fs-id1165137445711}

::: {#fs-id1165137445713}
**Đáp án nguồn:** tập xác định {{math:fs-id1165137445713:0}}
tập giá trị {{math:fs-id1165137445713:1}}.
:::

*Giải thích bổ sung:* Điểm cuối $(1,0)$ được lấy. Đáp án
nguồn xác định rằng nhánh kéo dài không bị chặn về phía
trái và không bị chặn phía trên. Giữ 1 trong tập xác định
và 0 trong tập giá trị; không dùng cận phải 2 từ mô tả
tiếng Anh bị sai.

### Bài 34 {#vi-answer-34}

**Lời giải bổ sung — nguồn không kèm đáp án.**

Tập xác định là $[-4,\infty)$, phù hợp với đầu mút tô kín
và phần kéo dài sang phải được mô tả trong nguồn. Đầu ra
$-2$ được nhận tại $(-4,-2)$ và là giá trị nhỏ nhất của
đường cong đi lên mà hình mô tả.

**Giới hạn thông tin nguồn:** Không có công thức hoặc đáp
án về tập giá trị, cũng không có thông tin tường minh về
cận trên hay tiệm cận ngang. Mũi tên vừa hướng phải vừa
hướng lên không tự chứng minh rằng đầu ra tăng không bị
chặn. Do đó, chưa thể khẳng định chính xác cận trên của
tập giá trị chỉ từ những dữ kiện này.

Nếu đọc mũi tên theo **giả thiết bổ sung rằng nhánh tiếp
tục tăng không bị chặn trên**, ta được tập giá trị
$[-2,\infty)$. Đây là kết luận có điều kiện, không phải
đáp án nguồn và không phải một kết luận chắc chắn từ khung
hình hữu hạn. Bản dịch không gán thêm công thức hoặc một
tiệm cận cụ thể cho đường cong.

### Bài 35 {#fs-id1165134043582}

::: {#fs-id1165135335983}
**Đáp án nguồn:**

Tập xác định: {{math:fs-id1165135335983:0}}

Tập giá trị: {{math:fs-id1165135335983:1}}.
:::

*Giải thích bổ sung:* Đọc bốn tọa độ ghi ngay trên hình;
các đầu mút đều được lấy. Khoảng giữa $-1/6$ và $1/6$ bị
loại khỏi cả hai tập. Các giá trị nằm ngoài đoạn $[-6,6]$
cũng bị loại: hình chỉ lấy những phần cong có các đầu mút
tô kín này.

Đường nét đứt tại $x=0$ không phải một nhánh của hàm số.
Mũi tên đen của các nhãn tọa độ chỉ vị trí điểm, không kéo
dài đường cong qua các đầu mút. Không thay tập đã cho bằng
toàn bộ tập số thực khác 0.

### Bài 36 {#vi-answer-36}

**Lời giải bổ sung — nguồn không kèm đáp án.**

Tập xác định là $(-2.5,\infty)$; tập giá trị là
$[-4,\infty)$. Mô tả tiếng Anh xác nhận cận trái $-2.5$;
vòng tròn rỗng loại đầu vào đó. Hai điểm thấp nhất có
tung độ $-4$ và được lấy. Mô tả Indonesia nêu rõ nhánh
bên phải đi lên không bị chặn, phù hợp với mũi tên trong
hình.

Tung độ 10 của vòng tròn rỗng bên trái vẫn được nhận ở
nhánh bên phải. Một lần nữa, loại một điểm không nhất
thiết loại tung độ của điểm ấy khỏi tập giá trị.

### Bài 37 {#fs-id1165137575572}

::: {#fs-id1165137601170}
**Đáp án nguồn:** tập xác định {{math:fs-id1165137601170:0}}
tập giá trị {{math:fs-id1165137601170:1}}.
:::

*Giải thích bổ sung:* Đồ thị bắt đầu tại $(-3,0)$, lấy
điểm này và tiếp tục về phía phải. Đầu ra nhỏ nhất là 0;
nhánh cuối đi lên không bị chặn như đáp án nguồn xác định.
Đoạn nằm ngang tại mức 5 không tạo khoảng trống trong tập
giá trị: các đoạn nối tiếp đã đi qua mọi mức từ 0 đến 5,
rồi nhánh cuối nhận các mức cao hơn.

## Nguồn và bước tiếp theo {#vi-attribution}

Nguồn: Jay Abramson và các cộng tác viên OpenStax, *Precalculus 2e*,
mô-đun m49304, UUID 1ca91f2c-f989-40da-b8cc-b930d5c0ad36;
[phiên bản được ghim](https://github.com/openstax/osbooks-college-algebra-bundle/tree/789b54099106b071d1d32bfcee454fed72eb4768).
Đối chiếu với [ấn bản Bahasa Indonesia](https://github.com/KokunoYumeto/openstax-precalculus-2e-id)
0.1.0-alpha.58-reader.1. Giữ nguyên mười một ảnh nguồn;
các mô tả tiếng Việt và phần giải thích bổ sung ở ngoài
ảnh không làm thay đổi ảnh hoặc đáp án nguồn.

Văn bản, bản dịch, phần bổ sung A30 và mười một hình nguồn
theo [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
Hình nguồn: Copyright Rice University, OpenStax. Giữ ghi
công, thông báo thay đổi, chia sẻ tương tự và các thông báo
riêng trong notices/; các sách khác giữ giấy phép riêng.
Đây là bản dịch độc lập, không được tác giả nguồn bảo trợ;
thực hiện với sự hỗ trợ của OpenAI Codex theo yêu cầu
người dùng, chưa có thẩm định của người bản ngữ.

Mã đi kèm kiểm tra việc giữ nguồn, các điều kiện đầu mút
và một số giá trị hữu hạn. Nó không xác định một công thức
ẩn sau các ảnh, không giải quyết sự thiếu thông tin ở
Bài 34 và không thay thế lập luận cho một tập vô hạn.

Bài này giữ tiêu đề nhóm đồ thị fs-id1165137580833 và dịch
trọn khối đầu gồm Bài 27–37, từ hướng dẫn fs-id1165135186809
đến bài fs-id1165137851981. Bài dừng trước hướng dẫn tiếp
theo fs-id1165137785119, nơi bắt đầu các bài phác đồ thị
hàm số cho bởi nhiều công thức. Phần còn lại của mô-đun,
sách A30 và toàn bộ nhiệm vụ năm sách vẫn cần tiếp tục.
