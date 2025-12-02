from dotenv import load_dotenv

from ui.layout import render_layout
from ui.chat import render_chat

load_dotenv()


def main():
    render_layout()
    render_chat()


if __name__ == "__main__":
    main()
