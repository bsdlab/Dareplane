<!-- ![](./assets/single_dareplane_logo.svg) -->
<picture>
    <source srcset="./assets/single_dareplane_logo_white.svg"  media="(prefers-color-scheme: dark)">
    <img src="./assets/single_dareplane_logo.svg">
</picture>

Dareplane is a modular and broad technology agnostic open source software platform for brain-computer interface research. [LSL](https://labstreaminglayer.org) is used for data communication and `TCP` sockets for module communication. The platform is designed to be minimalistic and to allow for easy development of custom modules, with minimal overhead of integrating existing code.

**Caveat:** The platform is in an early alpha stage and is developed by a small group of developers. Although core functionality is implemented and the platform has been used in >20 experimental sessions including simultaneous recording of EEG, ECoG, LFP and other signal modalities, please be aware that bugs are still likely and thorough testing of every setup is required.

The target users are developers of experimental setups who require customized software components, or who just want to have full control over the functionality of data I/O, algorithmic processing, and/or on stimulation and feedback. For this user group, Dareplane aims to provide a minimalistic framework which allows to develop and integrate bespoke modules in a simple way. It is a mind-child of the [https://suckless.org/](https://suckless.org/) philosophy and tries to adapt it in a pragmatic manner with research in the focus.

If you are looking for a setup that is more or less ready to use out of the box, you will be better of using a more mature framework which is oriented towards more _plug-and-play_ components. In any case it is good to have a look at the [other frameworks](#other-frameworks) section.

## The design philosophy of Dareplane

The basic idea of the Dareplane platform is to provide a modular approach for software components used for research of neuro-technology. The design goals are:

- to provide reusable single purpose modules which can be integrated into a larger system;
- to be technology agnostic, so that modules can be used with different hardware and developed in different languages;
- to be minimalistic in terms of constraints and required overhead for integrating existing software into the platform.

The implications of these design goals are:

- A common channel of communication between modules is required, which should work with a wide range of hardware and software. For Dareplane this is solved by using TCP sockets for module communication. For data transfer, the awesome [LSL](https://labstreaminglayer.org/) framework is used.
- A common protocol for communication is required, which Dareplane implements as string communication using what is referred to as _primary commands_. This is an arbitray string following by a pipe delimiter and potentially a `json` payload. Imagine a module for recording EEG data from a single data source. On a high level, a command you would want to use is: `STARTRECORDING|{"path":"./mydatafolder/", "file": "myrecoding.xdf"}`.

## Overview of the Dareplane projects and individual modules

| Link                                                                         | Description                                                                                                        |
| ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| [dp-strawmam-module](https://github.com/bsdlab/dp-strawman-module)           | a strawman repository as starting point for developing your modules                                                |
| [dp-control-room](https://github.com/bsdlab/dp-control-room)                 | the central module which combines individual modules to a system                                                   |
| [dp-lsl-recording](https://github.com/bsdlab/dp-lsl-recording)               | module for interacting with the [LSL LabRecorder](https://github.com/labstreaminglayer/App-LabRecorder)            |
| [dp-mockup-streamer](https://github.com/bsdlab/dp-mockup-streamer)           | module for creating mock-up streams from files or generating random data                                           |
| [dp-copydraw](https://github.com/bsdlab/dp-copydraw)                         | module to run the [CopyDraw - Castano et al. 2019](https://ieeexplore.ieee.org/abstract/document/8839739) paradigm |
| [dp-multiband-regression](https://github.com/bsdlab/dp-multiband-regression) | module to perform a multiband regression based on a multichannel data stream                                       |
| [dp-bollinger-control](https://github.com/bsdlab/dp-bollinger-control)       | a [Bollinger Band](https://en.wikipedia.org/wiki/Bollinger_Bands) control module                                   |
| [dp-ao-communicatio](https://github.com/bsdlab/dp-ao-communication)          | a C++ module interacting with the [Alpha Omega](https://www.alphaomega-eng.com/Neuro-Omega-System)'s API           |
| [dp-ao-stimulator](https://github.com/bsdlab/dp-ao-stimulator)               | python module to trigger stimulation via dp-ao-communication                                                       |
| [dp-arduino-stimulator](https://github.com/bsdlab/dp-arduino-stimulator)     | module to use an Arduino as a mock-up of a neuro-stimulator                                                        |
| [dp-picoscope-streamer](https://github.com/bsdlab/dp-picoscope-streamer)     | module to stream data from a Picoscope to [LSL](https://labstreaminglayer.org)                                     |
| [dp-passthrough](https://github.com/bsdlab/dp-passthrough)                   | a simple passthrough Dareplane module for performance testing                                                      |
| [dp-threshold-controller](https://github.com/bsdlab/dp-threshold-controller) | a threshold control module with grace periods                                                                      |
| [dp-cortec-bic](https://github.com/bsdlab/dp-cortec-bic)                     | _soon to be released_                                                                                              |

### For python modules / development

If you are building your modules in python, or using the existing python modules, the [`dareplane-utils`](https://pypi.org/project/dareplane-utils/) python module will provide some core functionality which most modules will need.

```
pip install dareplane-utils
```

The module provides basic functionality around TCP servers, logging, and collecting data from LSL streams.

#### Control Room module

The [`control room`](https://github.com/bsdlab/dp-control-room) module is the central piece for composition of modules to a full setup.
Modules you need in your experiment are added within a setup configuration file (see `./examples` and the documentation in the [`control room`](https://github.com/bsdlab/dp-control-room))

## Getting started

Refer to the `./examples` documents to so see a minimalistic setup and guidance on how to develop
your own modules.

## Other frameworks

This is a non-exhaustive list of other frameworks which might be more suitable depending on your needs:

- [BCI2000](https://www.bci2000.org/)
- [Medusabci](https://www.medusabci.com/)
- [timeflux](https://timeflux.io/)
