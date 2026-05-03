import textwrap


def withdrawal_usdt_float_text(placeholder: str):
    txt = textwrap.dedent(f"""
        <b>💲 USDT (TRC20)</b>
        \n{placeholder}
    """)
    return txt