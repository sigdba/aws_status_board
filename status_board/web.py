import os

import jinja2

import ecs


def status_board_title():
    if "SB_PAGE_TITLE" in os.environ:
        return os.environ["SB_PAGE_TITLE"]
    return "Status Board"


def status_board():
    env = jinja2.Environment(
        loader=jinja2.PackageLoader("web"),
        autoescape=jinja2.select_autoescape(),
    )
    template = env.get_template("index.html")
    return template.render(
        ecs_clusters=ecs.clusters_with_health(), page_title=status_board_title()
    )


if __name__ == "__main__":
    print(status_board())
