#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
题库解析脚本 - 解析temu.txt并生成结构化JSON数据
"""

import json
import re

def parse_question_bank(input_file, output_file):
    """解析题库文件"""

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')

    questions = []
    current_type = None
    question_num = 0
    question_text = ""
    options = {}
    current_answer = ""

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # 检测题目类型
        if '单选题' in line:
            current_type = 'single'
            question_num = 0
            i += 1
            continue
        elif '多选题' in line:
            current_type = 'multiple'
            question_num = 0
            i += 1
            continue
        elif '答案' in line or '第三部分' in line:
            break

        # 解析题目
        if line and not line.startswith('每题') and not line.startswith('下列'):
            # 检查是否是题号行
            num_match = re.match(r'^(\d+)[.、]', line)
            if num_match:
                # 保存上一题
                if question_text and options:
                    # 获取正确答案
                    answer = get_answer_for_question(question_num, current_type, answers_dict)

                    question_obj = {
                        'id': f"{'S' if current_type == 'single' else 'M'}{question_num}",
                        'type': 'single' if current_type == 'single' else 'multiple',
                        'number': question_num,
                        'question': question_text,
                        'options': options,
                        'answer': answer
                    }
                    questions.append(question_obj)

                # 开始新题
                question_num = int(num_match.group(1))
                # 移除题号后的内容作为题目
                question_text = re.sub(r'^(\d+)[.、]\s*', '', line).strip()
                options = {}

                # 查找选项
                j = i + 1
                option_letters = ['A', 'B', 'C', 'D', 'E']
                opt_idx = 0

                while j < len(lines) and opt_idx < len(option_letters):
                    opt_line = lines[j].strip()
                    if not opt_line:
                        j += 1
                        continue

                    # 检查是否是选项
                    opt_match = re.match(r'^([A-E])[.、．、]\s*(.+)', opt_line)
                    if opt_match:
                        letter = opt_match.group(1)
                        text = opt_match.group(2).strip()
                        if letter in option_letters:
                            options[letter] = text
                            opt_idx = option_letters.index(letter) + 1
                            j += 1
                            continue

                    # 如果不是选项且有新题号，退出
                    if re.match(r'^\d+[.、]', opt_line):
                        break

                    # 如果有内容但不是选项格式，检查是否是延续的选项内容
                    if opt_line and not opt_line.startswith('A') and not opt_line.startswith('B') and \
                       not opt_line.startswith('C') and not opt_line.startswith('D') and not opt_line.startswith('E') and \
                       not opt_line.startswith('1') and not opt_line.startswith('2') and not opt_line.startswith('3'):
                        # 检查是否在选项之后（当前已有A选项）
                        if 'A' in options and len(opt_line) > 10:
                            # 这可能是选项A的延续内容
                            if not options['A'].endswith(opt_line):
                                pass  # 跳过
                        j += 1
                        continue

                    j += 1

                i = j - 1
        i += 1

    # 保存最后一题
    if question_text and options:
        answer = get_answer_for_question(question_num, current_type, {})
        question_obj = {
            'id': f"{'S' if current_type == 'single' else 'M'}{question_num}",
            'type': 'single' if current_type == 'single' else 'multiple',
            'number': question_num,
            'question': question_text,
            'options': options,
            'answer': answer
        }
        questions.append(question_obj)

    # 输出结果
    result = {
        'title': '电离辐射安全与防护题库',
        'total': len(questions),
        'single_count': len([q for q in questions if q['type'] == 'single']),
        'multiple_count': len([q for q in questions if q['type'] == 'multiple']),
        'questions': questions
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"解析完成！共 {len(questions)} 道题")
    print(f"单选题: {result['single_count']} 道")
    print(f"多选题: {result['multiple_count']} 道")
    print(f"已保存到: {output_file}")


def get_answer_for_question(num, qtype, answers_dict):
    """获取题目答案"""
    # 这里需要根据答案部分来提取
    # 单选题答案格式: 1.A 2.B ...
    # 多选题答案格式: 1.AB 2.ACD ...
    key = f"{'S' if qtype == 'single' else 'M'}{num}"
    return answers_dict.get(key, '')


# 解析答案部分
def parse_answers(content):
    """从文件末尾解析答案"""
    answers = {}

    # 查找答案部分
    answer_section_match = re.search(r'第三部分.*?答案', content, re.DOTALL)
    if not answer_section_match:
        return answers

    answer_section = answer_section_match.group(0)

    # 解析单选题答案
    single_match = re.findall(r'(\d+)[.、]\s*([A-D]+)', answer_section)
    for num, ans in single_match:
        answers[f'S{num}'] = ans

    # 解析多选题答案
    multiple_match = re.findall(r'(\d+)[.、]\s*([A-E]+)', answer_section)
    for num, ans in multiple_match:
        answers[f'M{num}'] = ans

    return answers


if __name__ == '__main__':
    parse_question_bank('temu.txt', 'questions.json')
