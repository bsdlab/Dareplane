# dp-mi-paradigm

A simple motor imagery paradigm module for Dareplane.

## Overview

This module implements a basic motor imagery task that:

- Displays visual cues (letters "L" and "R") using [PsychoPy](https://www.psychopy.org/).
- Sends markers through the [LabStreamingLayer (LSL)](https://labstreaminglayer.org/) framework.
- Can be controlled via a TCP server integrated with the Dareplane platform.

## Setup

### Environment

Create the environment using the provided YAML file:

```bash
conda env create -f environment.yaml
```

Then activate the environment:

```bash
conda activate dareplane
```

DISCLAIMER: The environment was created in a Linux machine, therefore, running it from Windows may cause issues.

### Running the Paradigm

You can run the paradigm directly by invoking:

```bash
python -m mi_paradigm.main
```

## Further Information

For more details on integrating with the full Dareplane ecosystem, refer to the main [Dareplane README](../../README.md).

You can also take a look at [Hello World](../hello_world/hello_world.md), this setup was created using this description.
