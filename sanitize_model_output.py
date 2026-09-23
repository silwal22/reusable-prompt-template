import re
from pathlib import Path

root = Path('/Users/arjun.silwal/prompting')
ansi_re = re.compile(r'\x1B\[[0-9;?]*[ -/]*[@-~]')
control_re = re.compile(r'[\x00-\x08\x0B-\x1F\x7F]')


def collapse_soft_wraps(text: str) -> str:
    text = text.replace('\r', '\n')
    text = re.sub(r'(?<=[A-Za-z0-9])\n(?=[a-z])', ' ', text)
    text = re.sub(r'(?<=[a-z])\n(?=[A-Z])', ' ', text)
    text = re.sub(r'(?<=\w)\n(?=\w)', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def sanitize_text(raw: str):
    text = raw
    text = text.replace('\r', '\n')
    text = ansi_re.sub('', text)
    text = control_re.sub('', text)
    text = ''.join(ch for ch in text if ord(ch) >= 32 or ch in '\n\t')

    marker_sequence = ['...done thinking.', '...done thinking', 'done thinking.']
    for marker in marker_sequence:
        if marker in text:
            before, after = text.split(marker, 1)
            reasoning = collapse_soft_wraps(before)
            final = collapse_soft_wraps(after)
            final = re.sub(r'(?is)^thinking\s*\.\.\.\s*', '', final)
            reasoning = re.sub(r'(?is)^thinking\s*\.\.\.\s*', '', reasoning)
            return final.strip(), reasoning.strip()

    if 'Thinking...' in text:
        match = re.search(r'(?is)thinking\s*\.\.\.\s*(.*)', text)
        if match:
            reasoning = collapse_soft_wraps(match.group(1))
            final = collapse_soft_wraps(text[match.end():]) if match.end() < len(text) else ''
            return final.strip(), reasoning.strip()

    return collapse_soft_wraps(text), ''


for output_file in sorted(root.glob('applied/*/outputs/*.txt')):
    if output_file.name.endswith('_reasoning.txt'):
        continue

    original = output_file.read_text(encoding='utf-8', errors='replace')
    clean_final, reasoning = sanitize_text(original)

    if clean_final:
        output_file.write_text(clean_final + '\n', encoding='utf-8')
    else:
        output_file.write_text('', encoding='utf-8')

    reasoning_file = output_file.with_name(output_file.name.replace('.txt', '_reasoning.txt'))
    if reasoning:
        reasoning_file.write_text(reasoning + '\n', encoding='utf-8')
    elif reasoning_file.exists():
        reasoning_file.unlink()

print('Sanitized output files:', len(list(root.glob('applied/*/outputs/*.txt'))))
