# PS5 DualSense 컨트롤러 SVG

소니 PlayStation 5 DualSense 무선 컨트롤러(흰색 표준 모델, CFI-ZCT1W)를 정면에서 본 모습을 그린 SVG 일러스트입니다.
실물 치수(160 × 106 mm)에 맞춘 좌표계 위에 손으로 베지어 곡선을 그렸고, 배경은 투명합니다.

![DualSense front view](preview/dualsense-on-grey.png)

## 파일

| 경로 | 설명 |
|---|---|
| `dualsense.svg` | 완성본. `viewBox="-8 -8 1616 1076"`, 10단위 = 1 mm. 컨트롤러 자체는 x 0–1600, y 0–1060(트리거 끝부터 그립 끝까지)을 차지합니다. 외부 참조와 CSS가 없어 어디에나 그대로 넣을 수 있습니다. |
| `preview/dualsense.png` | 투명 배경 렌더 (1616 × 1076) |
| `preview/dualsense-on-grey.png` | 밝은 회색 배경 렌더 |
| `tools/build_dualsense.py` | SVG를 생성하는 스크립트. 색상표와 모든 좌표가 여기 있습니다. |
| `tools/svgkit.py` | 경로 작성, 좌우 대칭 복제, 그라디언트 도우미 |
| `tools/render.js` | Playwright + Chromium으로 SVG를 PNG로 렌더 |

## 구조

부품마다 `id`가 붙은 `<g>`로 묶여 있어 CSS나 스크립트로 개별 부품을 강조하거나 숨길 수 있습니다.

```
triggers        trigger-l2, trigger-r2
bumpers         bumper-l1, bumper-r1
shell           shell-body, usb-c
inner-section   inner-section-body (스틱 주변의 검은 부분과 그립 안쪽 띠)
touchpad        touchpad-surface, lightbar-l, lightbar-r
player-indicator, speaker
ps-button, mute-button (mute-icon), headset-jack
stick-l, stick-r
dpad            dpad-up, dpad-right, dpad-down, dpad-left
face-buttons    btn-triangle, btn-circle, btn-cross, btn-square
create-button, options-button, create-icon, options-icon
```

예를 들어 `#btn-cross` 그룹의 `fill`을 바꾸거나 `#lightbar-l, #lightbar-r`의 색을 바꾸면 플레이어 색상을 흉내 낼 수 있습니다.
라이트바는 플레이어 1의 파란색, 플레이어 표시등은 가운데 하나가 켜진 상태로 그렸습니다.

## 다시 만들기

```sh
python3 tools/build_dualsense.py -o dualsense.svg
node tools/render.js dualsense.svg preview/dualsense.png 1616 transparent
node tools/render.js dualsense.svg preview/dualsense-on-grey.png 1616 "#e9ebef"
```

생성 스크립트는 표준 라이브러리만 씁니다. 렌더 스크립트는 `playwright` 패키지와 Chromium이 필요합니다.

## 고증 메모

- 흰색 모델에서는 터치패드, 십자키, △○✕□ 버튼, 크리에이트/옵션 버튼이 모두 흰색 계열입니다. 검은 부분은 터치패드 아래쪽 가장자리에서 시작해 스틱, PS 버튼, 음소거 버튼을 감싸고 양쪽 그립 안쪽을 따라 가늘어지며 내려갑니다.
- L1/R1 범퍼와 L2/R2 트리거는 검은색입니다.
- 페이스 버튼의 기호는 색이 없는 회색이고, 투명한 캡 가장자리가 어두운 테두리로 보입니다.
- 터치패드 양옆에 라이트바가 가늘게 지나가고, 패드 아래에 플레이어 표시 LED 5개와 스피커 구멍 4개가 있습니다.
- PS 버튼은 로고 모양 그대로 돌출된 버튼이고, 그 아래에 음소거 버튼과 마이크 음소거 기호가 있습니다.
- 크리에이트 버튼 위에는 세 갈래 선, 옵션 버튼 위에는 가로줄 세 개가 인쇄되어 있습니다.
- 실루엣과 부품 위치는 공개 치수(160 × 66 × 106 mm, 스틱 간격 약 51 mm, 터치패드 약 63 × 34 mm 등)와 3D 모델의 정사영을 대조해 맞췄습니다. 정사영에서는 트리거가 거의 가려지지만, 제품 사진처럼 읽히도록 범퍼 위로 5 mm 정도 보이게 그렸습니다.

## 출처와 권리

- PlayStation 로고 경로는 [Simple Icons](https://github.com/simple-icons/simple-icons)의 `playstation.svg`(CC0 1.0)를 가져와 크기만 맞췄습니다. PlayStation 로고와 DualSense의 형태는 Sony Interactive Entertainment의 상표와 디자인이며, 이 그림은 제품을 묘사한 일러스트입니다.
- 비율을 맞추는 참고 자료로 Taohid Animation의 Sketchfab 모델 "PS5 Controller"(CC BY 4.0, [SafaElmali/dualsense-studio](https://github.com/SafaElmali/dualsense-studio)에 수록된 glTF)를 정사영해 사용했습니다. 모델의 지오메트리를 복사하지는 않았습니다.
- 렌더 확인: Chromium(Playwright), resvg, CairoSVG 세 렌더러에서 같은 결과가 나오는 것을 확인했습니다. 필터는 `feGaussianBlur`만, 그라디언트는 선형/방사형만 사용합니다.
