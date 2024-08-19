import re
import socket
import random

HOST = '127.0.0.1'
PORT = 5113

STATUS_CODES = {
    200: "OK",
    400: "Bad Request",
}

OPERATORS = {
    1: '+',
    2: '-',
    3: 'x',
    4: '÷'
}

def send_message(server_socket, message, code):
    full_message = str(code) + "," + STATUS_CODES.get(code) + "/" + message
    server_socket.send(full_message.encode('utf-8'))
    print(f"\n>> Sent message (full) to client: \"{full_message}\"")

def receive_message(server_socket) :
    message = server_socket.recv(1024).decode('utf-8')
    print(f"\n>> Received level choice from client: \"{message}\"")
    return message
    

def calculate_sol(question):
    return round(eval(question.replace('x', '*').replace('÷', '/')), 2)

def generate_question (level):
    genQuestion = ""
    for i in range(level):
        genQuestion += str(random.randint(1, 10000))
        if i < level - 1:
            genQuestion += " "
            genQuestion += OPERATORS.get(random.randint(1, 4))
            genQuestion += " "
    return genQuestion, calculate_sol(genQuestion)

# สร้าง Message ที่จะส่งไปยัง client
def create_response(client_message, question, solution, point, level):
    newResponse = ""
    code = 200
    old_solution = solution
    
    # ขอข้ามคำถาม คะแนน -2
    if client_message.lower() == "pass":
        newResponse += "Pass -2,"
        point -= 2
        question, solution = generate_question (level)
    
    # Format ไม่ถูกต้อง    
    elif not re.match(r'^-?\d+(\.\d+)?$', client_message):
        newResponse = question + ",Invalid format. Try again.," + str(point) + ",-"
        code = 400
        return newResponse, point, solution, code
    
    # ตอบถูก คะแนน +1
    elif float(client_message) == solution:
        newResponse += "Correct! +1,"
        point += 1
        question, solution = generate_question (level)
        
    # ตอบผิด คะแนน -1
    else:
        newResponse += "Wrong -1,"
        point -= 1
        question, solution = generate_question (level)
    
    newResponse += str(point)
    newResponse = question + "," + newResponse + "," + str(old_solution)
    
    return newResponse, point, solution, code

# รับ level ก่อนเล่นเกม
def receive_level(server_socket):
    while True:
        client_message = receive_message(server_socket)
        level_match = re.match(r'LEVEL:(\d)', client_message)
        level = int(level_match.group(1))
        
        if level_match and 2 <= level <= 9:
            print(f">> Valid level received: {level}")
            return level
        
        else:
            error_message = "Invalid level. Choose a level between 2-9."
            print(f">> Sending error message to client: \"{error_message}\"")
            send_message(server_socket, error_message, 400)

# ส่วนเกมหลัก
def main_game(server_socket, level):
    point = 0
    # สร้างคำถามแรก
    question, solution = generate_question (level)
    response = question + ",-," + str(point) + ",-"
    send_message(server_socket, response, 200)

    while True:
        client_message = receive_message(server_socket)
        # ถ้าได้รับคำว่า "Over" จะจบลูป
        if client_message.lower() == 'over':
            print("Game over.")
            break
        else:
            response, point, solution, code = create_response (client_message, question, solution, point, level)
            send_message(server_socket, response, code)

def main():
    # สร้าง server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

     # ผูก Socket กับที่อยู่ IP และ Port
    server_socket.bind((HOST, PORT))

    # กำหนดให้เชื่อมต่อกับ client ได้เพียง client เดียว
    server_socket.listen(1)

    print(f'Server is listening on {HOST}:{PORT}')

    # connect กับ client
    server_socket, addr = server_socket.accept()
    print(f'Got connection from {addr}')

    level = receive_level(server_socket)

    main_game(server_socket, level)

    # ปิดการเชื่อมต่อ
    server_socket.close()
    server_socket.close()

if __name__ == "__main__":
    main()
