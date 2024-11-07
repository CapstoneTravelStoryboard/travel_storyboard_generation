import os

# OpenAI API 키
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-A29dTH7iwp6yl4LXN_k0fTCrz1hxUBiQVGHMSbcinxT3BlbkFJ9ME5ZVAhANL1zSJXIhzzG9u7FK0WcASnlebCLuhYoA")  # 환경 변수 또는 기본 키 설정

# AWS S3 설정
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY", "...")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "...")
AWS_BUCKET_NAME = "capstonestoryboard"
