# RAG sources

`manifest.example.yaml`을 복사해 실제 카드/통신사 공식 문서 URL, 유효기간, checksum을 기록합니다. 원문 파일은 `documents/`에 두되 저작권과 이용조건을 확인하고 Git에 커밋하지 않습니다.

혜택 청크에는 최소한 `source_id`, `provider`, `product_name`, `merchant_keywords`, `valid_from`, `valid_to`, `source_url`을 포함해야 합니다. 필수 규칙이나 공식 출처가 없으면 calculator 입력에서 제외합니다.

