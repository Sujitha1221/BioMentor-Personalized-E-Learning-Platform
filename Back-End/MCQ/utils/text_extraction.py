import re

def extract_mcqs(prompt, raw_output):
    raw_output = raw_output.replace(prompt, "").strip()
    raw_output = re.sub(r"</?s>|</?INST>|><INST>", "", raw_output, flags=re.IGNORECASE)

    lines = [line.strip() for line in raw_output.split("\n") if line.strip()]

    mcqs = []
    current_mcq = {"question": None, "options": {}, "correct_answer": None}
    waiting_for_question = False

    def flush():
        if (
            current_mcq["question"]
            and len(current_mcq["options"]) == 5
            and current_mcq["correct_answer"] in current_mcq["options"]
        ):
            current_mcq["question"] = re.sub(
                r"^(?:Question\s*)?\d+[\.\:\)]\s*", "", current_mcq["question"]
            ).strip(" .:")
            mcqs.append(current_mcq.copy())

    for i, line in enumerate(lines):
        # Section headers like "Example:", "Easy 1:", etc.
        if re.match(r"^(Example|Easy|Medium|Hard)?\s*\d*[\:\)]\s*$", line, re.IGNORECASE) or line.lower() in ["example:", "example"]:
            flush()
            current_mcq = {"question": None, "options": {}, "correct_answer": None}
            waiting_for_question = True
            continue

        # Lines like "1:" or "Question 1:"
        if re.match(r"^(?:Question\s*)?\d+[\.\:\)]\s*$", line, re.IGNORECASE):
            flush()
            current_mcq = {"question": None, "options": {}, "correct_answer": None}
            waiting_for_question = True
            continue

        # Waiting for the question after a header
        if waiting_for_question:
            question = re.sub(r"^(?:Question\s*)?\d+[\.\:\)]\s*", "", line).rstrip(" .:")

            if question:
                current_mcq["question"] = question
                waiting_for_question = False
            continue

        # Inline: "Question 1: What is...?"
        q_match = re.match(r"^Question\s*[:\-]?\s*(.+)", line, re.IGNORECASE)
        if not q_match:
            q_match = re.match(r"^(?:Question\s*)?\d+[\.\:\)]\s*(.+)", line, re.IGNORECASE)
        if q_match:
            flush()
            question = re.sub(r"^(?:Question\s*)?\d+[\.\:\)]\s*", "", q_match.group(1)).rstrip(" .:")
            current_mcq = {"question": question, "options": {}, "correct_answer": None}
            continue
        
        # New format: "### Question X"
        if re.match(r"^###\s*Question\s*\d+", line, re.IGNORECASE):
            flush()
            current_mcq = {"question": None, "options": {}, "correct_answer": None}
            waiting_for_question = True
            continue
        
        match_easy_intro = re.match(r"^The .* level multiple-choice .* question .* is[:\-]?\s*(.+)?$", line, re.IGNORECASE)
        if match_easy_intro:
            flush()
            current_mcq = {"question": None, "options": {}, "correct_answer": None}
            possible_question = match_easy_intro.group(1)
            if possible_question:
                current_mcq["question"] = possible_question.strip(" .:")
            else:
                waiting_for_question = True  # Wait for next line if question is not in same line
            continue

        # Bullet-style questions: "- What is...?"
        bullet_q_match = re.match(r"^\-\s*(.+)", line)
        if bullet_q_match and not current_mcq["question"]:
            text = bullet_q_match.group(1).strip(" ?:")
            if not re.match(r"^[A-Ea-e][\)\.\:\-]?\s+", text):
                flush()
                question = re.sub(r"^(?:Question\s*)?\d+[\.\:\)]\s*", "", text).strip(" .:")
                current_mcq = {"question": question, "options": {}, "correct_answer": None}
                continue

        # Option A–E: "A) text"
        opt_match = re.match(r"^([A-Ea-e])[\)\.\:\-]?\s+(.+)", line)
        if opt_match:
            if not current_mcq["question"]:
                # Backtrack to find question
                for j in range(i - 1, -1, -1):
                    prev = lines[j]
                    if not re.match(r"^[A-Ea-e][\)\.\:\-]?\s+", prev) and not prev.lower().startswith("correct answer"):
                        question = re.sub(r"^(?:Question\s*)?\d+[\.\:\)]\s*", "", prev).strip(" .:")
                        if question:
                            current_mcq["question"] = question
                        break
            current_mcq["options"][opt_match.group(1).upper()] = opt_match.group(2).strip()
            continue

        # Numbered options: "(1)", "1.", "1)", etc.
        num_opt_match = re.match(r"^\(?([1-5])\)?[\.\:\-]?\s+(.+)", line)
        if num_opt_match:
            number_to_letter = {"1": "A", "2": "B", "3": "C", "4": "D", "5": "E"}
            letter = number_to_letter.get(num_opt_match.group(1))
            if letter:
                current_mcq["options"][letter] = num_opt_match.group(2).strip()
            continue

        # Answers: "Correct Answer: C" or "Correct Answer: (3)"
        ans_match = re.match(r"^(?:Correct\s*)?Answer\s*[:\-]?\s*\(?([A-Ea-e1-5])\)?(?:[\)\.\:\-]?\s+.*)?$", line, re.IGNORECASE)
        if ans_match:
            val = ans_match.group(1).upper()
            if val in "12345":
                val = chr(64 + int(val))  # Convert 1–5 to A–E
            current_mcq["correct_answer"] = val
            continue

    flush()
    return mcqs
