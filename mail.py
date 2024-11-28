import tls_client
import json
import time

class TempMail:
    def __init__(self, bearer_token: str = None) -> None:
        # Khởi tạo session tls-client
        self.session = tls_client.Session(
            client_identifier="chrome_108",
            random_tls_extension_order=True
        )
        
        # Cấu hình headers
        self.session.headers = {
            "accept": "*/*",
            "accept-language": "vi-VN,vi;q=0.9",
            "content-type": "application/json",
            "origin": "https://temp-mail.org",
            "referer": "https://temp-mail.org/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        }
        
        self.base_url = 'https://web2.temp-mail.org/v1'
        
        if bearer_token:
            self.session.headers['authorization'] = f'Bearer {bearer_token}'

    def get_mail(self):
        status = self.session.get(f'{self.base_url}/mailbox').status_code
        try:
            if status == 200:
                data = self.session.post(f'{self.base_url}/mailbox').json()
                self.session.headers['authorization'] = f'Bearer {data["token"]}'
                return data["token"], data["mailbox"]
        except Exception as e:
            return f'Email creation error: {str(e)}', False
    
    def fetch_inbox(self) -> dict:
        response = self.session.get(f'{self.base_url}/messages')
        if response.status_code == 200:
            return response.json()
        return {"messages": []}
    
    def get_message_content(self, message_id: str):
        response = self.session.get(f'{self.base_url}/messages/{message_id}')
        if response.status_code == 200:
            return response.json().get("bodyHtml", "No content")
        return "Error fetching message content."

if __name__ == "__main__":
    # Khởi tạo client
    email_client = TempMail()
    
    try:
        print("Đang tạo email...")
        token, email = email_client.get_mail()
        
        if not email or email.startswith("Email creation error"):
            print("Không thể tạo email")
            exit()
            
        print(f"Email đã tạo: {email}")
        print(f"Token: {token}")
        
        print("\nĐang đợi email mới...\n")
        
        while True:
            messages = email_client.fetch_inbox()
            print("Kiểm tra hộp thư...")
            
            if messages.get("messages") and len(messages["messages"]) > 0:
                print("\nĐã nhận được email mới!")
                for msg in messages["messages"]:
                    content = email_client.get_message_content(msg["_id"])
                    print(f"\nFrom: {msg.get('from', 'Unknown')}")
                    print(f"Subject: {msg.get('subject', 'No subject')}")
                    print(f"Content: {content}")
                break
            
            print("Chưa có email mới. Đợi 5 giây...")
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\nĐã dừng chương trình.")
    except Exception as e:
        print(f"\nCó lỗi xảy ra: {str(e)}")
      
