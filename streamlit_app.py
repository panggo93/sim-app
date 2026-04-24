import math
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from fractions import Fraction

def format_quadratic(a, b, c):
    """이차식을 자연스러운 문자열로 변환"""
    terms = []
    if a != 0:
        if a == 1:
            terms.append("x²")
        elif a == -1:
            terms.append("-x²")
        else:
            terms.append(f"{a}x²")
    if b != 0:
        if b == 1:
            if terms:
                terms.append("+x")
            else:
                terms.append("x")
        elif b == -1:
            terms.append("-x")
        elif b > 0 and terms:
            terms.append(f"+{b}x")
        else:
            terms.append(f"{b}x")
    if c != 0:
        if c > 0 and terms:
            terms.append(f"+{c}")
        else:
            terms.append(f"{c}")
    if not terms:
        return "0"
    return "".join(terms)

def format_quadratic_latex(a, b, c):
    """이차식을 LaTeX 수식 문자열로 변환"""
    parts = []
    if a != 0:
        coef = "" if abs(a) == 1 else str(abs(a))
        term = f"{coef}x^2" if coef else "x^2"
        parts.append(term if a > 0 else f"-{term}")
    if b != 0:
        coef = "" if abs(b) == 1 else str(abs(b))
        term = f"{coef}x" if coef else "x"
        parts.append(("+ " if b > 0 else "- ") + term if parts else (term if b > 0 else f"-{term}"))
    if c != 0:
        parts.append(("+ " if c > 0 else "- ") + str(abs(c)) if parts else str(c))
    if not parts:
        return "0"
    return " ".join(parts)

latex_ops = {
    ">": ">",
    "<": "<",
    ">=": r"\ge",
    "<=": r"\le",
    "=": "="
}

def rational_latex(value):
    if isinstance(value, float):
        if np.isclose(value, round(value), atol=1e-8):
            value = int(round(value))
        else:
            return f"{value:.6g}"
    frac = Fraction(value)
    if frac.denominator == 1:
        return str(frac.numerator)
    return rf"\frac{{{frac.numerator}}}{{{frac.denominator}}}"


def simplify_surd(delta):
    if delta == 0:
        return 0, 1
    base = math.isqrt(delta)
    if base * base == delta:
        return base, 1
    factor = 1
    remaining = delta
    for p in range(2, base + 1):
        while remaining % (p * p) == 0:
            remaining //= p * p
            factor *= p
    return factor, remaining


def root_latex(a, b, c, sign='+'):
    delta = b**2 - 4*a*c
    if delta == 0:
        return rational_latex(Fraction(-b, 2*a))

    numerator = -b
    denom = 2 * a
    surd_coef, surd_rad = simplify_surd(delta)

    if surd_rad == 1:
        sqrt_term = str(surd_coef)
    else:
        sqrt_term = rf"\sqrt{{{surd_rad}}}"
        if surd_coef != 1:
            sqrt_term = rf"{surd_coef}{sqrt_term}"

    if denom < 0:
        denom = -denom
        numerator = -numerator
        sign = '-' if sign == '+' else '+'

    if surd_rad == 1:
        combined = numerator + (surd_coef if sign == '+' else -surd_coef)
        return rational_latex(Fraction(combined, denom))

    common = math.gcd(math.gcd(abs(numerator), surd_coef), abs(denom))
    if common > 1:
        numerator //= common
        denom //= common
        surd_coef //= common
        if surd_coef == 1:
            sqrt_term = rf"\sqrt{{{surd_rad}}}"
        else:
            sqrt_term = rf"{surd_coef}\sqrt{{{surd_rad}}}"

    if numerator == 0:
        expr_num = rf"-{sqrt_term}" if sign == '-' else rf"{sqrt_term}"
    else:
        expr_num = rf"{numerator} - {sqrt_term}" if sign == '-' else rf"{numerator} + {sqrt_term}"

    if denom == 1:
        return expr_num
    return rf"\frac{{{expr_num}}}{{{denom}}}"


