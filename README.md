# NPDA Visualizer

این پروژه با هدف بصری‌سازی اجرای یک اتوماتای پشته‌ای غیرقطعی (NPDA) با استفاده از کتابخانه پایتون `automata-lib` توسعه یافته است. این ابزار به شما کمک می‌کند تا نحوه عملکرد NPDA را در پردازش رشته‌های ورودی مختلف درک کنید و مسیرهای اجرای ممکن را به صورت گرافیکی مشاهده کنید.

**NPDA چیست؟**
یک اتوماتای پشته‌ای غیرقطعی (NPDA) یک مدل محاسباتی است که از یک حافظه پشته‌ای برای تصمیم‌گیری در مورد پذیرش یا رد یک رشته ورودی استفاده می‌کند. "غیرقطعی" به این معنی است که در هر مرحله، ممکن است چندین انتقال ممکن وجود داشته باشد که NPDA می‌تواند یکی از آن‌ها را انتخاب کند. این پروژه این رفتار غیرقطعی را با نمایش تمام مسیرهای اجرای ممکن به صورت یک نمودار درختی بصری می‌کند.

**نحوه کارکرد:**
اسکریپت `npda_visualizer.py` یک تعریف NPDA را از یک فایل متنی می‌خواند. سپس، با دریافت یک رشته ورودی، تمام پیکربندی‌های ممکن NPDA را در هر مرحله از پردازش رشته ردیابی می‌کند. این پیکربندی‌ها شامل وضعیت فعلی، محتوای پشته و بخش باقی‌مانده از رشته ورودی است. در نهایت، این اطلاعات به دو نمودار DOT تبدیل می‌شوند:
1.  **نمودار اجرای NPDA (`npda_execution.png`)**: این نمودار مسیرهای اجرای NPDA را برای یک رشته ورودی خاص نشان می‌دهد. هر گره در نمودار یک پیکربندی NPDA (وضعیت، پشته، ورودی باقی‌مانده) را نشان می‌دهد و هر لبه یک انتقال را نشان می‌دهد.
2.  **نمودار تعریف NPDA (`npda_definition_diagram.png`)**: این نمودار ساختار کلی NPDA را نشان می‌دهد، شامل وضعیت‌ها، نمادهای ورودی، نمادهای پشته و تمام انتقال‌های تعریف شده.

این ابزار برای دانشجویان، محققان و هر کسی که به درک عمیق‌تر اتوماتا و نظریه محاسبات علاقه‌مند است، مفید است.

## Input File Format

The NPDA definition should be provided in a text file (e.g., `npda_definition.txt`). The file should contain the following sections:

### States
`states: q0,q1,q2`

### Input Symbols
`input_symbols: a,b,c`

### Stack Symbols
`stack_symbols: Z0,A,B`

### Initial State
`initial_state: q0`

### Initial Stack Symbol
`initial_stack_symbol: Z0`

### Final States
`final_states: q2`

### Acceptance Mode
`acceptance_mode: final_state` (or `empty_stack` or `both`)

### Transitions
Transitions should be defined one per line in the format:
`current_state,input_symbol,stack_top -> new_state,stack_push_symbols`

- `input_symbol` can be `lambda` for epsilon transitions.
- `stack_top` can be `lambda` if no symbol is popped.
- `stack_push_symbols` can be `lambda` if no symbol is pushed. If multiple symbols are pushed, they should be comma-separated (e.g., `A,B`). The `automata-lib` expects the symbols to be pushed in reverse order of how they appear in the string, so if you want to push 'A' then 'B', you would write 'B,A'.

**Example Transition:**
`q0,a,Z0 -> q0,A,Z0`
`q0,a,A -> q0,A,A`
`q0,b,A -> q1,lambda`
`q1,b,A -> q1,lambda`
`q1,c,Z0 -> q2,Z0`

## Setup

To run this project on your machine, follow these steps:

1.  **Clone the repository (if applicable):**
    ```bash
    git clone https://github.com/DevimanAI/NPDA.git
    cd NPDA
    ```

2.  **Install Python Dependencies:**
    This project requires `automata-lib`. You can install it using pip:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Install Graphviz:**
    Graphviz is required to render the DOT files into PNG images.
    -   **ویندوز (Windows):** Graphviz را از [وب‌سایت Graphviz](https://graphviz.org/download/windows/) دانلود و نصب کنید. اطمینان حاصل کنید که در طول نصب، Graphviz را به PATH سیستم خود اضافه کرده‌اید یا این کار را به صورت دستی انجام دهید.
    -   **macOS:**
        ```bash
        brew install graphviz
        ```
    -   **Linux (Debian/Ubuntu):**
        ```bash
        sudo apt-get install graphviz
        ```

## Usage

1.  Create an NPDA definition file (e.g., `npda_definition.txt`) following the format above.
2.  Run the `npda_visualizer.py` script, providing the path to your definition file and the input string. This will generate two PNG images: `npda_execution.png` (for the execution trace) and `npda_definition_diagram.png` (for the NPDA's structure).

Example:
```bash
python npda_visualizer.py npda_definition.txt aabb
```

This command will:
-   Load the NPDA definition from `npda_definition.txt`.
-   Simulate the NPDA's execution with the input string `aabb`.
-   Generate `npda_execution.dot` and `npda_execution.png` showing the execution trace.
-   Generate `npda_definition_diagram.dot` and `npda_definition_diagram.png` showing the NPDA's definition.