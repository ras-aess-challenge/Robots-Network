# Robots-Network

## Living Map — Robot-Side Simulation

This repository contains the **robot-side simulation** developed for the **Living Map** challenge.

The purpose of this component is to simulate the behavior of the robots that create, carry, transmit, and consume spatial information during a disaster-response mission.

The robot-side implementation is separated from the communication infrastructure implemented in the dedicated **Network** component.

The main robot workflow is:

```text
Writer Robot
     |
     v
Weak Node / Spatial Beacon
     |
     v
Network Component
     |
     v
Command Post
     |
     v
Executor Robot
```

The `Robots-Network` repository therefore focuses on:

* Writer robot behavior
* Weak Node representation
* Executor robot behavior
* Robot clients
* Beacon generation
* Spatial information
* Robot movement
* Probability of Detection
* Network-condition simulation used by the robots
* Robot failure and catastrophic attrition scenarios
* Communication with the separate Network component

---

# 1. Living Map Context

The Living Map is designed for disaster environments where robots may operate in areas with limited or unavailable communication.

Examples include:

* Collapsed buildings
* Mines
* Fire-damaged areas
* Hazardous zones
* Contaminated areas
* Underground environments
* Areas without reliable GPS
* Areas outside normal communication coverage

A robot entering such an environment may discover important information such as:

* A victim
* A hazard
* Debris
* A target
* An important location

Instead of keeping this information only inside the robot, the system converts it into **spatial memory** represented by Weak Nodes.

This information can then be transmitted through the network and later used by another robot.

The main concept is:

```text
Robot discovers information
          |
          v
Spatial information is created
          |
          v
Information is transmitted
          |
          v
Command Post stores the information
          |
          v
Another robot retrieves it
          |
          v
Mission continues
```

This means that the robot that originally discovered the information does not have to remain available for the information to remain useful.

---

# 2. Scope of This Repository

This repository represents the **robot side** of the Living Map system.

It does not replace the dedicated Network component.

The responsibilities are divided as follows.

## Robots-Network

```text
Writer Robot
Weak Node
Executor Robot
Robot movement
Event generation
Beacon generation
Robot-side simulation
Robot clients
Catastrophic attrition
Robot-side network behavior
```

## Network

The separate Network component is responsible for:

```text
TCP communication
Strong Node
ONA
Command Post
Beacon relay
Beacon storage
Authentication
Protocol implementation
Health checks
Docker deployment
Network infrastructure
```

The two components therefore work together but have different responsibilities.

---

# 3. Overall Architecture

The complete system can be represented as:

```text
                    ROBOTS-NETWORK
                  Robot-side system
                         |
                         |
                  +------+------+
                  |             |
                  v             |
            +-----------+       |
            |   Writer  |       |
            |   Robot   |       |
            +-----+-----+       |
                  |             |
                  v             |
            +-----------+       |
            | Weak Node |       |
            +-----+-----+       |
                  |             |
                  | Beacon      |
                  v             |
================================================
                    NETWORK
             Communication System
================================================
                  |
                  v
            +-----------+
            |   Strong  |
            |   Node     |
            +-----+-----+
                  |
                  v
            +-----------+
            |    ONA    |
            +-----+-----+
                  |
                  v
            +-----------+
            |  Command  |
            |   Post    |
            +-----+-----+
                  |
                  | Mission
                  v
================================================
                  ROBOTS-NETWORK
================================================
                  |
                  v
            +-----------+
            | Executor  |
            |   Robot   |
            +-----------+
```

The important communication principle is:

```text
Writer != Executor
```

The Writer generates the information.

The Executor consumes the information later.

The Network component provides the communication path between them.

---

# 4. Robot Roles

## 4.1 Writer Robot

The Writer is the robot responsible for exploring the environment and generating spatial information.

Its responsibilities include:

* Moving through the environment
* Detecting events
* Creating Weak Nodes
* Recording coordinates
* Recording event information
* Assigning a Probability of Detection
* Sending beacon information toward the network
* Handling robot-side failure conditions

The Writer is the source of spatial information.

Example:

```text
Writer detects:

VICTIM

Position:
X = 10.5
Y = 0.0

PoD:
0.90
```

The Writer creates a Weak Node containing this information.

---

# 5. Writer Implementation

## `writer.py`

`writer.py` contains the Writer robot logic.

