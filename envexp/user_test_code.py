"""User-defined test code to run after the imports have been tested."""

if __name__ == "__main__":
    import tensorflow as tf

    physical_devices = tf.config.list_physical_devices("GPU")
    assert len(physical_devices) > 0, "No GPU devices found."

    from sleap.gui.app import main as sleap_label

    ds = "/Users/liezlmaree/Projects/sleap-datasets/drosophila-melanogaster-courtship/courtship_labels.slp"
    # ds = "/Users/liezlmaree/Projects/sleap/tests/data/hdf5_format_v1/centered_pair_predictions.slp"
    sleap_label([ds])
