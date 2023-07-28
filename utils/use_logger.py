from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table
from rich.traceback import install


class WrapperRichLogger:
    def __init__(self):
        self.logger = Console(color_system="windows")
        install(show_locals=True)

    def error(self, msg: str):
        self.logger.log(f"[bold red]{msg}[/bold red]")

    def log(self, msg: str):
        self.logger.log(msg)

    def print(self, msg: str):
        self.logger.print(msg)

    def table(self, column: list, data: list, title: str = ""):
        """
        :param title:
        :param column: 标题
        :param data: 数据
        :return:
        """
        t = Table(title=title, box=box.DOUBLE_EDGE)
        for i in column:
            t.add_column(i)

        # table.add_row("May 25, 2018", "Solo: A Star Wars Story", "$393,151,347")
        for i in data:
            t.add_row(*i)
        self.logger.print(t)

    def bullet(self, title: str = "", msg_list: list = None):
        """
        :param title:
        :param msg_list: 列表
        :return:
        """
        if not msg_list:
            msg_list = []

        msg = f"# {title}\n"
        for i in range(len(msg_list)):
            msg += f"{i + 1}. {msg_list[i]}\n"
        self.logger.print(Markdown(msg))

    def h1(self, msg: str = ""):
        self.logger.print(Markdown(f"# {msg}"))

    def exception(self, msg: str = ""):
        self.logger.print_exception(show_locals=True)
        self.error(msg)


if __name__ == '__main__':
    logger = WrapperRichLogger()
    logger.h1("123")
    logger.log("123")
    logger.print("123")