It represents the internal behavior of the robot rather than the communication infrastructure.

The Writer is responsible for maintaining robot state and generating spatial information.

The Writer can:

```text
Move
Detect event
Stop
Create Weak Node
Store generated information
Continue or terminate operation
```

The Writer simulation also contains mission conditions that can trigger a stop.

For example:

```text
Spatial limit reached
```

can cause the Writer to stop moving before creating or transmitting the relevant beacon.

---

# 6. Writer Client

## `writer_client.py`

`writer_client.py` represents the communication-side execution of the Writer.

It connects the Writer simulation with the network communication layer.

The general workflow is:

```text
Writer simulation
       |
       v
Event detected
       |
       v
Weak Node created
       |
       v
Beacon prepared
       |
       v
Writer client
       |
       v
Network component
```

The Writer client is therefore the bridge between the robot simulation and the communication infrastructure.

---

# 7. Weak Node

## `weak_node.py`

A Weak Node represents a spatial information point created by the Writer.

It is the software representation of the spatial memory left by the robot.

A Weak Node contains information such as:

```text
Node ID
Position X
Position Y
Timestamp
Event
Probability of Detection
```

Example:

```text
WN001

Position:
(10.5, 0.0)

Event:
VICTIM

PoD:
0.90
```

The Weak Node is important because the information becomes independent from the Writer after it has been generated and transmitted.

---

# 8. Spatial Memory

The main purpose of the Weak Node is to create spatial memory.

The Writer discovers something:

```text
VICTIM
```

at:

```text
(10.5, 0.0)
```

The information is transformed into:

```text
WN001
```

and can then be transported through the network.

The concept is:

```text
Physical observation
        |
        v
Spatial memory
        |
        v
Network transmission
        |
        v
Mission information
```

This is the central robot-side contribution to the Living Map.

---

# 9. Probability of Detection

Each Weak Node can contain a Probability of Detection value.

For example:

```text
PoD = 0.90
```

represents a high confidence that the detected event is correct.

The simulation can model degradation of this information over time.

Conceptually:

```text
Initial detection
      |
      v
PoD = 0.90
      |
      | Time passes
      v
PoD decreases
```

For example:

```text
Initial:
0.900

Later:
0.888
```

This represents the idea that information can become less reliable as time passes.

---

# 10. Event Information

The Writer can generate different types of spatial events.

Examples include:

```text
VICTIM
HAZARD
DEBRIS
TARGET
```

The event is associated with the Weak Node.

For example:

```text
WN001
Event = VICTIM
Position = (10.5, 0.0)
PoD = 0.90
```

The event itself is encoded according to the protocol used by the Network component.

The robot-side implementation therefore generates the information while the Network component handles the communication protocol.

---

# 11. Beacon Generation

The Writer converts detected events into beacon information.

The process is:

```text
Event detected
      |
      v
Position determined
      |
      v
PoD assigned
      |
      v
Timestamp recorded
      |
      v
Weak Node created
      |
      v
Beacon generated
      |
      v
Network transmission
```

Example:

```text
Writer detects VICTIM

       ↓

WN001

X = 10.5
Y = 0.0
Event = VICTIM
PoD = 0.90
Timestamp = T
```

---

# 12. Beacon Protocol Boundary

The actual beacon protocol is handled by the separate Network component.

The robot-side system generates the information that must be transmitted.

The Network component is responsible for the communication protocol.

Therefore:

```text
Robots-Network
      |
      | Beacon information
      v
Network
      |
      | Encoded / authenticated / transmitted
      v
Command Post
```

This separation keeps the robot behavior independent from the underlying communication infrastructure.

---

# 13. Executor Robot

## `executor.py`

The Executor is the robot that acts on information collected by the Living Map.

The Executor does not need to be the same robot that originally discovered the information.

Its main responsibilities are:

* Receive a mission
* Read stored beacon information
* Identify relevant events
* Extract coordinates
* Navigate toward the required location
* Process the spatial information

The basic workflow is:

```text
Command Post
      |
      | Mission
      v
Executor
      |
      v
Read beacon
      |
      v
Identify event
      |
      v
Read coordinates
      |
      v
Navigate
```

---

# 14. Executor Client

## `executor_client.py`

`executor_client.py` provides the communication-side interface for the Executor.

The Executor can request mission information from the Command Post through the Network component.

Conceptually:

