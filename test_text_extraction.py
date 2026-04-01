import re

def extract_text_from_latex(latex_formula):
    """从 LaTeX 公式中提取 \text{} 中的纯文本内容"""
    # 匹配 \text{...} 模式
    pattern = r'\\text\{([^}]*)\}'
    matches = re.findall(pattern, latex_formula)
    
    if matches:
        # 如果有多个 \text{}，合并所有内容
        extracted_text = ''.join(matches)
        return extracted_text
    else:
        # 如果没有 \text{}，返回原始公式
        return latex_formula

# 测试用例
test_cases = [
    r'\text{测试汉字}',
    r'\text{面积} = \pi r^2',
    r'x^2 + y^2 = \text{半径}^2',
    r'这是一个纯数学公式 x^2 + 1',
    r'\begin{aligned}&\text{解方程}\\&x=1\end{aligned}'
]

for test in test_cases:
    result = extract_text_from_latex(test)
    print(f"Original: {repr(test)}")
    print(f"Extracted: {repr(result)}")
    print("---")