import os

from pynwb.spec import NWBGroupSpec, NWBNamespaceBuilder, export_spec

__version__ = "0.3.0"


def main(output_dir=None):
    ns_builder = NWBNamespaceBuilder(
        doc="type for storing metadata for Tank lab",
        name="ndx-tank-metadata",
        version=__version__,
        author=["Szonja Weigl", "Luiz Tauffer", "Ben Dichter", "Christian Tabedzki"],
        contact=["ben.dichter@gmail.com", "ct5868@princeton.edu"],
    )

    ns_builder.include_type("LabMetaData", namespace="core")
    ns_builder.include_type("DynamicTable", namespace="core")

    LabMetaDataExtension = NWBGroupSpec(
        doc="type for storing metadata for Brody and Tank labs",
        neurodata_type_def="LabMetaDataExtension",
        neurodata_type_inc="LabMetaData",
    )

    attributes = (
        ("experiment_name", "name of experiment run", "text"),
        ("world_file_name", "name of world file run", "text"),
        ("protocol_name", "name of protocol run", "text"),
        ("stimulus_bank_path", "path of stimulus bank file", "text"),
        ("commit_id", "Commit id for session run", "text"),
        ("location", "Name of rig where session was run", "text"),
        ("session_performance", "Performance of correct responses in %", "float", False),
        # isodatetime attributes need hdmf>=6.0 (pynwb>=4.0); older hdmf cannot write them. The
        # "datetime" alias round-trips too but fails pynwb.validate, so use the canonical name.
        ("session_end_time", "Datetime when session ended", "isodatetime"),
        ("num_trials", "Number of trials during the session", "int"),
        (
            "timeElapsedFirstTrial",
            "Lapsed time from starting session to initialization and appearance of world for first trial",
            "float",
            False,
        ),
        (
            "timeElapsedVideoStart",
            "Lapsed time between starting session and beginning of video acquisition; used for Sychronizing face video and Virmen streams",
            "float",
            False,
        ),
    )

    for attribute in attributes:
        name, doc, dtype = attribute[:3]
        required = attribute[3] if len(attribute) > 3 else True
        LabMetaDataExtension.add_attribute(name=name, doc=doc, dtype=dtype, required=required)

    RigExtension = NWBGroupSpec(
        doc="type for storing rig information",
        neurodata_type_def="RigExtension",
        neurodata_type_inc="LabMetaData",
    )

    rig_attr = [
        ("rig", "text", "miniVR or normalVR (projection is changed based on rig type)"),
        ("simulationMode", "int", "true to run in simulation mode with human input via keyboard"),
        ("hasDAQ", "int", "false for testing on laptop"),
        ("hasSyncComm", "int", "true if digital communications should be used for synchronization (ScanImage)"),
        ("minIterationDT", "float", "Minimum expected ViRMEn frame rate in seconds"),
        ("arduinoPort", "text", "Arduino port as seen in the Windows Device Manager"),
        ("sensorDotsPerRev", "float", "Sensor dots per ball revolution, obtained using the calibrateBall script"),
        ("ballCircumference", "float", "in cm"),
        ("toroidXFormP1", "float", "p1 parameter (slope) from poly1 fit of toroidal screen transformation"),
        ("toroidXFormP2", "float", "p2 parameter (offset) from poly1 fit of toroidal screen transformation"),
        ("colorAdjustment", "float", "[R; G; B] scale factor for projector display"),
        ("soundAdjustment", "float", "Scale factor for sound volume"),
        ("nidaqDevice", "int", "NI-DAQ device identifier"),
        ("nidaqPort", "int", "NI-DAQ port number"),
        ("nidaqLines", "int", "NI-DAQ lines for the specified port"),
        ("syncClockChannel", "int", "NI-DAQ digital line for I2C clock signal"),
        ("syncDataChannel", "int", "NI-DAQ digital line for I2C data signal"),
        ("rewardChannel", "int", "NI-DAQ digital line for turning on/off the solenoid valve"),
        ("rewardSize", "float", "in mL"),
        ("rewardDuration", "float", "Valve opening duration (in seconds) for 4uL reward"),
        ("laserChannel", "int", "NI-DAQ digital line for turning on/off the laser"),
        ("rightPuffChannel", "int", "NI-DAQ digital line for right air puff solenoid"),
        ("leftPuffChannel", "int", "NI-DAQ digital line for left air puff solenoid"),
        ("webcam_name", "text", "Webcam name"),
    ]

    for attr, datatype, description in rig_attr:
        if attr in ["sensorDotsPerRev", "colorAdjustment", "nidaqLines"]:
            RigExtension.add_attribute(name=attr, doc=description, dtype=datatype, shape=(None,), required=False)
        else:
            RigExtension.add_attribute(name=attr, doc=description, dtype=datatype, required=False)

    LabMetaDataExtension.add_group(
        name="rig",
        neurodata_type_inc="RigExtension",
        doc="type for storing rig information",
    )

    LabMetaDataExtension.add_group(
        name="mazes",
        neurodata_type_inc="MazeExtension",
        doc="type for storing maze information",
    )

    MazeExtension = NWBGroupSpec(
        doc="type for storing maze information",
        neurodata_type_def="MazeExtension",
        neurodata_type_inc="DynamicTable",
    )
    # MazeExtension has no attributes of its own: each maze field is an optional column (one row per
    # maze), declared in Python in ndx_tank_metadata/maze_extension.py.

    # export the extension to yaml files in the spec folder
    if output_dir is None:
        output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "spec"))
    export_spec(ns_builder, [LabMetaDataExtension, RigExtension, MazeExtension], output_dir)


if __name__ == "__main__":
    main()
