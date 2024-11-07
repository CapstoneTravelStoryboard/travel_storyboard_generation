# 로그를 파일에 저장하는 함수
def log_to_file(log_content, log_file):
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_content + "\n")