def format_interval_latex(low, high, low_inc, high_inc, low_latex=None, high_latex=None):
    if np.isinf(low) and np.isinf(high):
        return "모든 실수"
    if np.isinf(low):
        op = r"\le" if high_inc else "<"
        if high_latex:
            return rf"x {op} {high_latex}"
        return rf"x {op} {rational_latex(high)}"
    if np.isinf(high):
        op = r"\ge" if low_inc else ">"
        if low_latex:
            return rf"{low_latex} {op} x"
        return rf"{rational_latex(low)} {op} x"
    if low == high:
        if low_latex:
            return rf"x = {low_latex}"
        return rf"x = {rational_latex(low)}"
    left = r"\le" if low_inc else "<"
    right = r"\le" if high_inc else "<"
    left_value = low_latex if low_latex else rational_latex(low)
    right_value = high_latex if high_latex else rational_latex(high)
    return rf"{left_value} {left} x {right} {right_value}"

def solve_quadratic_inequality(a, b, c, op):
    """이차부등식의 해 구하기 및 구간 반환"""
    discriminant = b**2 - 4*a*c
    if op == "=":
        if discriminant < 0:
            return "해 없음", "해 없음", []
        elif discriminant == 0:
            root = float(-b / (2*a))
            root_latex_str = root_latex(a, b, c)
            return (
                f"x = {root}",
                rf"x = {root_latex_str}",
                [(root, root, True, True, root_latex_str, root_latex_str)],
            )
        else:
            root1 = float((-b - np.sqrt(discriminant)) / (2*a))
            root2 = float((-b + np.sqrt(discriminant)) / (2*a))
            if root1 > root2:
                root1, root2 = root2, root1
            return (
                f"x = {root1} 또는 x = {root2}",
                rf"x = {root_latex(a, b, c, sign='-')} \text{{ 또는 }} x = {root_latex(a, b, c, sign='+')}",
                [
                    (root1, root1, True, True, root_latex(a, b, c, sign='-'), root_latex(a, b, c, sign='-')),
                    (root2, root2, True, True, root_latex(a, b, c, sign='+'), root_latex(a, b, c, sign='+')),
                ],
            )

    if discriminant < 0:
        if a > 0:
            if op in ['>', '>=']:
                return "모든 실수", "모든 실수", [(-np.inf, np.inf, False, False, None, None)]
            return "해 없음", "해 없음", []
        else:
            if op in ['<', '<=']:
                return "모든 실수", "모든 실수", [(-np.inf, np.inf, False, False, None, None)]
            return "해 없음", "해 없음", []

    root1 = float((-b - np.sqrt(discriminant)) / (2*a))
    root2 = float((-b + np.sqrt(discriminant)) / (2*a))
    root1_latex = root_latex(a, b, c, sign='-')
    root2_latex = root_latex(a, b, c, sign='+')
    if root1 > root2:
        root1, root2 = root2, root1
        root1_latex, root2_latex = root2_latex, root1_latex

    if a > 0:
        if op == '>':
            return (
                f"x < {root1} 또는 x > {root2}",
                rf"x < {root1_latex} \text{{ 또는 }} x > {root2_latex}",
                [
                    (-np.inf, root1, False, False, None, root1_latex),
                    (root2, np.inf, False, False, root2_latex, None),
                ],
            )
        if op == '>=':
            return (
                f"x <= {root1} 또는 x >= {root2}",
                rf"x \le {root1_latex} \text{{ 또는 }} x \ge {root2_latex}",
                [
                    (-np.inf, root1, False, True, None, root1_latex),
                    (root2, np.inf, True, False, root2_latex, None),
                ],
            )
        if op == '<':
            return (
                f"{root1} < x < {root2}",
                rf"{root1_latex} < x < {root2_latex}",
                [(root1, root2, False, False, root1_latex, root2_latex)],
            )
        if op == '<=':
            return (
                f"{root1} <= x <= {root2}",
                rf"{root1_latex} \le x \le {root2_latex}",
                [(root1, root2, True, True, root1_latex, root2_latex)],
            )
    else:
        if op == '>':
            return (
                f"{root1} < x < {root2}",
                rf"{root1_latex} < x < {root2_latex}",
                [(root1, root2, False, False, root1_latex, root2_latex)],
            )
        if op == '>=':
            return (
                f"{root1} <= x <= {root2}",
                rf"{root1_latex} \le x \le {root2_latex}",
                [(root1, root2, True, True, root1_latex, root2_latex)],
            )
        if op == '<':
            return (
                f"x < {root1} 또는 x > {root2}",
                rf"x < {root1_latex} \text{{ 또는 }} x > {root2_latex}",
                [
                    (-np.inf, root1, False, False, None, root1_latex),
                    (root2, np.inf, False, False, root2_latex, None),
                ],
            )
        if op == '<=':
            return (
                f"x <= {root1} 또는 x >= {root2}",
                rf"x \le {root1_latex} \text{{ 또는 }} x \ge {root2_latex}",
                [
                    (-np.inf, root1, False, True, None, root1_latex),
                    (root2, np.inf, True, False, root2_latex, None),
                ],
            )
    return "해 없음", "해 없음", []

