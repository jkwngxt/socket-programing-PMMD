import re
import socket

HOST = '127.0.0.1'
PORT = 5113

# ถามผู้เล่นว่าต้องการเล่นหรือไม่
def ask_before_start():
    print("Welcome to PMMD -> (Plus Minus Multiply Divide)")
    print("Do you want to play PMMD?")
    while True:
        user_response = input("Y/N: ")
        if user_response.upper() == 'Y':
            print('Let\'s go!!!')
            return 1
        elif user_response.upper() == 'N':
            print("Exit...")
            return 0
        else:
            print("I will wait until you wanna play. Tell me when you are ready. (Y/N)")

def send_message(client_socket, message):
    print(f"\n>> Sent message to server: \"{message}\"")
    client_socket.send(message.encode('utf-8'))

def receive_message(client_socket):
    print(f"\n>> Waiting for message from server.")
    full_response = client_socket.recv(1024).decode('utf-8')
    response_header = full_response.split("/")[0].split(",") #  Status Code และ Status Phrase
    response_body = full_response.split("/")[1] # เนื้อหา
    print(f">> Received message from server (Full message): {full_response}")
    print(f">>    message: \"{response_body}\"")
    print(f">>    Status Code: \"{response_header[0]}\"")
    print(f">>    Status Phrase: \"{response_header[1]}\"\n")
    return response_body

# เลือก Level
def choose_level(client_socket):
    while True:
        user_response = input("Choose level -> 2, 3, 4, 5, 6, 7, 8, 9: ")
        if re.fullmatch(r'[2-9]', user_response):
            send_message(client_socket, "LEVEL:" + user_response)
            response = receive_message(client_socket)
            if "invalid" not in response.lower():
                print("\nRules:")
                print("  1. If you want to exit, submit 'Over'.")
                print("  2. Round your answer to 2 decimal places.")
                print("  3. If you want to pass the question, submit 'Pass', but you will lose 2 points.")
                print("  4. If your answer is correct, you will get 1 point.")
                print("     On the other hand, if your answer is wrong, you will lose 1 point.\n")
                return response
            else:
                print("Invalid level. Choose a level between 2-9.")
        else:
            print("Invalid level.")

# แยก message ที่ได้รับจาก Server
def token_response(response):
    responseList = ["", "", 0, ""]
    tokenStr = response.split(",")
    if len(tokenStr) >= 4:
        responseList[0] = tokenStr[0]  # คำถาม
        responseList[1] = tokenStr[1]  # การตรวจสอบของ Input ที่แล้ว
        responseList[2] = int(tokenStr[2])  # คะแนน
        responseList[3] = tokenStr[3]  # เฉลยของข้อที่แล้ว
    else:
        print("Error: Response format is incorrect.")
    return responseList

# ส่วนหลักในการเล่นเกม
def main_game(client_socket):
    response_number = 0
    response = choose_level(client_socket)

    while True:
        response_number += 1
        responseList = token_response(response)

        print(f'Message from server {response_number}')
        print(f'Check: {responseList[1]} | Solution: {responseList[3]}')
        print(f'Point: {responseList[2]}')
        print(f'Question {response_number}: {responseList[0]}')

        user_response = input("Ans: ")
        
        if user_response.lower() == 'over':
            send_message(client_socket, user_response)
            break
    

        send_message(client_socket, user_response)
        response = receive_message(client_socket)

def main():
    if ask_before_start():
        # สร้าง socket เพื่อเชื่อมต่อกับเซิร์ฟเวอร์
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # เชื่อมต่อกับเซิร์ฟเวอร์ที่ HOST และ PORT ที่ระบุ
        client_socket.connect((HOST, PORT))
        
        main_game(client_socket)
        # กล่าวลา
        print("Let's play together next time, bye!")
        # ปิดการเชื่อต่อ
        client_socket.close()

if __name__ == "__main__":
    main()
