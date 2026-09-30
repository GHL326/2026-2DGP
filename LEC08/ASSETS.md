# 기사 스프라이트 출처

- 작품: **Knight, Princess and Dragon 2**
- 제작자: **akylrum**
- 출처: https://opengameart.org/content/knight-princess-and-dragon-2
- 원본 다운로드: https://opengameart.org/sites/default/files/knightprincessanddragon2.zip
- 라이선스: **CC0 1.0** — 제작자의 위 배포 페이지에 표시됨.
- 라이선스 안내: https://creativecommons.org/publicdomain/zero/1.0/

`knight_source.zip`에는 원본의 `MaximumBounds/Knight/`에서 선택한
대기 40장, 걷기 20장, 달리기 20장, 검 공격 14장, 회전 공격 16장을 담았다.
각 PNG는 **660×545**이며, 원본 PNG 바이트를 변경하지 않고 파일명만 유지해
압축 내부의 하위 디렉터리를 생략했다. 선택한 프레임은 총 110장이다.

`build_atlas.py`는 원본의 투명 여백을 자르고 **4096×3037** 크기의
`knight_atlas.png` 한 장으로 묶는다. 원본 픽셀을 축소하지 않는다.
각 프레임의 크기와 중앙·바닥 기준점은 `animations.json`에 기록한다.

실제 화면에는 같은 배율 1.35를 적용하고 선형 필터링으로 표시한다.
원본 PNG는 그대로 포함되어 있으므로 인터넷 없이 시트를 재생성할 수 있다.
