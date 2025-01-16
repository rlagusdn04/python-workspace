import tkinter as tk
from tkinter import messagebox
import random

# 단어 데이터를 읽어오는 함수
def load_words(file_path):
    words = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                english, korean = line.strip().split(',', 1)
                korean_meanings = [meaning.strip() for meaning in korean.split(',')]
                words.append({'english': english, 'korean': korean_meanings, 'weight': 0})
    except FileNotFoundError:
        print(f"파일을 찾을 수 없습니다: {file_path}. 새로운 단어 파일을 생성합니다.")
    return words


def check_answer(event=None, root=None, current_word=None, words=None, score=None, streak=None, mode=None, question_label=None, entry=None, feedback_label=None, streak_label=None):
    """
    통합된 정답 확인 함수. 모드별로 동작을 분리하여 처리.
    - event: 키 이벤트 (Enter 키)
    - root: Tkinter 루트 윈도우
    - current_word: 현재 문제 단어
    - words: 단어 리스트
    - score: 총 점수
    - streak: 연속 정답 횟수
    - mode: 실행 중인 모드 ("classic", "fearless", "endless")
    - question_label: 문제 표시 라벨
    - entry: 사용자 입력 필드
    - feedback_label: 정답/오답 메시지 표시 라벨
    - streak_label: 연속 정답 표시 라벨 (fearless 모드 전용)
    """
    answer = entry.get().strip()
    correct = answer in current_word['korean']

    if correct:
        # 정답 처리
        current_word['weight'] = max(0, current_word['weight'] - 1)
        score.set(score.get() + 1)
        if streak:
            streak.set(streak.get() + 1)
        feedback_label.config(text=f"정답입니다! --> {', '.join(current_word['korean'])}", fg="green")
    else:
        # 오답 처리
        feedback_label.config(text=f"오답입니다. 정답은 --> {', '.join(current_word['korean'])}", fg="red")
        if streak:
            streak.set(0)  # 연속 정답 초기화

    # 모드별 처리
    if mode == "classic":
        if score.get() < 10:  # Classic Mode: 10문제 제한
            current_word = words[score.get()]
            question_label.config(text=f"문제 {score.get() + 1}/10: {current_word['english']} -> 한국어로?")
        else:
            feedback_label.config(text=f"Classic Mode 종료! 점수: {score.get()}/10", fg="blue")
            entry.config(state="disabled")
            return
    elif mode == "fearless":
        if streak.get() == 10:  # Fearless Mode: 연속 10문제 성공 시 종료
            feedback_label.config(text="10문제를 연속으로 맞췄습니다! Fearless Mode 종료!", fg="blue")
            entry.config(state="disabled")
            return
        else:
            current_word = random.choice(words)
            question_label.config(text=f"문제: {current_word['english']} -> 한국어로?")
    elif mode == "endless":
        current_word = random.choice(words)
        question_label.config(text=f"문제: {current_word['english']} -> 한국어로?")

    # UI 업데이트
    entry.delete(0, tk.END)
    if streak_label:
        streak_label.config(text=f"연속 정답: {streak.get()}" if streak else "")
    return current_word
def classic_ui(words):
    root = tk.Tk()
    root.title("Classic Mode")
    root.geometry("400x300")

    score = tk.IntVar(value=0)
    current_word = words[0]

    # UI 요소
    question_label = tk.Label(root, text=f"문제 1/10: {current_word['english']} -> 한국어로?", font=("Arial", 14))
    question_label.pack(pady=20)
    entry = tk.Entry(root, font=("Arial", 12))
    entry.pack(pady=10)
    feedback_label = tk.Label(root, text="", font=("Arial", 12))
    feedback_label.pack(pady=10)

    # 제출 이벤트
    entry.bind("<Return>", lambda e: check_answer(
        event=e, root=root, current_word=current_word, words=words,
        score=score, mode="classic", question_label=question_label,
        entry=entry, feedback_label=feedback_label))

    root.mainloop()

def fearless_ui(words):
    root = tk.Tk()
    root.title("Fearless Mode")
    root.geometry("400x300")

    score = tk.IntVar(value=0)
    streak = tk.IntVar(value=0)
    current_word = random.choice(words)

    # UI 요소
    question_label = tk.Label(root, text=f"문제: {current_word['english']} -> 한국어로?", font=("Arial", 14))
    question_label.pack(pady=20)
    entry = tk.Entry(root, font=("Arial", 12))
    entry.pack(pady=10)
    feedback_label = tk.Label(root, text="", font=("Arial", 12))
    feedback_label.pack(pady=10)
    streak_label = tk.Label(root, text="연속 정답: 0", font=("Arial", 12))
    streak_label.pack(pady=10)

    # 제출 이벤트
    entry.bind("<Return>", lambda e: check_answer(
        event=e, root=root, current_word=current_word, words=words,
        score=score, streak=streak, mode="fearless", question_label=question_label,
        entry=entry, feedback_label=feedback_label, streak_label=streak_label))

    root.mainloop()

def endless_ui(words):
    root = tk.Tk()
    root.title("Endless Mode")
    root.geometry("400x300")

    score = tk.IntVar(value=0)
    current_word = random.choice(words)

    # UI 요소
    question_label = tk.Label(root, text=f"문제: {current_word['english']} -> 한국어로?", font=("Arial", 14))
    question_label.pack(pady=20)
    entry = tk.Entry(root, font=("Arial", 12))
    entry.pack(pady=10)
    feedback_label = tk.Label(root, text="", font=("Arial", 12))
    feedback_label.pack(pady=10)

    # 제출 이벤트
    entry.bind("<Return>", lambda e: check_answer(
        event=e, root=root, current_word=current_word, words=words,
        score=score, mode="endless", question_label=question_label,
        entry=entry, feedback_label=feedback_label))

    root.mainloop()


# 모드 선택 UI
def mode_selection_ui(txt1, txt2):
    root = tk.Tk()
    root.title("단어 암기 프로그램")
    root.geometry("400x300")

    # 설명 라벨
    title_label = tk.Label(root, text="단어 암기 프로그램", font=("Arial", 16))
    title_label.pack(pady=20)

    desc_label = tk.Label(root, text="모드를 선택하세요", font=("Arial", 12))
    desc_label.pack(pady=10)

    # 모드 버튼 생성
    def on_mode_select(mode):
        root.destroy()
        if mode == '1':
            classic_ui(txt1 + txt2)
        elif mode == '2':
            fearless_ui(txt1 + txt2)
        elif mode == '3':
            endless_ui(txt1 + txt2)
        elif mode == '4':
            daily_words = txt2
            classic_ui(daily_words)  # Daily 모드에서 Classic 모드 실행

    modes = [
        ("Classic Mode", '1'),
        ("Fearless Mode", '2'),
        ("Endless Mode", '3'),
        ("Daily Mode", '4')
    ]
    for mode_name, mode_value in modes:
        mode_button = tk.Button(root, text=mode_name, font=("Arial", 12), command=lambda m=mode_value: on_mode_select(m))
        mode_button.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main_file_path = r'C:\Users\rlagu\Desktop\Python workspace\TOEIC\words.txt'
    daily_file_path = r'C:\Users\rlagu\Desktop\Python workspace\TOEIC\words2.txt'

    txt1 = load_words(main_file_path)
    txt2 = load_words(daily_file_path)

    mode_selection_ui(txt1, txt2)