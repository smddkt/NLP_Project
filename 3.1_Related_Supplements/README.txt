other_supplements.py => 보조제별 연관 높은 다른 보조제들 목록 도출하는 스크립트 (보조제 종류당 1행)
other_supplements.py => 두가지 이상의 보조제가 언급된 텍스트 데이터의 목록 (텍스트당 1행)



<other_supplements 관련 메모>

1. 파일 경로 정의

categorized_corpus_file_path: 전처리되고, 이후 보조제별로 분류된 텍스트 데이터 파일 경로
supplement_list_file_path: 보충제 리스트 파일 경로
output_file_path: 결과를 저장할 출력 파일 경로

2. 함께 언급된 보조제 리스트 작성 및 순서 조정

단순히 보조제별로 함께 언급된 횟수를 기준으로 나열하면, 압도적인 게시글 양을 보유한 melatonin등이 모든 보조제들에서 가장 많이 언급된 보조제로 나오게 됨.
이는 기존의 목적과 어긋나기 때문에 각 보조제별 총 언급량으로 이 수치를 나누게 하였음.
예를 들어, A라는 보조제와 함께 B보조제는 200번 언급되었지만, B보조제는 애초에 언급이 2000으로 많고(10%), 
C보조제는 10번만 함께 언급되었지만, 애초에 C보조제는 50개의 텍스트에서만 등장했다면(20%)
대중은 A보조제와 더 연관성이 깊다고 생각하는 보조제는 C라고 보는 것이 타당하다고 판단하였음.
