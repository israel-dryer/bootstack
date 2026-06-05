"""Convert raw HTML image blocks to .. image:: directives across all api rst files."""
import re
from pathlib import Path

# Format A: alt and style on separate lines (most files)
PATTERN_A = re.compile(
    r'\.\. raw:: html\n\n'
    r'   <img class="([^"]+)"\n'
    r'        src="([^"]+)"\n'
    r'        alt="([^"]+)"\n'
    r'        style="[^"]+?">\n'
    r'   <img class="([^"]+)"\n'
    r'        src="([^"]+)"\n'
    r'        alt="([^"]+)"\n'
    r'        style="[^"]+?">',
)

# Format B: alt and style on the same line (button.rst and similar)
PATTERN_B = re.compile(
    r'\.\. raw:: html\n\n'
    r'   <img class="([^"]+)"\n'
    r'        src="([^"]+)"\n'
    r'        alt="([^"]+)" style="[^"]+?">\n'
    r'   <img class="([^"]+)"\n'
    r'        src="([^"]+)"\n'
    r'        alt="([^"]+)" style="[^"]+?">',
)


def replacement(m: re.Match) -> str:
    light_class, light_src, light_alt = m.group(1), m.group(2), m.group(3)
    dark_class,  dark_src,  dark_alt  = m.group(4), m.group(5), m.group(6)
    return (
        f'.. image:: {light_src}\n'
        f'   :class: {light_class}\n'
        f'   :alt: {light_alt}\n'
        f'\n'
        f'.. image:: {dark_src}\n'
        f'   :class: {dark_class}\n'
        f'   :alt: {dark_alt}'
    )


rst_dir = Path(__file__).parent.parent / 'api'
changed = []
for rst_file in sorted(rst_dir.glob('*.rst')):
    content = rst_file.read_text(encoding='utf-8')
    new_content = PATTERN_A.sub(replacement, content)
    new_content = PATTERN_B.sub(replacement, new_content)
    if new_content != content:
        rst_file.write_text(new_content, encoding='utf-8')
        changed.append(rst_file.name)

print(f"Updated {len(changed)} files:")
for name in changed:
    print(f"  {name}")