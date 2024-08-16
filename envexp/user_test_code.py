"""User-defined test code to run after the imports have been tested."""

if __name__ == "__main__":
    
    import os

    from sleap import load_file

    ds = os.environ["ds-dmc"]
    load_file(ds)