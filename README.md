# fictional-engine

![Pelican riding a bicycle](pelican-bicycle.svg)

자전거를 탄 펠리칸. 손으로 좌표를 잡아 그린 단일 SVG 파일(`pelican-bicycle.svg`)이에요.

A great white pelican riding a teal city bicycle along a seaside road, hand-authored as a single SVG.

- 뷰박스 1200 × 800, 외부 참조·스크립트·글꼴 없이 파일 하나로 끝나요. 어디서 열어도 같은 그림이 나와요.
- 펠리칸: 갈고리처럼 굽은 부리 끝(nail), 아래턱에 매달린 주머니, S자 목, 검은 날개깃, 물갈퀴 발. 부리 끝에는 물고기 꼬리가 살짝 나와 있어요.
- 자전거: 다이아몬드 프레임, 포크, 스템과 뒤로 굽은 손잡이, 안장, 서로 반대 방향의 크랭크, 체인링에서 뒤 스프라켓으로 이어지는 체인, 바퀴살 열여덟 개씩.
- 구조: `<g id="background">`, `<g id="bicycle">`, `<g id="pelican">` 세 묶음으로 나뉘고, 바퀴는 `<defs>`에 한 번 정의해 두 번 `<use>`해요.