def interval_intersection(intervals1, intervals2):
    """두 구간 리스트의 교집합 계산"""
    result = []
    for i1 in intervals1:
        for i2 in intervals2:
            low = max(i1[0], i2[0])
            high = min(i1[1], i2[1])
            low_inc = True
            low_latex = None
            if i1[0] == low:
                low_inc &= i1[2]
                low_latex = i1[4]
            if i2[0] == low:
                low_inc &= i2[2]
                low_latex = i2[4] if low_latex is None else low_latex
            high_inc = True
            high_latex = None
            if i1[1] == high:
                high_inc &= i1[3]
                high_latex = i1[5]
            if i2[1] == high:
                high_inc &= i2[3]
                high_latex = i2[5] if high_latex is None else high_latex
            if low < high:
                result.append((low, high, low_inc, high_inc, low_latex, high_latex))
            elif low == high and low_inc and high_inc:
                result.append((low, high, True, True, low_latex, high_latex))
    return result

def plot_quadratics(a1, b1, c1, intervals1, a2, b2, c2, intervals2, intersection):
    """두 이차함수 그래프 그리기 및 해 구간 색칠"""
    x = np.linspace(-10, 10, 600)
    y1 = a1 * x**2 + b1 * x + c1
    y2 = a2 * x**2 + b2 * x + c2
    
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.set_facecolor('#fbfcfe')
    ax.plot(x, y1, label=f'{format_quadratic(a1, b1, c1)}', color='#1f77b4', linewidth=2.5)
    ax.plot(x, y2, label=f'{format_quadratic(a2, b2, c2)}', color='#d62728', linewidth=2.5)
    ax.axhline(0, color='#333333', linewidth=1.0)
    ax.axvline(0, color='#333333', linewidth=1.0)
    ax.grid(color='#d8dee9', linestyle='--', linewidth=0.8, alpha=0.8)
    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, 10)
    ax.set_xticks(np.arange(-10, 11, 1))
    ax.set_yticks(np.arange(-10, 11, 2))
    ax.set_axisbelow(True)
    
    # 교집합 영역 강조(x축 중앙, 노랑)
    for low, high, _, _, _, _ in intersection:
        if np.isinf(low):
            low = -10
        if np.isinf(high):
            high = 10
        mask = (x >= low) & (x <= high)
        ax.fill_between(x, -0.1, 0.1, where=mask, color='#ffc107', alpha=0.75, interpolate=True)
    
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    ax.spines['left'].set_position('zero')
    ax.spines['bottom'].set_position('zero')
    ax.spines['left'].set_color('#333333')
    ax.spines['bottom'].set_color('#333333')
    ax.tick_params(colors='#333333', labelsize=10)
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.annotate('x', xy=(10, 0), xytext=(8, -10), textcoords='offset points', ha='left', va='top', color='#333333')
    ax.annotate('y', xy=(0, 10), xytext=(-10, 8), textcoords='offset points', ha='right', va='bottom', color='#333333')
    return fig