```text
Executor
    |
    | Request mission
    v
Network / Command Post
    |
    | Stored beacon information
    v
Executor
```

The Executor then uses the returned information to determine what it should do.

---

# 15. Example Executor Mission

Suppose the Writer generated:

```text
WN001
Position = (10.5, 0.0)
Event = VICTIM
PoD = 0.90
```

The Command Post stores the information.

The Executor requests the mission.

The Executor receives:

```text
WN001
VICTIM
(10.5, 0.0)
PoD = 0.888
```

The Executor can then move toward:

```text
(10.5, 0.0)
```

The important point is that the Executor did not need to receive the information directly from the Writer.

---

# 16. Executor Navigation

The Executor uses the beacon coordinates as navigation targets.

For example:

```text
Executor position:

(0, 0)

Target:

(10.5, 0.0)
```

The Executor moves toward the target.

The simulation can therefore demonstrate:

```text
Mission information
       |
       v
Target coordinates
       |
       v
Robot movement
       |
       v
Target reached
```

This connects the networking system with the robot behavior.

---

# 17. Multiple Weak Nodes

The Writer can generate multiple spatial observations.

Example:

```text
WN001
(10.5, 0.0)
VICTIM

WN002
(21.0, 0.0)
HAZARD

WN003
(31.5, 0.0)
DEBRIS
```

These observations can be transmitted through the Network component.

The Command Post can then provide them to the Executor as mission information.

The Executor can process the beacons sequentially.

---

# 18. Robot-Side Network Physics

## `network_physics.py`

The robot simulation includes network-physics behavior to avoid assuming perfect communication.

The current simulation models communication quality according to distance.

The current parameters include:

```text
Maximum range:
2000 m

Degradation begins:
1400 m

Maximum simulated packet loss:
approximately 90%
```

The purpose is to simulate communication degradation.

The model is not intended to be a complete physical radio-propagation model.

It provides a software approximation that can be used to test robot behavior under unreliable communication.

---

# 19. Communication Degradation

The simulated behavior can be represented as:

```text
Distance increases
       |
       v
Signal quality decreases
       |
       v
Packet loss increases
       |
       v
Communication becomes unreliable
```

This is important for the Living Map scenario because robots may operate far from the communication infrastructure.

The robot-side simulation can therefore be tested under different communication conditions.

---

# 20. Robot Failure and Catastrophic Attrition

One of the important scenarios implemented in the Writer simulation is catastrophic attrition.

A Writer can fail after generating spatial information.

The purpose is to demonstrate that the information generated by the Writer does not necessarily disappear when the robot becomes unavailable.

Example:

```text
Writer
  |
  | Detects victim
  v
WN001 created
  |
  | Beacon transmitted
  v
Network
  |
  v
Command Post
```

Then:

```text
Writer
  X
FAILED
```

The previously transmitted information can still exist at the Command Post.

The Executor can therefore retrieve:

```text
WN001
VICTIM
(10.5, 0.0)
```

even though the original Writer is no longer operating.

---

# 21. Catastrophic Attrition Principle

The important principle is:

```text
Robot failure != Information failure
```

The Living Map is therefore not simply a robot-to-robot communication system.

It is a system for preserving spatial information across the mission.

The Writer creates the information.

The Network transports it.

The Command Post stores it.

The Executor consumes it.

---

# 22. Frame Translation

## `frame_translation.py`

`frame_translation.py` provides coordinate-frame translation functionality used by the robot-side system.

Different parts of the system may use different coordinate references.

The general concept is:

```text
Robot coordinate frame
          |
          v
Frame translation
          |
          v
Mission / shared coordinate frame
```

This allows spatial information created by one robot to be interpreted by another part of the system.

---

# 23. Communication Clients

The repository contains two main robot-side clients.

## Writer Client

```text
writer_client.py
```

Used to send Writer-generated information toward the Network component.

## Executor Client

```text
executor_client.py
```

Used to retrieve mission information from the Network / Command Post side.

The two directions are therefore:

```text
Writer
  |
  | SEND BEACON
  v
Network
```

and:

```text
Network / Command Post
  |
  | MISSION
  v
Executor
```

---

# 24. Repository File Structure

