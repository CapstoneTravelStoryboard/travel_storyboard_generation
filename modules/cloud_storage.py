import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from config.settings import AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, AWS_BUCKET_NAME

def upload_image_to_cloud(image_path, s3_file_name):
    # AWS S3 클라이언트 생성
    s3 = boto3.client('s3', 
                      aws_access_key_id=AWS_ACCESS_KEY, 
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    
    try:
        # S3에서 해당 파일이 이미 존재하는지 확인
        try:
            s3.head_object(Bucket=AWS_BUCKET_NAME, Key=s3_file_name)
            print(f"{s3_file_name} 파일이 이미 존재합니다. 업로드를 건너뜁니다.")
            return f"https://{AWS_BUCKET_NAME}.s3.amazonaws.com/{s3_file_name}"
        except ClientError as e:
            # 파일이 존재하지 않으면 업로드 진행
            if e.response['Error']['Code'] == '404':
                print(f"{s3_file_name} 파일이 존재하지 않음, 업로드를 진행합니다.")
                s3.upload_file(image_path, AWS_BUCKET_NAME, s3_file_name)
                return f"https://{AWS_BUCKET_NAME}.s3.amazonaws.com/{s3_file_name}"
            else:
                print("S3 오류 발생:", e)
                return None
    
    except FileNotFoundError:
        print("파일을 찾을 수 없습니다.")
        return None
    except NoCredentialsError:
        print("자격 증명이 없습니다.")
        return None