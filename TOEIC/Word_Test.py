import random

# 단어 데이터를 읽어오는 함수
def load_words(file_path):
    words = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                english, korean = line.strip().split(',', 1)  # 첫 번째 단어는 영어, 나머지는 한국어
                korean_meanings = [meaning.strip() for meaning in korean.split(',')]  # 쉼표로 구분된 한국어 정답
                words.append({'english': english, 'korean': korean_meanings, 'weight': 0})
    except FileNotFoundError:
        print(f"파일을 찾을 수 없습니다: {file_path}. 새로운 단어 파일을 생성합니다.")
    return words

# 단어 데이터를 저장하는 함수
def save_words(file_path, words):
    with open(file_path, 'w', encoding='utf-8') as file:
        for word in words:
            korean_meanings = ', '.join(word['korean'])
            file.write(f"{word['english']},{korean_meanings}\n")

# 문제를 묻는 함수
def ask_question(word):
    print(f"문제: {word['english']} -> 한국어로?")
    answer = input("정답: ").strip()
    return answer in word['korean'], word

# Classic Mode: 문제 출제 함수
def classic(words):
    total_questions = 10  # 출제할 문제 수
    questions = random.sample(words, min(total_questions, len(words)))  # 중복 방지
    incorrect = []

    for i, word in enumerate(questions, 1):
        print(f"\n문제 {i}/{total_questions}")
        correct, word = ask_question(word)
        if correct:
            print(f"정답입니다! --> {', '.join(word['korean'])}")
            word['weight'] = max(0, word['weight'] - 1)  # 가중치 감소 (최소 0 유지)
        else:
            print(f"오답입니다. 정답은 --> {', '.join(word['korean'])}")
            word['weight'] += 1  # 가중치 증가
            incorrect.append(word)

    correct_count = total_questions - len(incorrect)
    accuracy = (correct_count / total_questions) * 100
    print(f"\nClassic 모드 종료! 정답률: {accuracy:.2f}%")

    # 틀린 문제 복습 반복
    while incorrect:
        print("\n틀린 문제를 다시 풀어봅니다.")
        new_incorrect = []
        for word in incorrect:
            correct, word = ask_question(word)
            if correct:
                print(f"정답입니다! --> {', '.join(word['korean'])}")
                word['weight'] = max(0, word['weight'] - 1)  # 가중치 감소
            else:
                print(f"오답입니다. 정답은 --> {', '.join(word['korean'])}")
                word['weight'] += 1  # 가중치 증가
                new_incorrect.append(word)
        incorrect = new_incorrect

    print("\n틀린 문제 복습 완료!")

# Fearless Mode
def fearless(words):
    incorrect = []
    consecutive_correct = 0  # 연속 정답 횟수
    

    while True:
        # 가중치가 높은 문제와 가중치 0인 문제를 우선 선정
        high_weight_questions = sorted([w for w in words if w['weight'] > 0], key=lambda w: -w['weight'])
        zero_weight_questions = [w for w in words if w['weight'] == 0]
        questions = high_weight_questions + zero_weight_questions

        # 상위 10개의 문제를 랜덤으로 섞어서 출제
        questions = questions[:10]
        random.shuffle(questions)
        

        if not questions:
            print("출제할 문제가 없습니다.")
            break

        incorrect.clear()
        for i, word in enumerate(questions, 1):
            print(f"\n문제 {i}/{len(questions)}")
            correct, word = ask_question(word)
            if correct:
                print(f"정답입니다! --> {', '.join(word['korean'])}")
                word['weight'] = max(-1, word['weight'] - 1)  # 가중치 감소
                consecutive_correct += 1

                # 연속 정답 10문제 달성 시 종료
                if consecutive_correct == 10:
                    print("\n10문제를 연속으로 맞췄습니다! Fearless 모드를 종료합니다.")
                    return incorrect
            else:
                print(f"오답입니다. 정답은 --> {', '.join(word['korean'])}")
                word['weight'] += 1
                incorrect.append(word)
                consecutive_correct = 0  # 연속 정답 초기화

        # 매 라운드 종료 시 정답률 출력
        correct_count = len(questions) - len(incorrect)
        accuracy = (correct_count / len(questions)) * 100
        print(f"\n이번 라운드 종료! 정답률: {accuracy:.2f}%")

    return incorrect



# Endless Mode
def endless(words):
    print("\nEndless Mode: 틀릴 때까지 문제를 풉니다.")
    score = 0

    while True:
        word = random.choice(words)
        correct, word = ask_question(word)
        if correct:
            print(f"정답입니다! --> {', '.join(word['korean'])}")
            word['weight'] = max(0, word['weight'] - 1)  # 가중치 감소
            score += 1
        else:
            print(f"오답입니다. 정답은 --> {', '.join(word['korean'])}")
            print(f"\n게임 종료! 최종 점수는 {score}점입니다.")
            break

# 복습 문제 반복 함수
def review_loop(words):
    while True:
        words_to_review = [word for word in words if word['weight'] > 0]

        if not words_to_review:
            print("\n모든 단어를 완료했습니다! 🎉")
            break

        print("\n복습 문제를 진행합니다.")
        classic(words_to_review)

if __name__ == "__main__":
    main_file_path = r'C:\Users\rlagu\Desktop\Python_workspace\TOEIC\words.txt'
    daily_file_path = r'C:\Users\rlagu\Desktop\Python_workspace\TOEIC\words2.txt'

    txt1 = load_words(main_file_path)
    txt2 = load_words(daily_file_path)

    words = txt1 + txt2

    print("=" * 40)
    print("\n단어 암기 프로그램에 오신 것을 환영합니다!\n")
    print("1. Classic Mode (클래식 모드): 10문제 출제 후 복습 문제를 진행합니다.")
    print("2. Fearless Mode (피어리스 모드): 연속 정답 10문제 도전 모드입니다.")
    print("3. Endless Mode (엔드리스 모드): 틀릴 때까지 계속 진행합니다.")
    print("4. Daily Mode (데일리 모드): txt2 단어만 학습합니다.")
    print("=" * 40)

    mode = input("원하는 모드를 선택하세요 (1, 2, 3, 4): ").strip()

    # Daily Mode 처리
    if mode == '4':
        print("\nDaily Mode: txt2 단어만 학습합니다.")
        words = txt2  # txt2 단어로 교체
        print("\nDaily 모드에서 사용할 방식을 선택하세요: 1, 2, 3 (Classic, Fearless, Endless)")
        mode = input("Daily 모드에서 학습할 방식을 선택하세요 (1, 2, 3): ").strip()

    # 선택된 모드 실행
    if mode == '1':
        classic(words)
    elif mode == '2':
        fearless(words)
    elif mode == '3':
        endless(words)
    else:
        print("잘못된 입력입니다. 프로그램을 종료합니다.")