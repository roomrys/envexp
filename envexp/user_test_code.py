"""User-defined test code to run after the imports have been tested."""

if __name__ == "__main__":
    import tensorflow as tf

    physical_devices = tf.config.list_physical_devices("GPU")
    assert len(physical_devices) > 0, "No GPU devices found."

    from sleap.gui.app import main as sleap_label

    ds = "/Users/liezlmaree/Projects/sleap-datasets/drosophila-melanogaster-courtship/courtship_labels.slp"
    # ds = "/Users/liezlmaree/Projects/sleap/tests/data/hdf5_format_v1/centered_pair_predictions.slp"
    # sleap_label([ds])

    from pathlib import Path

    from sleap import load_file
    from sleap.nn.training import main as sleap_train

    # Get the relative video path
    labels = load_file(ds)
    video_path: str = labels.videos[0].filename
    search_paths = [str(Path("/Users/liezlmaree/Projects/sleap/") / video_path)]

    # Reload the labels with the search paths to find the video
    labels = load_file(ds, search_paths=search_paths)
    labels.save("./test_labels.slp")

    sleap_train(["/Users/liezlmaree/Projects/sleap-datasets/drosophila-melanogaster-courtship/models/231016_063130.centroid.n=149","./test_labels.slp"])