```text
Robots-Network/
│
├── tests/
│
├── .dockerignore
├── .gitignore
├── README.md
│
├── beacon_codec.py
├── executor.py
├── executor_client.py
├── frame_translation.py
├── mission_service.py
├── network_client.py
├── network_physics.py
├── security_config.py
├── strong_node_server.py
├── weak_node.py
├── writer.py
└── writer_client.py
```

---

# 25. File Responsibilities

| File                    | Responsibility                                             |
| ----------------------- | ---------------------------------------------------------- |
| `writer.py`             | Writer robot behavior                                      |
| `writer_client.py`      | Writer-side communication                                  |
| `weak_node.py`          | Weak Node / spatial memory representation                  |
| `executor.py`           | Executor robot behavior                                    |
| `executor_client.py`    | Executor-side communication                                |
| `network_physics.py`    | Simulated communication degradation                        |
| `network_client.py`     | Robot-side network communication                           |
| `mission_service.py`    | Mission information handling                               |
| `frame_translation.py`  | Coordinate-frame translation                               |
| `beacon_codec.py`       | Beacon data encoding/decoding used by the robot side       |
| `security_config.py`    | Security configuration used by the communication interface |
| `strong_node_server.py` | Interface/support for the Strong Node communication side   |
| `tests/`                | Automated testing                                          |
| `.gitignore`            | Git ignored files                                          |
| `.dockerignore`         | Docker build exclusions                                    |
| `README.md`             | Documentation                                              |

---

# 26. Relationship With the Network Repository

The `Robots-Network` component should not be confused with the separate `Network` component.

The two components have complementary responsibilities.

## Robots-Network

```text
Robot simulation
      |
      +-- Writer
      |
      +-- Weak Node
      |
      +-- Executor
      |
      +-- Robot movement
      |
      +-- Event generation
      |
      +-- Spatial information
      |
      +-- Robot failure simulation
```

## Network

```text
Communication infrastructure
      |
      +-- Strong Node
      |
      +-- ONA
      |
      +-- Command Post
      |
      +-- TCP relay
      |
      +-- Beacon storage
      |
      +-- Authentication
      |
      +-- Health checks
      |
      +-- Docker deployment
```

The robot repository produces and consumes information.

The Network repository transports and manages that information.

---

# 27. Complete System Data Flow

The complete Living Map data flow is:

```text
                    WRITER ROBOT
                         |
                         |
                  Detects an event
                         |
                         v
                   WEAK NODE
                         |
                         |
                  Beacon information
                         |
                         v
================================================
                    NETWORK
================================================
                         |
                         v
                   STRONG NODE
                         |
                         v
                       ONA
                         |
                         v
                   COMMAND POST
                         |
                         |
                   Stored beacon
                         |
                         v
================================================
                  ROBOTS-NETWORK
================================================
                         |
                         v
                   EXECUTOR
                         |
                         |
                   Reads mission
                         |
                         v
                  Target location
                         |
                         v
                   Robot movement
```

---

# 28. Example End-to-End Scenario

## Step 1 — Writer moves

The Writer starts at:

```text
(0, 0)
```

and moves through the environment.

---

## Step 2 — Event detected

The Writer detects a victim at:

```text
(10.5, 0.0)
```

---

## Step 3 — Weak Node created

The Writer creates:

```text
WN001

Event:
VICTIM

Position:
(10.5, 0.0)

PoD:
0.90
```

---

## Step 4 — Beacon transmitted

The Writer client sends the information to the Network component.

```text
Writer
   |
   v
Writer Client
   |
   v
Network
```

---

## Step 5 — Network transports information

The Network component handles the communication infrastructure.

```text
Strong Node
    |
    v
ONA
    |
    v
Command Post
```

---

## Step 6 — Command Post stores information

The Command Post stores:

```text
WN001
VICTIM
(10.5, 0.0)
```

---

## Step 7 — Writer fails

The Writer becomes unavailable.

```text
WRITER
   X
FAILED
```

The information has already reached the Command Post.

---

## Step 8 — Executor requests mission

The Executor requests mission information.

```text
Executor
    |
    v
Command Post
```

---

## Step 9 — Executor receives WN001

The Executor receives:

```text
WN001
VICTIM
(10.5, 0.0)
```

---

## Step 10 — Executor navigates

The Executor moves toward:

```text
(10.5, 0.0)
```

The mission can therefore continue even though the original Writer failed.

---

# 29. Running the Robot Simulation

The exact execution depends on the Network component running at the same time.