st.title("그래프로 이해하는 이차부등식")

st.header("첫 번째 부등식")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(r"$a_1\ (x^2\ 계수)$")
    a1 = st.number_input("", value=1, min_value=-10, max_value=10, step=1, key="a1", label_visibility="collapsed")
with col2:
    st.markdown(r"$b_1\ (x\ 계수)$")
    b1 = st.number_input("", value=0, min_value=-10, max_value=10, step=1, key="b1", label_visibility="collapsed")
with col3:
    st.markdown(r"$c_1\ (상수항)$")
    c1 = st.number_input("", value=-4, min_value=-10, max_value=10, step=1, key="c1", label_visibility="collapsed")
with col4:
    st.markdown("부등호")
    op1 = st.selectbox("", [">", "<", ">=", "<=", "="], index=0, key="op1", label_visibility="collapsed")

st.header("두 번째 부등식")
col5, col6, col7, col8 = st.columns(4)
with col5:
    st.markdown(r"$a_2\ (x^2\ 계수)$")
    a2 = st.number_input("", value=1, min_value=-10, max_value=10, step=1, key="a2", label_visibility="collapsed")
with col6:
    st.markdown(r"$b_2\ (x\ 계수)$")
    b2 = st.number_input("", value=0, min_value=-10, max_value=10, step=1, key="b2", label_visibility="collapsed")
with col7:
    st.markdown(r"$c_2\ (상수항)$")
    c2 = st.number_input("", value=1, min_value=-10, max_value=10, step=1, key="c2", label_visibility="collapsed")
with col8:
    st.markdown("부등호")
    op2 = st.selectbox("", [">", "<", ">=", "<=", "="], index=0, key="op2", label_visibility="collapsed")
    confirm = st.button("확인")

if confirm:
    if a1 == 0 or a2 == 0:
        st.error("a는 0이 될 수 없습니다. 이차식이어야 합니다.")
    else:
        st.markdown(rf"**첫 번째 부등식:** ${format_quadratic_latex(a1, b1, c1)} {latex_ops[op1]} 0$")
        sol1, sol1_latex, intervals1 = solve_quadratic_inequality(a1, b1, c1, op1)
        if sol1 in ["모든 실수", "해 없음"]:
            st.markdown(f"**해:** {sol1}")
        else:
            st.markdown(rf"**해:** ${sol1_latex}$")
        
        st.markdown(rf"**두 번째 부등식:** ${format_quadratic_latex(a2, b2, c2)} {latex_ops[op2]} 0$")
        sol2, sol2_latex, intervals2 = solve_quadratic_inequality(a2, b2, c2, op2)
        if sol2 in ["모든 실수", "해 없음"]:
            st.markdown(f"**해:** {sol2}")
        else:
            st.markdown(rf"**해:** ${sol2_latex}$")
        
        intersection = interval_intersection(intervals1, intervals2)
        if intersection:
            joined = r" \text{ 또는 } ".join(
                format_interval_latex(low, high, low_inc, high_inc, low_latex, high_latex)
                for low, high, low_inc, high_inc, low_latex, high_latex in intersection
            )
            if joined == "모든 실수":
                st.markdown(rf"**최종 해 (교집합):** {joined}")
            else:
                st.markdown(rf"**최종 해 (교집합):** ${joined}$")
        else:
            st.markdown("**최종 해:** 해 없음")
        
        fig = plot_quadratics(a1, b1, c1, intervals1, a2, b2, c2, intervals2, intersection)
        st.pyplot(fig)