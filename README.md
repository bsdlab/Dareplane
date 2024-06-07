<!-- ![](./assets/single_dareplane_logo.svg) -->
<picture>
    <source srcset="./assets/single_dareplane_logo_white.svg"  media="(prefers-color-scheme: dark)">
    <img src="./assets/single_dareplane_logo.svg">
</picture>

**Caveat:** This project is in an early alpha stage and was so far mainly developed by a single developer. Although core functionality is implemented and the platform has been used in 15 experimental sessions including simultaneous recording of EEG, ECoG, LFP and other signal modalities, please be aware that there will be bugs and features are still limited. Also documentation is very rudimentary, but will improve over the coming months.

We still think that the platform can already serve as a development framework which allows to make used of existing modules and extend this open-source project based on your bespoke needs. This with minimal overhead, keeping your project lightweight and allowing to develop single responsibility modules that can be composed to complex systems.

The target users are developers of experimental setups who require customized software components, or who just want to have full control over the functionality of data I/O, algorithmic processing, and/or on stimulation and feedback. For this user group, Dareplane aims to provide a minimalistic framework which allows to develop and integrate bespoke modules in a simple way. It is a mind-child of the [https://suckless.org/](https://suckless.org/) philosophy and tries to adapt it in a pragmatic manner with research in the focus.

If you are looking for a setup that is more or less ready to use out of the box, you will be better of using a more mature framework which is oriented towards more _plug-and-play_ components. In any case it is good to have a look at the [other frameworks](#other-frameworks) section.

## The design philosophy of Dareplane

The basic idea of the Dareplane platform is to provide a modular approach for software components used for research of neuro-technology. The design goals are:

- to provide reusable single purpose modules which can be integrated into a larger system;
- to be technology agnostic, so that modules can be used with different hardware and developed in different languages;
- to be minimalistic in terms of constraints and required overhead for integrating existing software into the platform.

The implications of these design goals are:

- A common channel of communication between modules is required, which should work with a wide range of hardware and software. For Dareplane this is solved by using TCP sockets for communication. For data transfer, the awesome [LSL](https://labstreaminglayer.org/) framework is used.
- A common protocol for communication is required, which Dareplane implements as string communication using what we call _primary commands_. This is an arbitray string following by a pipe delimiter and potentially a `json` payload. This is a kind of abstraction of functionality. Imagine a module for recording EEG data from a single data source. On a high level, a command you would want to use is: `STARTRECORDING|{"path":"./mydatafolder/", "file": "myrecoding.xdf"}`.

## Overview of the Dareplane project and individual modules

This is a very first release and many more of the modules we already have in use will be published in the coming weeks.

| Link                                                               | Description                                                                                             |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------- |
| [dp-strawmam-module](https://github.com/bsdlab/dp-strawman-module) | a strawman repository as starting point for developing your modules                                     |
| [dp-control-room](https://github.com/bsdlab/dp-control-room)       | the central module which combines individual modules to a system                                        |
| [dp-lsl-recording](https://github.com/bsdlab/dp-lsl-recording)     | module for interacting with the [LSL LabRecorder](https://github.com/labstreaminglayer/App-LabRecorder) |
| [dp-mockup-streamer](https://github.com/bsdlab/dp-mockup-streamer) | module for creating mock-up streams from files or generating random data                                |
|                                                                    |                                                                                                         |
|                                                                    |                                                                                                         |

### Individual modules

You can find individual modules included in the `./modules` folder, where they are linked as submodules.

### For python modules / development

If you are building your modules in python, or using the existing python modules, you will need the `dareplane-utils` python module.
```
pip install dareplane-utils
```
The module provides basic functionality around TCP servers, logging, and collect data from LSL streams.

#### Control Room module

The [`control room`](https://github.com/bsdlab/dp-control-room) module is the central piece for composition of modules to a larger system.
Modules you need in your experiment are added within a setup configuration file (see `./examples` and the documentation in the [`control room`](https://github.com/bsdlab/dp-control-room))

## Get started

Refer to the `./examples` documents to so see a minimalistic setup and guidance on how to develop
your own modules.

## Other frameworks

This is a non-exhaustive list of other frameworks which might be more suitable depending on your needs:

- [BCI2000](https://www.bci2000.org/)
- [Medusabci](https://www.medusabci.com/)
- [timeflux](https://timeflux.io/)
