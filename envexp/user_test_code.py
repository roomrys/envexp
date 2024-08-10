"""User-defined test code to run after the imports have been tested."""

if __name__ == "__main__":
    assert False, "Replace this block with your own test code."

    # Example test code that is not run since after return
    from qtpy.QtWidgets import QApplication, QMainWindow

    def create_app():
        """Creates Qt application."""
        app = QApplication([])
        return app

    app = create_app()

    window = QMainWindow()
    window.showMaximized()

    app.exec_()
