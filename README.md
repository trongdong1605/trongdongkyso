# Ứng dụng Ký Số File Bằng RSA (Flask)

Đây là ứng dụng web viết bằng **Python Flask** cho phép:
- Sinh cặp khóa RSA (Public / Private Key)
- Ký số một file bằng khóa riêng
- Gửi file đã ký đến người nhận
- Xác minh chữ ký bằng khóa công khai

## Tính năng chính

- Đăng nhập bằng tên người dùng
- Sinh khóa RSA (Tải xuống file `.pem`)
- Upload và ký file
- Gửi file và chữ ký đến người dùng khác
- Xác minh chữ ký và tải về file gốc nếu hợp lệ

### Công nghệ sử dụng

- Python 3.13
- Flask
- PyCryptodome (`Crypto`)
- HTML + Bootstrap 5

### Giao diện
![image](https://github.com/user-attachments/assets/8dbcfae1-6c92-4490-ba08-bdfa0cd7b359)
