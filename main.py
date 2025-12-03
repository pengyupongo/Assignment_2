"""Entry point for launching the MiniPac game loop."""

from minopac.game import Game


def main() -> None:
    """Boot the ``Game`` object and start the main pygame loop.

    Returns:
        None: The function blocks until the pygame window closes.
    """
    Game().run()


if __name__ == "__main__":
    main()