The general order is:

```text
1. Start Network infrastructure
2. Start Strong Node / communication services
3. Start Writer
4. Generate beacon information
5. Allow Network to relay information
6. Start Executor
7. Executor retrieves mission
8. Executor processes beacon
```

---

# 30. Running the Writer

From the `Robots-Network` directory:

```bash
python writer_client.py
```

The Writer simulation should generate output describing robot activity.

Example:

```text
[WRITER_1] RTA trigger: spatial limit reached
[WRITER_1] Halted (v=0.0 m/s)
[WRITER_1] Dropped WN001 at (10.5, 0.0)
[WRITER] Sending WN001
```

The exact output depends on the current simulation state.

---

# 31. Running the Executor

Run:

```bash
python executor_client.py
```

The Executor client requests mission information from the communication infrastructure.

The returned information can contain beacons such as:

```text
WN001
Event: VICTIM
Position: (10.5, 0.0)
PoD: 0.888
```

The Executor then uses the information as part of its navigation logic.

---

# 32. Running Tests

The repository contains a `tests/` directory.

If the project uses `pytest`, tests can be executed with:

```bash
python -m pytest
```

If `pytest` is not installed:

```bash
pip install pytest
```

Then:

```bash
python -m pytest
```

Tests are intended to verify the behavior of the robot-side components without requiring the complete physical robot system.

---

# 33. Simulation vs Physical System

The current implementation is a software simulation.

The following are simulated:

```text
Robot movement
Robot positions
Events
Weak Nodes
Communication conditions
Packet loss
Probability of Detection
Robot failure
Mission retrieval
```

No physical robot hardware is required for the current implementation.

The purpose is to validate the architecture and software behavior before physical deployment.

---

# 34. Future Hardware Integration

The robot-side software can later be connected to physical robot hardware.

The current software architecture can evolve from:

```text
Python Writer
      |
      v
Python Network
      |
      v
Python Executor
```

toward:

```text
Physical Writer Robot
      |
      | Radio
      v
Physical Network Node
      |
      | Gateway
      v
Command Post
      |
      | Radio
      v
Physical Executor Robot
```

The robot logic can therefore be developed independently from the final hardware.

---

# 35. Current Limitations

The current implementation is a simulation and has several limitations.

## Environment

The disaster environment is represented in software.

## Radio

Communication is simulated rather than produced by real radio hardware.

## Movement

Robot movement is simulated rather than controlled by real motors.

## Coordinates

Coordinates are simulation coordinates and are not necessarily geographic GPS coordinates.

## Propagation

The network-physics model is simplified and does not represent every real-world radio effect.

---

# 36. Design Principles

The robot-side implementation follows these principles.

### 1. Information must survive robot failure

A Writer should not be the only location where important information exists.

### 2. Robots should be decoupled

The Executor should not depend directly on the Writer.

### 3. Spatial information should be explicit

Events should contain a location.

### 4. Information confidence should be represented

PoD provides a confidence value.

### 5. Communication should not be assumed perfect

The simulation includes communication degradation.

### 6. Robot logic should remain independent from infrastructure

The Writer and Executor should not need to implement the complete communication infrastructure themselves.

---

# 37. Core Concept

The most important concept implemented by this repository can be summarized as:

```text
        DISCOVER
           |
           v
        REMEMBER
           |
           v
        TRANSMIT
           |
           v
         STORE
           |
           v
         RETRIEVE
           |
           v
          ACT
```

In the Living Map:

```text
Writer
  ↓
Weak Node
  ↓
Network
  ↓
Command Post
  ↓
Executor
```

The robot that discovers an event creates the spatial memory.

The communication infrastructure transports the memory.

The Command Post preserves the information.

The Executor later uses that information to continue the mission.

---

# 38. Final Objective

The objective of `Robots-Network` is to provide the robot-side implementation needed to demonstrate the Living Map concept.

The repository demonstrates:

* Writer robot simulation
* Weak Node generation
* Spatial memory
* Event detection
* Position tracking
* Probability of Detection
* Beacon generation
* Robot-side communication
* Network-condition simulation
* Executor mission retrieval
* Executor navigation
* Catastrophic Writer attrition
* Information persistence after robot failure

The overall concept is:

```text
A robot may fail.

The information it discovered should not have to fail with it.
```

This is the core principle of the Living Map robot-network architecture.
